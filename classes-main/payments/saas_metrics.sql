/*
 SaaS business health indicator queries for production tables.
 Tables:
   - auth_user
   - payments_order
   - payments_transaction

 Assumptions:
   - auth_user.date_joined is user signup timestamp.
   - payments_transaction.status='completed' indicates an active paid relationship.
   - Active subscription status is inferred from completed payments in the billing window.
   - Churn is defined as users active in the prior 30-day window who do not complete a payment in the latest 30-day window.
*/

-- 1. Conversion rate: signups to active paid subscribers over time (monthly cohort)
WITH signup_cohort AS (
    SELECT
        u.id AS user_id,
        date(u.date_joined) AS signup_date,
        strftime('%Y-%m', u.date_joined) AS signup_month,
        MIN(t.created_at) AS first_paid_at
    FROM auth_user u
    LEFT JOIN payments_order o
      ON o.user_id = u.id
    LEFT JOIN payments_transaction t
      ON t.order_id = o.id
     AND t.status = 'completed'
    GROUP BY u.id, signup_date, signup_month
)
SELECT
    signup_month,
    COUNT(*) AS signup_count,
    COUNT(CASE WHEN first_paid_at IS NOT NULL
                 AND date(first_paid_at) <= date(signup_date, '+30 days')
              THEN 1 END) AS paid_within_30_days,
    ROUND(
        100.0 * COUNT(CASE WHEN first_paid_at IS NOT NULL
                            AND date(first_paid_at) <= date(signup_date, '+30 days')
                         THEN 1 END)
        / NULLIF(COUNT(*), 0),
        2
    ) AS conversion_rate_pct
FROM signup_cohort
GROUP BY signup_month
ORDER BY signup_month;


-- 2. Current active subscription MRR (absolute value)
-- Estimate absolute MRR as the sum of the latest completed payment amount for every user
-- who has a completed payment within the most recent 30-day window.
WITH latest_completed AS (
    SELECT
        o.user_id,
        t.amount,
        t.created_at,
        ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY t.created_at DESC) AS rn
    FROM payments_transaction t
    JOIN payments_order o
      ON o.id = t.order_id
    WHERE t.status = 'completed'
)
SELECT
    COUNT(*) AS active_subscribers,
    SUM(amount) AS current_active_mrr_minor_units,
    ROUND(SUM(amount) / 100.0, 2) AS current_active_mrr_major_units
FROM latest_completed
WHERE rn = 1
  AND date(created_at) >= date('now', '-30 days');


-- 3. Rolling 30-day churn rate (user churn and revenue churn)
WITH start_customers AS (
    SELECT DISTINCT o.user_id
    FROM payments_transaction t
    JOIN payments_order o
      ON o.id = t.order_id
    WHERE t.status = 'completed'
      AND date(t.created_at) >= date('now', '-60 days')
      AND date(t.created_at) < date('now', '-30 days')
),
end_customers AS (
    SELECT DISTINCT o.user_id
    FROM payments_transaction t
    JOIN payments_order o
      ON o.id = t.order_id
    WHERE t.status = 'completed'
      AND date(t.created_at) >= date('now', '-30 days')
),
revenue_start AS (
    SELECT
        user_id,
        amount AS last_amount
    FROM (
        SELECT
            o.user_id,
            t.amount,
            ROW_NUMBER() OVER (PARTITION BY o.user_id ORDER BY t.created_at DESC) AS rn
        FROM payments_transaction t
        JOIN payments_order o
          ON o.id = t.order_id
        WHERE t.status = 'completed'
          AND date(t.created_at) >= date('now', '-60 days')
          AND date(t.created_at) < date('now', '-30 days')
    ) latest
    WHERE rn = 1
)
SELECT
    (SELECT COUNT(*) FROM start_customers) AS start_customer_count,
    (SELECT COUNT(*) FROM end_customers) AS end_customer_count,
    (SELECT COUNT(*) FROM start_customers
         WHERE user_id NOT IN (SELECT user_id FROM end_customers)
    ) AS churned_customer_count,
    ROUND(
        100.0 * (SELECT COUNT(*) FROM start_customers
                 WHERE user_id NOT IN (SELECT user_id FROM end_customers))
        / NULLIF((SELECT COUNT(*) FROM start_customers), 0),
        2
    ) AS user_churn_pct,
    (SELECT SUM(last_amount) FROM revenue_start) AS revenue_at_start_minor_units,
    (SELECT SUM(last_amount)
         FROM revenue_start
         WHERE user_id NOT IN (SELECT user_id FROM end_customers)
    ) AS churned_revenue_minor_units,
    ROUND(
        100.0 * (SELECT SUM(last_amount)
                 FROM revenue_start
                 WHERE user_id NOT IN (SELECT user_id FROM end_customers))
        / NULLIF((SELECT SUM(last_amount) FROM revenue_start), 0),
        2
    ) AS revenue_churn_pct
;