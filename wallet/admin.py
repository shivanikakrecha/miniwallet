from django.contrib import admin
from wallet.models import (
    Wallet, Transaction
)


# Register your models here.
class TransactionInline(admin.TabularInline):
    model = Transaction
    min_num = 0
    extra = 0
    max_num = 100

    fields = ['id', 'wallet', 'amount', 'running_balance', 'created_at']

    readonly_fields = ['created_at']

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')


class WalletAdmin(admin.ModelAdmin):
    list_display = ('id', 'owned_by', 'balance', 'status')

    inlines = [TransactionInline]

    def has_add_permission(self, request, obj=None):
        return True


admin.site.register(Wallet, WalletAdmin)
admin.site.register(Transaction)
