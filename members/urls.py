
from django.urls import path,include
from members import views

urlpatterns = [
    path('app_setting', views.app_settingView, name='app_settingView'),
    path('member_list', views.member_listView, name='member_listView'),
    path('transactions', views.transactionsView, name='transactionsView'),
    path('transactions_details', views.transactions_detailsView, name='transactions_detailsView'),
    path('activate_account/<int:select_username>', views.activate_accountView, name='activate_accountView'),
    path('activate_member_account', views.activate_member_accountView, name='activate_member_accountView'),
    path('member_details/<int:select_username>', views.member_detailsView, name='member_detailsView'),

    path('verify_payment_amount', views.verify_payment_amountView, name='verify_payment_amountView'),
    path('upload_pod', views.upload_podView, name='upload_podView'),
    path('submit_transaction', views.submit_transactionView, name='submit_transactionView'),

]
