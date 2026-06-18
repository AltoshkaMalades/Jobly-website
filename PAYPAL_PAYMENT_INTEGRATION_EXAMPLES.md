# 💳 PayPal Payment Integration - Quick Reference

## 🔗 Direct Links

Add payment links anywhere in your templates:

### Basic Payment Link (Tailwind CSS)
```html
<a href="/payments/paypal/?amount=29.99&description=Premium+Plan" 
   class="px-6 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-colors">
    💳 Pay $29.99 with PayPal
</a>
```

### Payment Button with Icon
```html
<a href="/payments/paypal/?amount=9.99&description=Monthly+Subscription&currency=USD" 
   class="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white font-bold rounded-xl hover:shadow-lg transition-all">
    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM5 16a2 2 0 11-4 0 2 2 0 014 0zm8 0a2 2 0 11-4 0 2 2 0 014 0z"></path>
    </svg>
    <span>Subscribe Now</span>
</a>
```

### Plan Cards with Payment Buttons
```html
<div class="grid md:grid-cols-3 gap-6">
    <!-- Basic Plan -->
    <div class="border-2 border-neutral-200 rounded-xl p-6 hover:border-blue-600 transition-colors">
        <h3 class="text-2xl font-bold mb-2">Starter</h3>
        <p class="text-4xl font-black text-blue-600 mb-4">$9<span class="text-lg">.99</span></p>
        <ul class="space-y-2 mb-6 text-neutral-600">
            <li>✓ 10 job applications</li>
            <li>✓ Basic profile</li>
            <li>✓ Email support</li>
        </ul>
        <a href="/payments/paypal/?amount=9.99&description=Starter+Plan" 
           class="w-full py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors">
            Get Started
        </a>
    </div>

    <!-- Professional Plan -->
    <div class="border-2 border-blue-600 rounded-xl p-6 shadow-lg relative">
        <div class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-bold">
            POPULAR
        </div>
        <h3 class="text-2xl font-bold mb-2">Professional</h3>
        <p class="text-4xl font-black text-blue-600 mb-4">$29<span class="text-lg">.99</span></p>
        <ul class="space-y-2 mb-6 text-neutral-600">
            <li>✓ Unlimited applications</li>
            <li>✓ Resume builder</li>
            <li>✓ Priority support</li>
        </ul>
        <a href="/payments/paypal/?amount=29.99&description=Professional+Plan" 
           class="w-full py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors">
            Upgrade Now
        </a>
    </div>

    <!-- Enterprise Plan -->
    <div class="border-2 border-neutral-200 rounded-xl p-6 hover:border-blue-600 transition-colors">
        <h3 class="text-2xl font-bold mb-2">Enterprise</h3>
        <p class="text-4xl font-black text-blue-600 mb-4">$99<span class="text-lg">.99</span></p>
        <ul class="space-y-2 mb-6 text-neutral-600">
            <li>✓ Everything in Pro</li>
            <li>✓ Team features</li>
            <li>✓ 24/7 support</li>
        </ul>
        <a href="/payments/paypal/?amount=99.99&description=Enterprise+Plan" 
           class="w-full py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors">
            Contact Sales
        </a>
    </div>
</div>
```

---

## 🎯 Integration Examples

### In Job Detail Page
```html
{% extends "accounts/base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <div class="max-w-2xl">
        <h1>{{ job.title }}</h1>
        <p>{{ job.description }}</p>
        
        {% if user.is_authenticated %}
            <a href="{% url 'payments:paypal_payment' %}?amount=49&description={{ job.title|urlencode }}+Application+Fee" 
               class="mt-6 px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700">
                Apply Now - Pay $49
            </a>
        {% else %}
            <a href="{% url 'login' %}" class="mt-6 px-6 py-3 bg-neutral-900 text-white font-bold rounded-lg">
                Login to Apply
            </a>
        {% endif %}
    </div>
</div>
{% endblock %}
```

### In Course Card Component
```html
<div class="bg-white rounded-xl border-2 border-neutral-200 overflow-hidden hover:shadow-lg transition-shadow">
    <img src="{{ course.image.url }}" alt="{{ course.title }}" class="w-full h-48 object-cover">
    
    <div class="p-6">
        <h3 class="text-xl font-bold mb-2">{{ course.title }}</h3>
        <p class="text-neutral-600 mb-4">{{ course.description|truncatewords:20 }}</p>
        
        <div class="flex items-center justify-between">
            <span class="text-2xl font-black text-blue-600">${{ course.price }}</span>
            <a href="/payments/paypal/?amount={{ course.price }}&description=Course:+{{ course.title|urlencode }}" 
               class="px-4 py-2 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700 transition-colors">
                Enroll
            </a>
        </div>
    </div>
</div>
```

### In Profile Page
```html
{% if user.is_authenticated %}
<div class="mt-8 pt-8 border-t-2">
    <h2 class="text-2xl font-bold mb-4">💎 Upgrade Your Account</h2>
    
    <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
            <h3 class="text-xl font-bold text-blue-900 mb-4">Premium Features</h3>
            <ul class="space-y-2 text-blue-800 mb-6">
                <li>✓ Unlimited job applications</li>
                <li>✓ Advanced resume builder</li>
                <li>✓ Salary insights</li>
                <li>✓ Priority support</li>
            </ul>
            <a href="/payments/paypal/?amount=19.99&description=Premium+Monthly&currency=USD" 
               class="w-full px-4 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700">
                Upgrade - $19.99/month
            </a>
        </div>
        
        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border-2 border-purple-200">
            <h3 class="text-xl font-bold text-purple-900 mb-4">🚀 Pro Package</h3>
            <ul class="space-y-2 text-purple-800 mb-6">
                <li>✓ Everything in Premium</li>
                <li>✓ Career coaching</li>
                <li>✓ Mock interviews</li>
                <li>✓ Company insights</li>
            </ul>
            <a href="/payments/paypal/?amount=49.99&description=Pro+Package+Monthly&currency=USD" 
               class="w-full px-4 py-3 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-700">
                Get Pro - $49.99/month
            </a>
        </div>
    </div>
</div>
{% endif %}
```

---

## 📊 Payment Status Tracking

### Check Order Status
```html
<div id="payment-status">
    Loading payment status...
</div>

<script>
async function checkPaymentStatus(orderId) {
    const response = await fetch(`/api/payments/orders/${orderId}/`);
    const data = await response.json();
    
    if (data.success) {
        document.getElementById('payment-status').innerHTML = `
            <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
                <p><strong>Order:</strong> #${data.order.id}</p>
                <p><strong>Amount:</strong> ${data.order.currency} ${data.order.amount}</p>
                <p><strong>Status:</strong> ${data.order.status}</p>
            </div>
        `;
    }
}
</script>
```

---

## 🔄 Dynamic Payment Amount

### From Form Input
```html
<form method="get" action="{% url 'payments:paypal_payment' %}" class="space-y-4">
    <div>
        <label class="block font-bold mb-2">Amount</label>
        <input type="number" name="amount" min="0.01" step="0.01" value="29.99" 
               class="w-full px-4 py-2 border-2 border-neutral-200 rounded-lg focus:border-blue-600 outline-none">
    </div>
    
    <div>
        <label class="block font-bold mb-2">Description</label>
        <input type="text" name="description" value="Service Payment"
               class="w-full px-4 py-2 border-2 border-neutral-200 rounded-lg focus:border-blue-600 outline-none">
    </div>
    
    <button type="submit" class="w-full px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-700">
        Proceed to Payment
    </button>
</form>
```

---

## 📱 Mobile Payment Link
```html
<!-- Mobile-optimized payment link -->
<a href="{% url 'payments:paypal_payment' %}?amount=29.99&description=Premium+Access" 
   class="block w-full py-3 px-4 bg-blue-600 text-white font-bold rounded-lg text-center hover:bg-blue-700 transition-colors">
    💳 Pay with PayPal
</a>
```

---

## ✅ Checklist for Integration

- [ ] Add payment links to job detail page
- [ ] Add payment buttons to course cards  
- [ ] Add upgrade links to user profile
- [ ] Configure email notifications
- [ ] Set up receipt generation
- [ ] Test with PayPal sandbox
- [ ] Customize payment page styling
- [ ] Add payment history to dashboard
- [ ] Configure webhooks for live environment

---

**Ready to go!** Start adding payment links to your application.
