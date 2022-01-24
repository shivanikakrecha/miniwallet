import uuid
from django.db import models
from django.conf import settings
from django.db import transaction, IntegrityError
from decimal import Decimal

from base.models import BaseModel
from customer.models import Customer


# Create your models here.
class Wallet(BaseModel):
    """ Wallet model. Stores wallet related details.
    """

    DISABLE = "disable"
    ENABLE = "enable"

    WALLET_CHOICES = (
        (DISABLE, "Disable"),
        (ENABLE, "Enable")
    )

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4
    )
    owned_by = models.OneToOneField(
        Customer, null=True, on_delete=models.SET_NULL,
        related_name='wallet', verbose_name="Owned by"
    )

    balance = models.DecimalField(
        verbose_name='Wallet Balance', max_digits=10, decimal_places=2, default=0
    )
    status = models.CharField(
        verbose_name="Wallet Status", max_length=20, default="disable",
        choices=WALLET_CHOICES
    )
    enabled_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Enabled At"
    )
    disabled_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Disabled At"
    )

    @transaction.atomic
    def deposit(self, amount, reference_id):
        """ Deposit `amount` to wallet.
        """

        amount = Decimal(amount)

        self.transaction_set.create(
            amount=amount,
            running_balance=self.balance + amount,
            reference_id=reference_id
        )
        self.balance += amount
        self.save()

    @transaction.atomic
    def withdraw(self, amount, reference_id):
        """ Withdraw `amount` to wallet.
        """

        amount = Decimal(amount)

        if amount > self.balance:
            raise IntegrityError("Insufficient Balance")

        self.transaction_set.create(
            amount=-amount,
            running_balance=self.balance - amount,
            reference_id=reference_id
        )
        self.balance -= amount
        self.save()

    def __str__(self):
        return self.owned_by.user.email


class Transaction(BaseModel):
    """ `Transaction` model to store any money transaction details.
    """

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"

    TRANSACTION_CHOICES = (
        (DEPOSIT, 'Deposit'),
        (WITHDRAWAL, 'Withdrawal')
    )
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4
    )
    wallet = models.ForeignKey(
        Wallet, null=True, on_delete=models.SET_NULL
    )
    amount = models.DecimalField(
        verbose_name='Amount', max_digits=10, decimal_places=2, default=0
    )
    running_balance = models.DecimalField(
        verbose_name='Wallet Balance at the time of transaction', max_digits=10,
        decimal_places=2, default=0
    )
    reference_id = models.UUIDField(
        default=uuid.uuid4
    )
    transaction_at = models.DateTimeField(
        auto_now=True, null=True, blank=True, verbose_name="Transaction At"
    )
    transaction_type = models.CharField(
        verbose_name="Transaction Type", max_length=20, default="disable",
        choices=TRANSACTION_CHOICES
    )

    def __str__(self):
        return self.wallet.owned_by.user.email
