from rest_framework import serializers
from wallet.models import (
    Wallet, Transaction
)
from customer.models import Customer


class WalletInitSerializer(serializers.Serializer):
    customer_xid = serializers.UUIDField(
        label="Customer ID",
        write_only=True,
        required=False
    )

    token = serializers.CharField(
        label="Token",
        read_only=True
    )

    def validate(self, attrs):
        customer_xid = attrs.get('customer_xid')

        if customer_xid:
            customer = Customer.objects.filter(customer_id=customer_xid)

            if not customer.exists():
                msg = "Unable to find customer with provided customer xid."
                raise serializers.ValidationError(msg)
        else:
            msg = 'Missing data for required field.'
            raise serializers.ValidationError({"customer_xid": msg})

        attrs['customer'] = customer.first()
        return attrs


class WalletSerializer(serializers.ModelSerializer):
    enabled_at = serializers.SerializerMethodField(
        label="Enabled At"
    )
    owned_by = serializers.SerializerMethodField(
        label="Owned By"
    )
    balance = serializers.SerializerMethodField(
        label="Balance"
    )

    def __init__(self, *args, **kwargs):
        kwargs['partial'] = True
        super(WalletSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Wallet
        fields = ('id', 'owned_by', 'status', 'enabled_at', 'balance')

    def get_owned_by(self, obj):
        if obj.owned_by:
            return obj.owned_by.customer_id
        return None

    def get_enabled_at(self, obj):
        return obj.created_at

    def get_balance(self, obj):
        return int(obj.balance)

    def update(self, instance, validated_data):
        is_disabled = validated_data.get('is_disabled')
        if is_disabled and instance and instance.status == 'enable':
            if is_disabled == 'true':
                instance.status = "disable"
                instance.save()
            else:
                msg = "Value of is_disabled must be true."
                raise serializers.ValidationError(msg)
        else:
            msg = "Your wallet is already disabled."
            raise serializers.ValidationError(msg)

        return instance


class TransactionSerializer(serializers.ModelSerializer):
    deposited_by = serializers.SerializerMethodField(
        label="Deposit By"
    )

    deposited_at = serializers.SerializerMethodField(
        label="Deposit At"
    )

    class Meta:
        model = Transaction
        fields = ('id', 'deposited_by', 'deposited_at', 'amount', 'reference_id')

    def get_deposited_by(self, obj):
        return obj.wallet.owned_by.customer_id

    def get_deposited_at(self, obj):
        return obj.transaction_at

    def validate(self, attrs):
        amount = attrs.get('amount')

        if (not amount) or (amount <= 0):
            msg = "Please enter a valid amount."
            raise serializers.ValidationError(msg)

        return attrs

    def create(self, validated_data):
        reference_id = validated_data.get('reference_id')
        wallet = Wallet.objects.get(owned_by__customer_id=reference_id)

        if not self.context.get('is_withdraw'):
            wallet.deposit(int(validated_data.get('amount')))
        else:
            wallet.withdraw(int(validated_data.get('amount')))
        transaction = Transaction(**validated_data)
        return transaction
