"""SaaS metric helpers for the payment tables.

This module provides reusable query logic for conversion rate, MRR, and rolling churn.
The queries are intentionally written to match production tables and to minimize repeated
joins or scan overhead.
"""
from __future__ import annotations

import os
from django.db import connection
from django.db.models import Count, Q
from django.utils import timezone

SQL_FILE = os.path.join(os.path.dirname(__file__), 'saas_metrics.sql')


def _execute_sql(sql: str) -> list[dict[str, object]]:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def load_query(name: str) -> str:
    """Load a named query from the SQL file by marker comment."""
    if not os.path.exists(SQL_FILE):
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")

    with open(SQL_FILE, encoding='utf-8') as f:
        content = f.read()

    marker = f"-- {name}"
    start = content.find(marker)
    if start == -1:
        raise ValueError(f"Named query not found: {name}")

    next_marker = content.find('--', start + len(marker))
    query = content[start:next_marker].strip() if next_marker != -1 else content[start:].strip()
    return query


def conversion_rate_over_time() -> list[dict[str, object]]:
    """Return signup-to-paid conversion by monthly signup cohort."""
    sql = load_query('1. Conversion rate: signups to active paid subscribers over time (monthly cohort)')
    return _execute_sql(sql)


def current_active_mrr() -> dict[str, object]:
    """Return current active MRR based on the latest completed payment per user."""
    sql = load_query('2. Current active subscription MRR (absolute value)')
    rows = _execute_sql(sql)
    return rows[0] if rows else {}


def rolling_30_day_churn() -> dict[str, object]:
    """Return a rolling 30-day user and revenue churn snapshot."""
    sql = load_query('3. Rolling 30-day churn rate (user churn and revenue churn)')
    rows = _execute_sql(sql)
    return rows[0] if rows else {}


if __name__ == '__main__':
    import django
    django.setup()

    print('Conversion rate over time:')
    for row in conversion_rate_over_time():
        print(row)

    print('\nCurrent active MRR:')
    print(current_active_mrr())

    print('\nRolling 30-day churn:')
    print(rolling_30_day_churn())
