from django.shortcuts import render,redirect
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User ,auth
from django.contrib import  messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count,Sum
from django.db.models import Q
import datetime
from datetime import date
from django.db import transaction
import threading
from k12auth.models import User
from members.models import *
from django.conf import settings
from mailjet_rest import Client as MailjetClient  # Alias for the Client class
import random
from datetime import datetime


def welcome(request):
    if request.user.is_authenticated:
        return redirect('/members_dashboard')
    else:
        return render(request,'index.html',{})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('/members_dashboard')
    else:
        return render(request,'auth/login.html')


def resetView(request):
    if request.user.is_authenticated:
        return redirect('/members_dashboard')
    else:
        return render(request,'auth/reset.html')

def user_registrattion(request):
    if request.user.is_authenticated:
        return redirect('/members_dashboard')
    else:
        return render(request,'auth/register.html',{})

@login_required(login_url="/login")
def member_dashboard(request):
    members_instance=User.objects.filter( Q(is_member=True,is_staff=False) | Q(is_member=False,is_staff=False) )
    username = request.user.username
    mainUserInstance = User.objects.get(username=settings.MAIN_GROUP_NUMBER)
    select_members_instance=User.objects.get(username=username)        
    mainAccountBalance = Account.objects.filter(member=mainUserInstance).values_list('mainAccountBalance', flat=True).first() 
    membersBalance = Account.objects.filter(member=select_members_instance).values_list('memberBalance',flat=True).first()
    troubleFundsBalance = Account.objects.filter(member=mainUserInstance).values_list('troubleFundsBalance',flat=True).first()
    groupRegistrationAmount = Account.objects.filter(member=select_members_instance).values_list('registrationAmount',flat=True).first()
    transaction_log = Transaction.objects.filter(member=select_members_instance).order_by('-created_at')[:5]
    toBeReconcileTransaction = Transaction.objects.filter(transactionStatus="Initiated",transactionType="Deposit").order_by('-created_at')[:10]
    toBeWithdrawalTransaction = Withdrawal.objects.filter(withdrawalStatus="Initiated").order_by('-created_at')[:10]

    data = {
        'members_instance':members_instance,
        'mainAccountBalance':mainAccountBalance,
        'membersBalance':membersBalance,
        'troubleFundsBalance':troubleFundsBalance,
        'groupRegistrationAmount':groupRegistrationAmount,
        'transaction_log':transaction_log,
        'toBeReconcileTransaction':toBeReconcileTransaction,
        'toBeWithdrawalTransaction':toBeWithdrawalTransaction
    }    
    return render(request,'members/dashboard.html',context=data)

@login_required(login_url="/login")
def reset_pinView(request):
    return render(request,'members/app_change_pin.html',{})


@login_required(login_url="/login")
def set_preference_dateView(request):
    preferenceDateCount=PreferenceDate.objects.filter(member=request.user).count()
    data = {
        "preferenceDateCount":preferenceDateCount
    }
    return render(request,'members/app_preference_date.html',context=data)

@login_required(login_url="/login")
def delete_preference_DateView(request):
    return render(request,'members/app_delete_preference_date.html')


@login_required(login_url="/login")
def preference_date_successfulView(request,preference_date):
    data = {
        "preference_date" : preference_date
    }
    return render(request,'members/app_preference_date_successful.html',context=data)


@login_required(login_url="/login")
def preference_delete_successfulView(request):
    return render(request,'members/app_preference_delete_successful.html')


@login_required(login_url="/login")
def change_photoView(request):
    return render(request,'members/app_change_photo.html')

@transaction.atomic
def setTemporalPinView(request):
    if request.method != "POST":
        messages.info(request, "Invalid request.")
        return redirect('/reset')

    email = request.POST.get('email')

    if not email:
        messages.info(request, "Please enter your email address.")
        return redirect('/reset')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.info(request, "Invalid email address.")
        return redirect('/reset')

    # Generate 5 digit temporary PIN
    temporal_pin = str(random.randint(10000, 99999))

    # Set temporary password
    user.set_password(temporal_pin)
    user.save()
    transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
    mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
    data = {
        'Messages': [{
            "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
            "To": [{"Email": user.email, "Name": user.first_name}],
            "Subject": f"Temporary PIN Reset {transaction_date}",
            "HTMLPart": f'''
            <p>Dear <strong>{user.first_name}</strong>,</p>
            <p>
                A request to reset your account PIN was processed on 
                <strong>{transaction_date}</strong>.
            </p>

            <p>
                A temporary PIN has been generated for your account to allow you to log in.
            </p>

            <p>
                <strong>Temporary PIN:{temporal_pin}</strong>
            </p>

            <p>
                Please use this temporary PIN to log in to your account. For security reasons, 
                you will be required to change it immediately after logging in.
            </p>

            <p>
                If you did not request this reset, please contact the administration of 
                <strong>{settings.DEFAULT_FROM_NAME}</strong> immediately.
            </p>

            <p>
            Kind regards,<br>
            <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
            </p>
            <hr>

            <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
            <p>
                This email and any attachments are confidential and intended solely for the named recipient. 
                If you have received this email in error, please notify the sender and delete it from your system.
            </p>
            '''
        }]
    }
    mailjet.send.create(data=data)
    messages.info(
        request,
        "Your temporary PIN has been set and sent to your email. Please login and change it immediately."
    )
    return redirect('/login')


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
            
            create_new_members_account = Account(member=create_new_member_account,accountNumber=phone)
            create_new_members_account.save()
    
            mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
            data = {
                'Messages': [{
                    "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                    "To": [{"Email": email, "Name": fname}],
                    "Subject": "K12 Registration Confirmation",
                    "HTMLPart": f'''
                    <p>Dear <strong>{fname}</strong>,</p>
                    <p>
                        We are pleased to confirm that a new account has been created for the {settings.DEFAULT_FROM_NAME}. 
                        The account is currently under verification. Once the verification process is completed, your account will be activated.
                    </p>
                    <hr>
                    <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
                    <p>
                        This email and any attachments are confidential and intended for the named recipient only. 
                        If you received this message in error, please notify the sender immediately and delete it. 
                        Do not copy, disclose, or use any part of this message. Please note that internet communications may not be secure or virus-free.
                    </p>
                    '''}]
            }
            mailjet.send.create(data=data)
            messages.info(request,"Account created! Verification is pending before it becomes active")
            return redirect('/register')
        else:
            messages.info(request,"Account could not be created successfully. Please try again.")
            return redirect('/register')
    else:
        messages.info(request,"Invalid input. Please check and try again.")
        return redirect('/register')
    
    
@transaction.atomic
@login_required(login_url="/login")
def change_pinView(request):
    if request.method == "POST" and request.POST['username'] and request.POST['password']:
        username=request.POST['username']
        password=request.POST['password']
        
        if len(password) != 5:
            messages.info(request, "PIN should be 5 digits")
            return redirect('/reset_pin')
                
        loginUserInstance = User.objects.get(username=username)
        loginUserInstance.set_password(password)
        loginUserInstance.save()
        transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
        user = request.user
        mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
        data = {
            'Messages': [{
                "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                "To": [{"Email": user.email, "Name": user.first_name}],
                "Subject": f"PIN Change Confirmation {transaction_date}",
                "HTMLPart": f'''
                <p>Dear <strong>{user.first_name}</strong>,</p>

                <p>
                    This email confirms that your account PIN was successfully changed on 
                    <strong>{transaction_date}</strong>.
                </p>

                <p>
                    Your new PIN is now active and will be required for all future logins 
                    to your <strong>{settings.DEFAULT_FROM_NAME}</strong> member account.
                </p>

                <p>
                    If you made this change, no further action is required.
                </p>

                <p>
                    However, if you did not authorize this change, please contact the 
                    administration of <strong>{settings.DEFAULT_FROM_NAME}</strong> immediately 
                    to secure your account.
                </p>

                <p>
                Kind regards,<br>
                <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
                </p>
                <hr>

                <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
                <p>
                    This email and any attachments are confidential and intended solely for the named recipient. 
                    If you have received this email in error, please notify the sender and delete it from your system.
                </p>
                '''
            }]
        }
        mailjet.send.create(data=data)
        messages.info(request,"New PIN has been changed successfuly")
        return redirect('/member_logout')
    else:
        messages.info(request,"Invalid input. Please check and try again.")
        return redirect('/reset_pin')
    


@transaction.atomic
def members_loginView(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.info(request, "Incorrect login credentials.")
            return redirect('/login')

        userlog = auth.authenticate(username=username, password=password)

        if userlog is None:
            messages.info(request, "Incorrect login credentials.")
            return redirect('/login')

        # check activation BEFORE login
        if not userlog.is_member and not userlog.is_admin:
            messages.info(request, "Your account is not activated.")
            return redirect('/login')

        # login user
        auth.login(request, userlog)
        return redirect('/members_dashboard')

    else:
        messages.info(request, "Enter a valid username and PIN")
        return redirect('/login')
    
def member_logoutView(request):
    auth.logout(request)
    messages.info(request,"Logout Successfully")
    return redirect('/') 


@transaction.atomic
@login_required(login_url="/login")
def save_preference_dateView(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        preference_date = request.POST.get("preference_date")

        if not username or not preference_date:
            messages.info(request, "Please enter a valid username and date")
            return redirect('/set_preference_date')

        try:
            user_instance = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.info(request, "Incorrect username to set preference date")
            return redirect('/set_preference_date')

        # Update if exists, otherwise create new
        preference_instance, created = PreferenceDate.objects.update_or_create(
            member=user_instance,
            defaults={"preference_date": preference_date}
        )
        mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
        data = {
            'Messages': [{
                "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                "To": [{"Email": user_instance.email, "Name": user_instance.first_name}],
                "Subject": f"Withdrawal Preference Confirmation {preference_date}",
                "HTMLPart": f'''
                <p>Dear <strong>{user_instance.first_name}</strong>,</p>

                <p>
                    This email confirms that your preferred withdrawal date was successfully 
                    set on <strong>{preference_date}</strong>.
                </p>

                <p>
                    Your savings withdrawals will follow the preference date you selected 
                    within your <strong>{settings.DEFAULT_FROM_NAME}</strong> member account.
                </p>

                <p>
                    You can log in to your account at any time to review or update your 
                    withdrawal preference if needed.
                </p>

                <p>
                    If you did not make this change or believe it was done in error, 
                    please contact the administration of 
                    <strong>{settings.DEFAULT_FROM_NAME}</strong> immediately.
                </p>

                <p>
                Kind regards,<br>
                <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
                </p>
                <hr>
                <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
                <p>
                    This email and any attachments are confidential and intended solely 
                    for the named recipient. If you have received this email in error, 
                    please notify the sender and delete it from your system.
                </p>
                '''
            }]
        }

        mailjet.send.create(data=data)
        return redirect(f'/preference_date_successful/{preference_date}')
        
  
@transaction.atomic
@login_required(login_url="/login")
def delete_preference_dateView(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()

        if not username:
            messages.info(request, "Please enter a valid username and date")
            return redirect('/delete_preference_Date')

        try:
            user_instance = User.objects.get(username=username)
            PreferenceDate.objects.filter(member=user_instance).delete()
            return render(request,'members/app_preference_delete_successful.html')
        
        except User.DoesNotExist:
            messages.info(request, "Preference Date could not be remove")
            return redirect('/delete_preference_Date')
