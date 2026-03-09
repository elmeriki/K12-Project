
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

    path('withdrawals', views.withdrawalsView, name='withdrawalsView'),


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
    
    path('close_donation/<int:donationId>', views.close_donationView, name='close_donationView'),

    
    path('transfer', views.transferView, name='transferView'),
    path('verify_fund_transfer', views.verify_fund_transferView, name='verify_fund_transferView'),
    path('finalise_transfer', views.finalise_transferView, name='finalise_transferView'),
       
    path('donation_withdrawal_successful_confirmation/<int:withdrawalID>', views.donation_withdrawal_successfulView, name='donation_withdrawal_successfulView'),


    path('transfer_donation/<int:donationID>', views.transfer_donationView, name='transfer_donationView'),
    path('transfer_donation_', views.transfer_donation_View, name='transfer_donation_View'),
    path('donation_sucessful/<int:donationId>', views.donation_sucessfulView, name='donation_sucessfulView'),
    path('donation_withdrawal_sucessful/<int:withdrawalID>', views.donation_withdrawal_sucessfulView, name='donation_withdrawal_sucessfulView'),
    path('donation_withdrawal', views.donation_withdrawalView, name='donation_withdrawalView'),

    path('process_donation_withdrawal', views.process_donation_withdrawalView, name='process_donation_withdrawalView'),

    path('final_donation_withdrawal', views.final_donation_withdrawalView, name='final_donation_withdrawalView'),


    path('make_withdrawal', views.make_withdrawalView, name='make_withdrawalView'),
    path('finalise_make_withdrawal', views.finalise_make_withdrawalView, name='finalise_make_withdrawalView'),
    path('withdrawal_success/<int:withdrawalID>', views.withdrawal_successView, name='withdrawal_successView'),

    path('transfer_successful/<int:sendersID>/<int:recieverID>', views.transfer_successfulView, name='transfer_successfulView'),


    path('process_withdrawal_request/<int:withdrawalID>', views.process_withdrawal_requestView, name='process_withdrawal_requestView'),
    path('finalise_withdrawal', views.finalise_withdrawalView, name='finalise_withdrawalView'),
    path('withdrawal_successful_confirmation/<int:withdrawalID>', views.withdrawal_successful_confirmationView, name='withdrawal_successful_confirmationView'),

    path('withdrawal_details/<int:withdrawalID>', views.withdrawal_detailsView, name='withdrawal_detailsView'),

    path('change_profile_picture', views.change_profile_pictureView, name='change_profile_pictureView'),
    path('photo_change_successful', views.photo_change_successfulView, name='photo_change_successfulView'),

]
