"""
Django admin configuration for payments app.
"""
from django.contrib import admin
from payments.models import Order, Transaction, StateTransitionLog


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'amount', 'currency', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('user__username', 'idempotency_key')
    readonly_fields = ('created_at', 'updated_at', 'idempotency_key')
    
    fieldsets = (
        ('Order Info', {
            'fields': ('user', 'status', 'amount', 'currency')
        }),
        ('Details', {
            'fields': ('description', 'idempotency_key')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'provider', 'status', 'amount', 'created_at')
    list_filter = ('provider', 'status', 'created_at')
    search_fields = ('transaction_id', 'order__user__username', 'idempotency_key')
    readonly_fields = ('transaction_id', 'created_at', 'updated_at', 'idempotency_key')
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('order', 'transaction_id', 'provider', 'status')
        }),
        ('Amount', {
            'fields': ('amount', 'currency', 'refund_amount')
        }),
        ('Metadata', {
            'fields': ('metadata', 'idempotency_key'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StateTransitionLog)
class StateTransitionLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'from_status', 'to_status', 'actor', 'timestamp')
    list_filter = ('from_status', 'to_status', 'timestamp')
    search_fields = ('order__user__username', 'actor')
    readonly_fields = ('order', 'from_status', 'to_status', 'actor', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
