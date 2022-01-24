from django.urls import path, include
from rest_framework import routers

from wallet.views import (
    CustomerAuthToken, CustomerWalletView, DepositAmount,
    WithdrawAmount
)

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('init/', CustomerAuthToken.as_view(), name='api_token_auth'),
    path('wallet/', CustomerWalletView.as_view({
        'get': 'retrieve',
        'patch': 'patch',
        'post': 'post'
    }), name='wallet'),
    path('wallet/deposit/', DepositAmount.as_view(), name="Deposit Amount"),
    path('wallet/withdrawals/', WithdrawAmount.as_view(), name='Withdraw Amount')

]
