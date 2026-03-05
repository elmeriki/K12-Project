
from django.urls import path,include
from members import views

urlpatterns = [
    path('app_setting', views.app_settingView, name='app_settingView'),
    path('member_list', views.member_listView, name='member_listView'),
    path('unactivated_members', views.unactivated_membersView, name='unactivated_membersView'),
    path('transactions', views.transactionsView, name='transactionsView'),
    path('transactions_details/<int:transactionid>', views.transactions_detailsView, name='transactions_detailsView'),
    path('activate_account/<int:select_username>', views.activate_accountView, name='activate_accountView'),
    path('activate_member_account', views.activate_member_accountView, name='activate_member_accountView'),
    path('member_details/<int:select_username>', views.member_detailsView, name='member_detailsView'),

    path('payment_successful/<int:amount>/<str:transactionReference>', views.payment_successfulView, name='payment_successfulView'),

    path('saving_successful/<int:transactionId>', views.saving_successfulView, name='saving_successfulView'),
    path('saving_unsuccessful/<int:transactionId>', views.saving_unsuccessfulView, name='saving_unsuccessfulView'),

    path('incoming_payment', views.incoming_paymentView, name='incoming_paymentView'),


    path('verify_payment_amount', views.verify_payment_amountView, name='verify_payment_amountView'),
    path('upload_pod', views.upload_podView, name='upload_podView'),
    path('submit_transaction', views.submit_transactionView, name='submit_transactionView'),

    path('reconcile_transaction/<int:transactionId>', views.reconcile_transactionView, name='reconcile_transactionView'),
    path('reconcile_transaction_/<int:transactionId>', views.reconcile_transaction_View, name='reconcile_transaction_View'),

    path('new_donation', views.new_donationView, name='new_donationView'),
    path('create_new_donation', views.create_new_donationView, name='create_new_donationView'),

    path('donations_log/<int:donationId>', views.donations_logView, name='donations_logView'),



    path('donations', views.donationsView, name='donationsView'),
    path('verify_donation_confirmation/<int:donationId>', views.verify_donation_confirmationView, name='verify_donation_confirmationView'),
    path('make_donation/<int:donationId>', views.make_donationView, name='make_donationView'),
    path('make_donation_/<int:donationId>', views.make_donation_View, name='make_donation_View'),
    path('donation_sucessful/<int:donationId>', views.donation_sucessfulView, name='donation_sucessfulView'),
    
    
    path('transfer', views.transferView, name='transferView'),
    path('verify_fund_transfer', views.verify_fund_transferView, name='verify_fund_transferView'),
    path('finalise_transfer', views.finalise_transferView, name='finalise_transferView'),
    
    path('transfer_successful/<int:transactionId>', views.transfer_successfulView, name='transfer_successfulView'),

]
