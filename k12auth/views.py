from django.shortcuts import render,redirect
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User,auth
from django.contrib import  messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count,Sum
from django.db.models import Q
from twilio.rest import Client
from decouple import config
import datetime
from datetime import date
from django.db import transaction
import threading
from k12auth.models import *


def welcome(request):
    return render(request,'index.html',{})


def user_login(request):
    return render(request,'auth/login.html',{})



def user_registrattion(request):
    return render(request,'auth/register.html',{})


def members_profile(request):
    return render(request,'members/profile.html',{})




@transaction.atomic
def register_a_memberView(request):
    if request.method == "POST" and request.POST['fname'] and request.POST['lname'] and request.POST['email'] and request.POST['phone'] and request.POST['password']:
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=str(request.POST['email'])
        phone=request.POST['phone']
        password=request.POST['password'] 
        
        if len(phone) > 9:
            messages.info(request,"Incorrect cell phone number")
            return redirect('/register')
        
        if len(phone) < 9:
            messages.info(request,"Incompleted cell phone number")
            return redirect('/register')
        
        if len(password) > 5:
            messages.info(request,"PIN must be 5 Digit")
            return redirect('/register')
        
        if len(password) < 5:
            messages.info(request,"PIN must be 5 Digit")
            return redirect('/register')
        
        if User.objects.filter(username=phone).exists():
            messages.info(request,"Cell Phone Number has been used already")
            return redirect('/register')
        
        if User.objects.filter(email=email).exists():
            messages.info(request,"Email address has been used already")
            return redirect('/register')
        
        create_new_member_account=User.objects.create_user(username=phone,first_name=fname,last_name=lname,email=email,password=password)
        if create_new_member_account:
            create_new_member_account.save()
            messages.info(request,"Customer account has been created successfully")
            return redirect('/register')
        else:
            messages.info(request,"Account could not be created successfully")
            return redirect('/register')
    else:
        messages.info(request,"Enter valid data")
        return redirect('/register')
    
    
    
@transaction.atomic
def members_loginView(request):
    if request.method =="POST" and request.POST['username'] and request.POST['password']:
        username = request.POST['username']
        password =request.POST['password']
                
        if not User.objects.filter(username=username).exists():
            messages.info(request,'Incorrect login credentials.')
            return redirect('/login')  
        
        userlog = auth.authenticate(username=username,password=password)
        # checking if it is an existing user in the database
        
        # customise error messages handler
        if userlog is not None:
            auth.login(request, userlog)
            if request.user.is_authenticated:
                return redirect('/members_profile')
        else:
            messages.info(request,"Incorrect login credentials.")
            return redirect('/login')
        
        if userlog is not None:
            auth.login(request, userlog)
            if request.user.is_authenticated and not request.user.is_activation:
                messages.info(request,"Your acount is not activated ")
                return redirect('/login')
        else:
            messages.info(request,"Incorrect login credentials.")
            return redirect('/login')
                
    else:
        messages.info(request,"Enter a Valid username and PIN")
        return redirect('/login')  
    
    
def member_logoutView(request):
    auth.logout(request)
    messages.info(request,"Logout Successfully")
    return redirect('/') 
