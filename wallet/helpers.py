import uuid

from customer.models import Customer
from wallet.models import Wallet


def prepare_data_wallet(wallet):
    data = {
        "id": wallet.id,
        "owned_by": wallet.owned_by.customer_id,
        "status": wallet.status,
        "disabled_at": wallet.disabled_at,
        "balance": int(wallet.balance)
    }
    return data


def fetch_wallet(user):
    customer = Customer.objects.filter(user=user)
    wallet = Wallet.objects.filter(owned_by=customer)

    if not (customer.exists() or wallet.exist()):
        return None, "Invalid user."


def is_valid_referenceid(reference_id):
    try:
        uuid.UUID(str(reference_id))
        return True
    except ValueError as ve:
        print(ve)
        return False
