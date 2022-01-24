import datetime

from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.compat import coreapi, coreschema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.schemas import ManualSchema
from rest_framework.schemas import coreapi as coreapi_schema
from rest_framework.views import APIView

from base.renderers import custom_response_renderer
from customer.models import Customer
from wallet.helpers import prepare_data_wallet, fetch_wallet, is_valid_referenceid
from wallet.models import Wallet, Transaction

from wallet.serializers import (
    WalletInitSerializer, WalletSerializer
)


# Create your views here.
class CustomerAuthToken(ObtainAuthToken):
    serializer_class = WalletInitSerializer

    if coreapi_schema.is_enabled():
        schema = ManualSchema(
            fields=[
                coreapi.Field(
                    name="customer_xid",
                    location='form',
                    schema=coreschema.String(
                        title="customer_xid",
                        description="Valid customer_xid for authentication",
                    ),
                ),
            ],
            encoding="application/json",
        )

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.validated_data['customer']
            token, created = Token.objects.get_or_create(user=customer.user)
            return custom_response_renderer(
                data={'token': token.key},
                status="success",
                status_code=status.HTTP_200_OK
            )
        else:
            return custom_response_renderer(
                data={'error': serializer.errors},
                status="fail",
                status_code=status.HTTP_400_BAD_REQUEST
            )


class CustomerWalletView(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    serializer_class = WalletSerializer
    http_method_names = ['get', 'patch', 'post']

    def get_queryset(self):
        return Wallet.objects.filter(owned_by__user=self.request.user)

    def get_object(self):
        object = get_object_or_404(self.get_queryset())
        return object

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == Wallet.ENABLE:
            serializer = self.get_serializer(instance, data=request.data)
            if serializer.is_valid():
                return custom_response_renderer(
                    data={'wallet': serializer.data},
                    status="success",
                    status_code=status.HTTP_200_OK
                )
            else:
                msg = serializer.errors
        else:
            msg = "Disabled"
        return custom_response_renderer(
            data={'error': msg},
            status="fail",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['PATCH'], detail=True)
    def patch(self, request, *args, **kwargs):
        is_disabled = request.data.get('is_disabled', None)
        wallet, msg = fetch_wallet(request.user)

        if is_disabled == 'true':
            if wallet and wallet.status == Wallet.ENABLE:
                wallet.status = Wallet.DISABLE
                wallet.disabled_at = datetime.datetime.now()
                wallet.save()
                return custom_response_renderer(
                    data={'wallet': prepare_data_wallet(wallet)},
                    status="success",
                    status_code=status.HTTP_200_OK
                )
            else:
                msg = "Your wallet is already disabled."
        else:
            msg = "Value of is_disabled must be true."

        return custom_response_renderer(
            data={'errors': msg},
            status="fail",
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['POST'], detail=True)
    def post(self, request, *args, **kwargs):
        customer = Customer.objects.filter(user=request.user).first()
        wallet = Wallet.objects.filter(owned_by=customer).first()
        if wallet and wallet.status == Wallet.DISABLE:
            wallet.status = Wallet.ENABLE
            wallet.enabled_at = datetime.datetime.now()
            wallet.save()
            return custom_response_renderer(
                data={'wallet': prepare_data_wallet(wallet)},
                status="success",
                status_code=status.HTTP_200_OK
            )
        else:
            msg = "Already enabled."
        return custom_response_renderer(
            data={'errors': msg},
            status="fail",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class DepositAmount(APIView):
    """ API to deposit an amount to user's wallet.
    """

    authentication_classes = (TokenAuthentication,)
    queryset = Transaction.objects.all()

    def post(self, request):
        amount = request.data.get('amount', None)
        reference_id = is_valid_referenceid(request.data.get('reference_id', None))
        if not reference_id:
            msg = "Reference id is not valid."
            custom_response_renderer(
                data={'error': msg},
                status="fail",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if amount and reference_id:
            wallet = Wallet.objects.filter(owned_by__user=request.user)
            if not wallet.exists():
                msg = "Your wallet is not found."
            else:
                wallet = wallet.first()
                if wallet.status == "enable":

                    wallet.deposit(int(request.data.get('amount')), reference_id)
                    transaction = Transaction.objects.filter(wallet=wallet).last()
                    data = {
                        "id": transaction.id,
                        "deposited_by": wallet.owned_by.customer_id,
                        "status": wallet.status,
                        "deposited_at": transaction.transaction_at,
                        "amount": int(transaction.amount),
                        "reference_id": transaction.reference_id
                    }
                    return custom_response_renderer(
                        data={'wallet': data},
                        status="success",
                        status_code=status.HTTP_200_OK
                    )
                else:
                    msg = "Your wallet is disabled."
        else:
            msg = "Missing amount or reference_id information."
        return custom_response_renderer(
            data={'error': msg},
            status="fail",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class WithdrawAmount(APIView):
    """ API to withdraw amount from user's wallet.
    """

    authentication_classes = (TokenAuthentication,)
    queryset = Transaction.objects.all()

    def post(self, request):
        amount = request.data.get('amount', None)
        reference_id = is_valid_referenceid(request.data.get('reference_id', None))
        if not reference_id:
            msg = "Reference id is not valid."
            custom_response_renderer(
                data={'error': msg},
                status="fail",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if amount and reference_id:
            if not Transaction.objects.filter(reference_id=reference_id,
                                              transaction_type=Transaction.TransactionTypes.Deposit).first():
                wallet = Wallet.objects.filter(owned_by__user=request.user)
                if not wallet.exists():
                    msg = "Your wallet is not found."
                else:
                    wallet = wallet.first()
                    if wallet.status == "enable":

                        wallet.withdraw(int(request.data.get('amount')), reference_id)
                        transaction = Transaction.objects.filter(wallet=wallet).last()
                        data = {
                            "id": transaction.id,
                            "withdrawn_by": wallet.owned_by.customer_id,
                            "status": wallet.status,
                            "withdrawn_at": transaction.transaction_at,
                            "amount": int(transaction.amount),
                            "reference_id": transaction.reference_id
                        }
                        return custom_response_renderer(
                            data={'wallet': data},
                            status="success",
                            status_code=status.HTTP_200_OK
                        )
                    else:
                        msg = "Your wallet is disabled."
            else:
                msg = "Your wallet is disabled. Enable it first in order to make deposits."
        else:
            msg = "Missing amount or reference_id information."
        return custom_response_renderer(
            data={'error': msg},
            status="fail",
            status_code=status.HTTP_400_BAD_REQUEST
        )
