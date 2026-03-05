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
from django.conf import settings
from django.db.models import F


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
    if request.user.is_authenticated and request.user.is_member or request.user.is_admin:
        members_instance=User.objects.filter( Q(is_member=True,is_staff=False) | Q(is_member=False,is_staff=False) )
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/app_members_list.html',context=data)

    else:
        return redirect('/login')

def unactivated_membersView(request):
    if request.user.is_authenticated and request.user.is_admin:
        members_instance=User.objects.filter(is_member=False,is_staff=False)
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
        transaction = Transaction.objects.filter(member=members_instance)
        data = {
            'members_instance':members_instance,
            'transaction':transaction
        }
        return render(request,'members/transactions.html',context=data)
    else:
        return redirect('/login')
    
    
def donations_logView(request,donationId):
    if request.user.is_authenticated:
        donationInstance=Donation.objects.get(id=donationId)
        transaction = DonationTransaction.objects.filter(donation=donationInstance)
        data = {
            'transaction':transaction
        }
        return render(request,'members/app_donations_log.html',context=data)
    else:
        return redirect('/login')
    

def incoming_paymentView(request):
    if request.user.is_authenticated and request.user.is_admin:
        transaction = Transaction.objects.filter(transactionStatus="Verified")[:10]
        data = {
            'transaction':transaction
        }
        return render(request,'members/app_incoming_payment.html',context=data)
    else:
        return redirect('/login')

def payment_successfulView(request,amount,transactionReference):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        data = {
            'members_instance':members_instance,
            'amount':amount,
            'transactionReference':transactionReference,
        }
        return render(request,'members/app_deposit_success.html',context=data)
    else:
        return redirect('/login')
    
def transfer_successfulView(request,transactionId):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        data = {
            'members_instance':members_instance,
        }
        return render(request,'members/app_transfer_success.html',context=data)
    else:
        return redirect('/login')
    
    
def saving_successfulView(request,transactionId):
    if request.user.is_authenticated:
        selectedSucessfulTransaction=Transaction.objects.get(id=transactionId)
        data = {
            'selectedSucessfulTransaction':selectedSucessfulTransaction,
        }
        return render(request,'members/app_saving_success.html',context=data)
    else:
        return redirect('/login')
    
    
def saving_unsuccessfulView(request,transactionId):
    if request.user.is_authenticated:
        selectedSucessfulTransaction=Transaction.objects.get(id=transactionId)
        data = {
            'selectedSucessfulTransaction':selectedSucessfulTransaction,
        }
        return render(request,'members/app_saving_unsuccess.html',context=data)
    else:
        return redirect('/login')

def transactions_detailsView(request,transactionid):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        select_transaction = Transaction.objects.get(id=transactionid)
        data = {
            'members_instance':members_instance,
            'select_transaction':select_transaction
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
        registrationAmount=int(request.POST['registrationAmount'])
        username_instance = User.objects.get(username=username)
        if designation == "Admin":
            User.objects.filter(username=username_instance).update(membershipTitle=position,is_admin=True)
            
        if designation == "Member":
            User.objects.filter(username=username_instance).update(membershipTitle=position,is_member=True)
            
        mainGroup_instance = User.objects.get(username=settings.MAIN_GROUP_NUMBER)
        Account.objects.filter(member=mainGroup_instance).update(
        mainAccountBalance=F('mainAccountBalance') + registrationAmount)
        
        account = Account.objects.get(member=username_instance)
        account.registrationAmount = registrationAmount
        account.save()
        
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
def verify_fund_transferView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['amount'] and request.POST['username']:
        amount=int(request.POST['amount'])
        userToRecieveMoney=request.POST['username']
        
        if not User.objects.filter(username=userToRecieveMoney).exists():
            messages.info(request,"Members phone number is not VALID")
            return redirect('/transfer')
        
        senderInstanceBalance = Account.objects.get(member=request.user).memberBalance
        if amount > senderInstanceBalance:
            messages.info(request,"Insufficient Balance to complete transaction")
            return redirect('/transfer')
        
        if amount < 0:
            messages.info(request,"Enter a valid amount")
            return redirect('/transfer')
        
        if amount <= senderInstanceBalance:
            username = request.user.username
            data = {
                "RecieveInstance":User.objects.get(username=userToRecieveMoney),
                "sendingInstance":User.objects.get(username=username),
                "amount":amount,
                "userToRecieveMoney":userToRecieveMoney,
            }
            return render(request,'members/app_confirm_transfer.html',context=data)

    else:
        return redirect('/transfer')
    
    
# @transaction.atomic
# def finalise_transferView(request):
#     if request.user.is_authenticated and request.method == "POST" and request.POST['amount'] and request.POST['username']:
#         amount=int(request.POST['amount'])
#         memberToRecieveMoney=request.POST['username']
#         username = request.user.username
#         RecieverInstance = User.objects.get(username=memberToRecieveMoney)
#         sendingInstance = User.objects.get(username=username)
#         RecieverInstanceBalance = Account.objects.filter(member=RecieverInstance).values_list('memberBalance', flat=True).first()
#         senderInstanceBalance = Account.objects.filter(member=sendingInstance).values_list('memberBalance', flat=True).first()
       
#         if amount > senderInstanceBalance:
#             messages.info(request,"Insufficient Funds")
#             return redirect('/verify_fund_transfer')
        
#         if senderInstanceBalance < amount:
#             newSendersAccountBalance = senderInstanceBalance - amount
#             newReceieversAccountBalance = RecieverInstanceBalance + amount
            
#             updateSendersAccount = Account.objects.get(member=sendingInstance)
#             updateSendersAccount.memberBalance = newSendersAccountBalance
#             updateSendersAccount.save()
            
#             updateRecieversAccount = Account.objects.get(member=RecieverInstance)
#             updateRecieversAccount.memberBalance = newReceieversAccountBalance
#             updateRecieversAccount.save()
            
#             data = {
#                "sendingInstance":sendingInstance,
#                 "RecieverInstance":RecieverInstance
#             }
#             return render(request,'members/app_transfer_success.html',context=data)
#     else:
#         return redirect('/verify_fund_transfer')


@transaction.atomic
def finalise_transferView(request):
    if not request.user.is_authenticated or request.method != "POST":
        return redirect('/verify_fund_transfer')

    amount = request.POST.get('amount')
    receiver_username = request.POST.get('username')

    if not amount or not receiver_username:
        messages.info(request, "Invalid transfer request")
        return redirect('/verify_fund_transfer')

    try:
        amount = int(amount)
        sender = request.user
        receiver = User.objects.get(username=receiver_username)
        
    except (ValueError, User.DoesNotExist):
        messages.info(request, "Invalid user or amount")
        return redirect('/verify_fund_transfer')

    if sender.id == receiver.id:
        messages.info(request, "You cannot transfer money to yourself")
        return redirect('/verify_fund_transfer')

    sender_account = Account.objects.select_for_update().get(member=sender)
    receiver_account = Account.objects.select_for_update().get(member=receiver)

    if sender_account.memberBalance < amount:
        messages.info(request, "Insufficient Funds")
        return redirect('/verify_fund_transfer')

    # Perform transfer
    sender_account.memberBalance -= amount
    receiver_account.memberBalance += amount

    sender_account.save()
    receiver_account.save()

    recordTransactionForSender=Transaction(member=sender,amount=amount,transactionType="Transfer",transactionReference="Transfer",transactionStatus="Successful")
    recordTransactionForSender.save()
    
    recordTransactionForReciever=Transaction(member=receiver,amount=amount,transactionType="Recieving",transactionReference="Incoming",transactionStatus="Successful")
    recordTransactionForReciever.save()
    
    data = {
        "sendingInstance": sender,
        "RecieverInstance": receiver
    }

    return render(request, 'members/app_transfer_success.html', context=data)

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
    
    

# @transaction.atomic
# def submit_transactionView(request):
#     if request.user.is_authenticated and request.user.is_member and request.method == "POST":

#         amount = amount=int(request.POST['amount'])
#         username = request.POST.get('username')
#         reference = request.POST.get('reference')
#         pod = request.FILES.get('pod')

#         if pod:
#             # Validate extension
#             allowed_extensions = ['.png', '.jpg', '.jpeg']
#             ext = os.path.splitext(pod.name)[1].lower()

#             if ext not in allowed_extensions:
#                 messages.info(request,"Only PNG, JPG, and JPEG files are allowed.")
#                 return redirect('/upload_pod')

#             image = Image.open(pod)

#             # Convert PNG with transparency properly
#             if image.mode in ("RGBA", "P"):
#                 image = image.convert("RGB")

#             # Optional: resize to reduce size
#             max_size = (800, 800)
#             image.thumbnail(max_size)

#             # Compress image
#             buffer = BytesIO()
#             image.save(buffer, format="JPEG", quality=60, optimize=True)

#             file_name = f"transactions/{username}_{reference}.jpg"
#             file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))
            
#             # Save in database
#             Transaction.objects.create(
#                 member=request.user,
#                 amount=amount,
#                 transactionReference=reference,
#                 PODs=file_path,
#                 transactionType = "Deposit",
#                 transactionStatus="Initiated"
#             )
#             return redirect(f'/payment_successful/{amount}/{reference}')
#         else:
#             messages.info(request,"Uploading POD could not be completed, Please try again")
#             return redirect('/upload_pod')
#     else:
#         messages.info(request,"Uploading POD could not be completed, Please try again")
#         return redirect('/upload_pod')
    
    
@transaction.atomic
def submit_transactionView(request):
    if not (request.user.is_authenticated and request.user.is_member and request.method == "POST"):
        messages.info(request, "Uploading POD could not be completed, Please try again")
        return redirect('/upload_pod')

    amount = int(request.POST.get('amount', 0))
    username = request.POST.get('username')
    reference = request.POST.get('reference', '').strip()
    pod = request.FILES.get('pod')

    if not reference:
        messages.info(request, "Enter a valid reference")
        return redirect('/upload_pod')

    if not pod:
        messages.info(request, "Uploading POD could not be completed, Please try again")
        return redirect('/upload_pod')

    # Validate extension
    allowed_extensions = ['.png', '.jpg', '.jpeg']
    ext = os.path.splitext(pod.name)[1].lower()

    if ext not in allowed_extensions:
        messages.info(request, "Only PNG, JPG, and JPEG files are allowed.")
        return redirect('/upload_pod')

    image = Image.open(pod)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    max_size = (800, 800)
    image.thumbnail(max_size)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=60, optimize=True)

    file_name = f"transactions/{username}_{reference}.jpg"
    file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))

    Transaction.objects.create(
        member=request.user,
        amount=amount,
        transactionReference=reference,
        PODs=file_path,
        transactionType="Deposit",
        transactionStatus="Initiated")

    return redirect(f'/payment_successful/{amount}/{reference}')
    
    
def new_donationView(request):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/app_new_donation.html',context=data)
    else:
        return redirect('/login')
    
def donationsView(request):
    if request.user.is_authenticated:
        donations_list=Donation.objects.filter()
        data = {
            'donations_list':donations_list
        }
        return render(request,'members/app_donations.html',context=data)
    else:
        return redirect('/login')
    
@transaction.atomic
def create_new_donationView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['username'] and request.POST['title'] and request.POST['description'] and request.POST['amount']:
        username=request.POST['username']
        amount=int(request.POST['amount'])
        title=request.POST['title']
        description=request.POST['description']
        username_instance = User.objects.get(username=username)
        
        user = User.objects.filter(username=username).first()
        if not user:
            messages.info(request, "No user found with this username.")
            return redirect('/new_donation')
        
        if Donation.objects.filter(member=username_instance,donationStatus="Pending").exists():
            messages.info(request,"This member is having a pending donation")
            return redirect('/new_donation')
        
        create_new_donationView =Donation(member=username_instance,donationType=title,description=description,donationStatus="Pending",minDonationAmount=amount)
        if create_new_donationView:
            create_new_donationView.save()
            messages.info(request,"New Donation has been created successfully")
            return redirect('/new_donation')
        else:
            messages.info(request,"New Donation could not be created")
            return redirect('/new_donation')
    else:
        messages.info(request,"New Donation could not be created")
        return redirect('/new_donation')
    
    
    
@transaction.atomic
def verify_donation_confirmationView(request,donationId):
    if request.user.is_authenticated:
        donation_instance = Donation.objects.get(id=donationId)
        data = {
            "donation_instance":donation_instance
        }
        return render(request,'members/app_donation_confirmation.html',context=data)

    else:
        return render(request,'members/app_donation_confirmation.html',context=data)
    


@transaction.atomic
def make_donationView(request,donationId):
    if request.user.is_authenticated:
        donation_instance = Donation.objects.get(id=donationId)
        username = request.user.username
        username_instance = User.objects.get(username=username)
        membersBalance = Account.objects.filter(member=username_instance).values_list('memberBalance', flat=True).first()

        data = {
            "membersBalance":membersBalance,
            "donation_instance":donation_instance,
            'donationId':donationId
        }
        return render(request,'members/app_make_donation.html',context=data)

    else:
        return render(request,'members/app_make_donation.html',context=data)
    
@transaction.atomic
def transferView(request):
    if request.user.is_authenticated:
        return render(request,'members/app_transfer.html')
    else:
        return render(request,'members/app_transfer.html')
    
@transaction.atomic
def make_donation_View(request,donationId):
    if request.user.is_authenticated and request.method == "POST" and request.POST['donationAmount'] and request.POST['reference']:
        donationAmount=int(request.POST['donationAmount'])
        reference = request.POST.get('reference')
        donationInstance = Donation.objects.get(id=donationId)
        username = request.user.username
        member_instance = User.objects.get(username=username)
        membersBalance = Account.objects.filter(member=member_instance).values_list('memberBalance', flat=True).first()

        if donationAmount > membersBalance:
            messages.info(request, "Insufficient account balance to process the donation")
            return redirect(f'/make_donation/{donationId}')
        
        if not request.POST.get('reference'):
            messages.info(request, "Enter a valid donation reference")
            return redirect(f'/make_donation/{donationId}')
        
        if membersBalance >= donationAmount:
            newMembersBalance = membersBalance - donationAmount
            Account.objects.filter(member=member_instance).update(memberBalance=newMembersBalance)
            
            donationBalance =Donation.objects.filter(id=donationId).values_list('totalDonationAmount', flat=True).first()
            newDonationBalance = donationBalance + donationAmount
            Donation.objects.filter(id=donationId).update(totalDonationAmount=newDonationBalance)
            
            recordAsTransaction=Transaction(member=member_instance,amount=donationAmount,transactionType="Donation",transactionReference=reference,transactionStatus="Successful")
            recordAsTransaction.save()
            
            recordAsDonation=DonationTransaction(member=member_instance,donation=donationInstance,amount=donationAmount,reference=reference,donationStatus="Successful")
            recordAsDonation.save()
            
            return redirect(f'/donation_sucessful/{donationId}')
        else:
            messages.info(request,"Donation could not be process")
            return redirect(f'/make_donation/{donationId}')
    else:
        messages.info(request,"Donation could not be process")
        return redirect(f'/make_donation/{donationId}')
    
    
    
def donation_sucessfulView(request,donationId):
    if request.user.is_authenticated:
        donationTransaction = DonationTransaction.objects.get(id=donationId)
        data = {
            'donationTransaction':donationTransaction,
        }
        return render(request,'members/app_donation_success.html',context=data)
    else:
        return redirect('/login')
    
    
    
def reconcile_transactionView(request,transactionId):
    if request.user.is_authenticated:
        selectedTransactionToReconcile=Transaction.objects.get(id=transactionId)
        data = {
            'selectedTransactionToReconcile':selectedTransactionToReconcile
        }
        return render(request,'members/app_reconcile_payment.html',context=data)
    else:
        return redirect('/login')
    
    
    
@transaction.atomic
def reconcile_transaction_View(request,transactionId):
    if request.user.is_authenticated and request.method == "POST" and request.POST['username'] and request.POST['amount'] and request.POST['reference'] and request.POST['decision']:
        amount=int(request.POST['amount'])
        username=request.POST['username']
        reference=request.POST['reference']
        decision=request.POST['decision']
        
        if decision == "Verified":
            member_instance = User.objects.get(username=username)
            mainGroup_instance = User.objects.get(username="650065763")

            membersBalance = Account.objects.filter(member=member_instance).values_list('memberBalance', flat=True).first()
            mainAccountBalance = Account.objects.filter(member=mainGroup_instance).values_list('mainAccountBalance',flat=True).first()
            newMainAccountBalance = mainAccountBalance + amount
            newMembersBalance = membersBalance + amount
            
            membersAccount = Account.objects.get(member=member_instance)
            membersAccount.memberBalance = newMembersBalance
            membersAccount.save()
            
            groupAccount = Account.objects.get(member=mainGroup_instance)
            groupAccount.mainAccountBalance = newMainAccountBalance
            groupAccount.save()
            
            membersTransactionUpdate = Transaction.objects.get(id=transactionId)
            membersTransactionUpdate.transactionStatus=decision
            membersTransactionUpdate.save()
            return redirect(f'/saving_successful/{transactionId}')
        
        if decision == "Rejected" or decision == "Fraud":
            membersTransactionUpdate = Transaction.objects.get(id=transactionId)
            membersTransactionUpdate.transactionStatus=decision
            membersTransactionUpdate.save()
            return redirect(f'/saving_unsuccessful/{transactionId}')
    else:
        messages.info(request,"Payment could not be reconcile")
        return redirect(f'/reconcile_transaction/{transactionId}')