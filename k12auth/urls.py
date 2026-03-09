
from django.urls import path,include
from k12auth import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login', views.user_login, name='user_login'),
    path('register', views.user_registrattion, name='user_registrattion'),
    path('members_dashboard', views.member_dashboard, name='member_dashboard'),
    path('register_a_member', views.register_a_memberView, name='register_a_memberView'),
    path('members_login', views.members_loginView, name='members_loginView'),
    path('member_logout', views.member_logoutView, name='member_logoutView'),
    
    path('change_pin', views.change_pinView, name='change_pinView'),
    path('reset_pin', views.reset_pinView, name='reset_pinView'),
    path('preference_date_successful/<str:preference_date>', views.preference_date_successfulView, name='preference_date_successfulView'),
    path('set_preference_date', views.set_preference_dateView, name='set_preference_dateView'),
    path('save_preference_date', views.save_preference_dateView, name='save_preference_dateView'),
    
    path('change_photo', views.change_photoView, name='change_photoView'),

    
    path('delete_preference_Date', views.delete_preference_DateView, name='delete_preference_DateView'),
    path('delete_preference_date', views.delete_preference_dateView, name='delete_preference_dateView'),
    path('preference_delete_successful', views.preference_delete_successfulView, name='preference_delete_successfulView'),

]
