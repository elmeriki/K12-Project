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
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO
import os
from members.models import *

def app_settingView(request):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/app_my_profile.html',context=data)
    else:
        return redirect('/login')

 

def member_listView(request):
    if request.user.is_authenticated:
        members_instance=User.objects.filter( Q(is_member=True,is_staff=False) | Q(is_member=False,is_staff=False) )
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/app_members_list.html',context=data)
    else:
        return redirect('/login')


def transactionsView(request):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/transactions.html',context=data)
    else:
        return redirect('/login')
    


def transactions_detailsView(request):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/transaction_detail.html',context=data)
    else:
        return redirect('/login')
    
    
def activate_accountView(request,select_username):
    if request.user.is_authenticated:
        select_members_instance=User.objects.get(username=select_username)
        data = {
            'select_members_instance':select_members_instance
        }
        return render(request,'members/app_activate_member.html',context=data)
    else:
        return redirect('/login')
    

def member_detailsView(request,select_username):
    if request.user.is_authenticated:
        select_members_instance=User.objects.get(username=select_username)
        data = {
            'select_members_instance':select_members_instance
        }
        return render(request,'members/app_members_details.html',context=data)
    else:
        return redirect('/login')
    
    
@transaction.atomic
def activate_member_accountView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['fname'] and request.POST['lname'] and request.POST['username'] and request.POST['designation']:
        fname=request.POST['fname']
        lname=request.POST['lname']
        username=str(request.POST['username'])
        designation=request.POST['designation']
        position=request.POST['position']
        username_instance = User.objects.get(username=username)
        if designation == "Admin":
            User.objects.filter(username=username_instance).update(membershipTitle=position,is_admin=True,is_member=True)
            
        if designation == "Member":
            User.objects.filter(username=username_instance).update(membershipTitle=position,is_member=True)
        
        messages.info(request,"Member's account has been activated successfuly")
        return redirect(f'/activate_account/{username}')
    else:
        messages.info(request,"Activation process could not be completed")
        return redirect(f'/activate_account/{username}')
    
    
    
@transaction.atomic
def verify_payment_amountView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['amount'] and request.POST['reference']:
        amount=int(request.POST['amount'])
        reference=request.POST['reference']
        username = request.user.username
        username_instance = User.objects.get(username=username)
        data = {
            "amount":amount,
            "reference":reference,
            "username_instance":username_instance
        }
        return render(request,'members/app_process_payment.html',context=data)

    else:
        return render(request,'members/app_process_payment.html',context=data)


@transaction.atomic
def upload_podView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['amount'] and request.POST['reference']:
        amount=int(request.POST['amount'])
        reference=request.POST['reference']
        username = request.user.username
        username_instance = User.objects.get(username=username)
        data = {
            "amount":amount,
            "reference":reference,
            "username_instance":username_instance
        }
        return render(request,'members/app_upload_pods.html',context=data)

    else:
        return render(request,'members/app_upload_pods.html',context=data)
    
    
    
@transaction.atomic
def submite_transactionView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['username'] and request.POST['amount'] and request.POST['reference']:
        amount=int(request.POST['amount'])
        username=request.POST['username']
        reference=request.POST['reference']
        pod=request.FILE['pod']
        username = request.user.username
        username_instance = User.objects.get(username=username)
        
        data = {
            "amount":amount,
            "reference":reference,
            "username":username,
            "username_instance":username_instance
        }
        return render(request,'members/app_upload_pods.html',context=data)

    else:
        return render(request,'members/app_upload_pods.html',context=data)
    
    

@transaction.atomic
def submit_transactionView(request):
    if request.user.is_authenticated and request.user.is_member and request.method == "POST":

        amount = amount=int(request.POST['amount'])
        username = request.POST.get('username')
        reference = request.POST.get('reference')
        pod = request.FILES.get('pod')

        if pod:
            # Validate extension
            allowed_extensions = ['.png', '.jpg', '.jpeg']
            ext = os.path.splitext(pod.name)[1].lower()

            if ext not in allowed_extensions:
                messages.info(request,"Only PNG, JPG, and JPEG files are allowed.")
                return redirect('/upload_pod')

            image = Image.open(pod)

            # Convert PNG with transparency properly
            if image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

            # Optional: resize to reduce size
            max_size = (800, 800)
            image.thumbnail(max_size)

            # Compress image
            buffer = BytesIO()
            image.save(buffer, format="JPEG", quality=60, optimize=True)

            file_name = f"transactions/{username}_{reference}.jpg"
            file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))

            # Save in database
            Transaction.objects.create(
                member=request.user,
                amount=amount,
                transactionReference=reference,
                PODs=file_path,
                transactionType = "Deposit",
                transactionStatus="Initiated"
            )
            data = {
               "amount":amount,
               "transactionReference":reference,
               "transactionStatus": "Initiated",
              "currentDate": date.today().isoformat()
            }
            return render(request,'members/app_deposit_success.html',context=data)

        else:
            messages.info(request,"Uploading POD could not be completed, Please try again")
            return redirect('/upload_pod')
    else:
        messages.info(request,"Uploading POD could not be completed, Please try again")
        return redirect('/upload_pod')