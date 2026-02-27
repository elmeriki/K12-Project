
from django.urls import path,include
from k12auth import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login', views.user_login, name='user_login'),
    path('register', views.user_registrattion, name='user_registrattion'),
    path('members_profile', views.members_profile, name='members_profile'),
    path('register_a_member', views.register_a_memberView, name='register_a_memberView'),
    path('members_login', views.members_loginView, name='members_loginView'),
    path('member_logout', views.member_logoutView, name='member_logoutView')

]
