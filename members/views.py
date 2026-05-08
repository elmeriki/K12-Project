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
from decimal import Decimal
from mailjet_rest import Client as MailjetClient  # Alias for the Client class
from datetime import datetime


@login_required(login_url="/login")
def error_404_view(request, exception):
    return render(request, 'members/404.html', status=404)


@login_required(login_url="/login")
def error_500_view(request):
    return render(request, 'members/500.html', status=500)


@login_required(login_url="/login")
def app_settingView(request):
    context = {
        'members_instance': request.user
    }
    return render(request, 'members/app_my_profile.html', context)


# @login_required(login_url="/login")
# def app_settingView(request):
#     if request.user.is_authenticated:
#         username = request.user.username
#         members_instance=User.objects.get(username=username)
#         data = {
#             'members_instance':members_instance
#         }
#         return render(request,'members/app_my_profile.html',context=data)
#     else:
#         return redirect('/login')

 
# @login_required(login_url="/login")
# def member_listView(request):
#     if request.user.is_authenticated and request.user.is_member or request.user.is_admin:
#         members_instance=User.objects.filter(is_member=True)
#         data = {
#             'members_instance':members_instance
#         }
#         return render(request,'members/app_members_list.html',context=data)
#     else:
#         return redirect('/login')

@login_required(login_url="/login")
def member_listView(request):
    if not (request.user.is_member or request.user.is_admin):
        return redirect("/login")
    members_instance = User.objects.filter(is_member=True).only(
        "id", "username", "first_name", "last_name"
    )
    context = {
        "members_instance": members_instance
    }
    return render(request, "members/app_members_list.html", context)

@login_required(login_url="/login")
def unactivated_membersView(request):
    if request.user.is_authenticated and request.user.is_admin:
        members_instance=User.objects.filter(is_member=False)
        data = {
            'members_instance':members_instance
        }
        return render(request,'members/app_members_list.html',context=data)
    else:
        return redirect('/login')

@login_required(login_url="/login")
def transactionsView(request):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        transaction = Transaction.objects.filter(member=members_instance).order_by('-created_at')[:20]
        data = {
            'members_instance':members_instance,
            'transaction':transaction
        }
        return render(request,'members/transactions.html',context=data)
    else:
        return redirect('/login')
    

@login_required(login_url="/login")
def donation_withdrawalView(request):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        withdrawal_transaction = DonationWithdrawal.objects.filter(member=members_instance)
        data = {
            'withdrawal_transaction':withdrawal_transaction
        }
        return render(request,'members/withdrawal_log.html',context=data)
    else:
        return redirect('/login')
    
@login_required(login_url="/login")
def process_donation_withdrawalView(request):
    if request.user.is_authenticated:
        withdrawal_transaction = DonationWithdrawal.objects.filter(donationStatus="Pending").order_by('-created_at')[:20]
        data = {
            'withdrawal_transaction':withdrawal_transaction
        }
        return render(request,'members/withdrawal_log.html',context=data)
    else:
        return redirect('/login')
    
@login_required(login_url="/login")
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
    
@login_required(login_url="/login")
def incoming_paymentView(request):
    if request.user.is_authenticated and request.user.is_admin:
        transaction = Transaction.objects.filter(transactionStatus="Verified" ).order_by('-created_at')[:20]
        data = {
            'transaction':transaction
        }
        return render(request,'members/app_incoming_payment.html',context=data)
    else:
        return redirect('/login')
    
    
@login_required(login_url="/login")
def withdrawalsView(request):
    if request.user.is_authenticated and request.user.is_admin:
        withdrawals = Withdrawal.objects.order_by('-created_at')[:10]
        data = {
            'withdrawals':withdrawals
        }
        return render(request,'members/app_withdrawal.html',context=data)
    else:
        return redirect('/login')
    
    
@login_required(login_url="/login")
def payment_successfulView(request,transactionID):
    if request.user.is_authenticated:
        transactions = Transaction.objects.get(id=transactionID)
        data = {
            'transactions':transactions,
        }
        return render(request,'members/app_deposit_success.html',context=data)
    else:
        return redirect('/login')

# @login_required
# def transfer_successfulView(request,transactionId):
#     if request.user.is_authenticated:
#         username = request.user.username
#         members_instance=User.objects.get(username=username)
#         data = {
#             'members_instance':members_instance,
#         }
#         return render(request,'members/app_transfer_success.html',context=data)
#     else:
#         return redirect('/login')
    
    
@login_required(login_url="/login")
def donation_withdrawal_successfulView(request,withdrawalID):
    if request.user.is_authenticated:
        donation_withdrawal_transaction=DonationWithdrawal.objects.get(id=withdrawalID)
        data = {
            'donation_withdrawal_transaction':donation_withdrawal_transaction,
        }
        return render(request,'members/app_donation_withdrawal_confirmation.html',context=data)
    else:
        return redirect('/login')
    
    
@login_required(login_url="/login")
def withdrawal_successful_confirmationView(request,withdrawalID):
    if request.user.is_authenticated:
        withdrawal_transaction=Withdrawal.objects.get(id=withdrawalID)
        data = {
            'withdrawal_transaction':withdrawal_transaction,
        }
        return render(request,'members/app_withdrawal_confirmation.html',context=data)
    else:
        return redirect('/login')
    
    
@login_required(login_url="/login")
def saving_successfulView(request,transactionId):
    if request.user.is_authenticated:
        selectedSucessfulTransaction=Transaction.objects.get(id=transactionId)
        data = {
            'selectedSucessfulTransaction':selectedSucessfulTransaction,
        }
        return render(request,'members/app_saving_success.html',context=data)
    else:
        return redirect('/login')
    
@login_required(login_url="/login")
def saving_unsuccessfulView(request,transactionId):
    if request.user.is_authenticated:
        selectedSucessfulTransaction=Transaction.objects.get(id=transactionId)
        data = {
            'selectedSucessfulTransaction':selectedSucessfulTransaction,
        }
        return render(request,'members/app_saving_unsuccess.html',context=data)
    else:
        return redirect('/login')

@login_required(login_url="/login")
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

@login_required(login_url="/login")
def withdrawal_detailsView(request,withdrawalID):
    if request.user.is_authenticated:
        username = request.user.username
        members_instance=User.objects.get(username=username)
        select_transaction = Withdrawal.objects.get(id=withdrawalID)
        data = {
            'members_instance':members_instance,
            'select_withdrawal':select_transaction
        }
        return render(request,'members/withdrawal_detail.html',context=data)
    else:
        return redirect('/login')

@login_required(login_url="/login")
def activate_accountView(request,select_username):
    if request.user.is_authenticated:
        select_members_instance=User.objects.get(username=select_username)
        data = {
            'select_members_instance':select_members_instance
        }
        return render(request,'members/app_activate_member.html',context=data)
    else:
        return redirect('/login')
    
@login_required(login_url="/login")
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
@login_required(login_url="/login")
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
        
        mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
        data = {
            'Messages': [{
                "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                "To": [{"Email": username_instance.email, "Name": fname}],
                "Subject": f"{settings.DEFAULT_FROM_NAME} Account Activation Confirmation",
                "HTMLPart": f'''
                <p>Dear <strong>{fname}</strong>,</p>

                <p>
                    We are pleased to inform you that your account with 
                    <strong>{settings.DEFAULT_FROM_NAME}</strong> has been successfully activated.
                </p>
                <p>
                    Your position within the group has been recorded as 
                    <strong>{position}</strong>.
                </p>
                <p>
                    You can now log in to your account and begin using the platform to manage 
                    your savings, transactions, and other member activities.
                </p>
                <p>
                    If you have any questions or require assistance, please feel free to contact the administrator.
                </p>

                <br>
                <p>Kind regards,<br>
                <strong>{settings.DEFAULT_FROM_NAME} Administration</strong></p>
                <br>
                <hr>
                <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
                <p>
                    This email and any attachments are confidential and intended solely for the named recipient. 
                    If you have received this email in error, please notify the sender immediately and delete it 
                    from your system. Unauthorized use, disclosure, or distribution of this message is prohibited.
                </p>
                '''
            }]
        }

        mailjet.send.create(data=data)
        messages.info(request,"Member's account has been activated successfuly")
        return redirect(f'/activate_account/{username}')
    else:
        messages.info(request,"Activation process could not be completed")
        return redirect(f'/activate_account/{username}')
    
    
@transaction.atomic
@login_required(login_url="/login")
def transfer_donation_View(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['selectedDonation'] and request.POST['momoNumber'] and request.POST['momoName'] and request.POST['with_amount']:
        selectedDonationID=request.POST['selectedDonation']
        momoNumber=request.POST['momoNumber']
        momoName=str(request.POST['momoName'])
        with_amount=int(request.POST['with_amount'])
        username_instance = request.user
        donationInstance = Donation.objects.get(id=selectedDonationID)
        selectedTotalDonationAmount = Donation.objects.get(id=selectedDonationID).totalDonationAmount
        if with_amount > selectedTotalDonationAmount:
            messages.info(request,"Request amount is bigger than donation amount")
            return redirect(f'/transfer_donation/{selectedDonationID}')  
        
        if with_amount <= selectedTotalDonationAmount:
            
            newSelectedTotalDonationAmount = Donation.objects.get(id=selectedDonationID).totalDonationAmount - with_amount
            updateDonationAccount = Donation.objects.get(id=selectedDonationID)
            updateDonationAccount.totalDonationAmount = newSelectedTotalDonationAmount
            updateDonationAccount.save()
            
            save_new_donation_withdrawal = DonationWithdrawal(member=username_instance,donation=donationInstance,amount=with_amount,momoName=momoName,momoNumber=momoNumber,donationStatus="Pending")
            save_new_donation_withdrawal.save()
            withdrawalID = save_new_donation_withdrawal.id
            return redirect(f'/donation_withdrawal_sucessful/{withdrawalID}')  
        
        if with_amount < 0:
            messages.info(request,"Enter a valid donation amount bigger than zero")
            return redirect(f'/transfer_donation/{selectedDonationID}')  
    else:
        messages.info(request,"Something went wrong during withdrawal process")
        return redirect('/transfer_donation/{selectedDonationID}')
    
    
@transaction.atomic
def verify_payment_amountView(request):
    if request.user.is_authenticated and request.method == "POST" and request.POST['amount'] and request.POST['reference']:
        amount=int(request.POST['amount'])
        reference=request.POST['reference']
        username = request.user.username
        username_instance = User.objects.get(username=username) 
        depositCountLog = Transaction.objects.filter(member=username_instance,transactionType="Deposit",transactionStatus="Initiated").count()
        data = {
            "amount":amount,
            "reference":reference,
            "username_instance":username_instance,
            "depositCountLog":depositCountLog,
            "kontrimanFloat":settings.KONTRIMAN_MTN_NUMBER
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
    



@login_required(login_url="/login")
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
    transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
    mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
    data = {
        'Messages': [{
            "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
            "To": [{"Email": sender.email, "Name": sender.first_name}],
            "Subject": f"Member Transfer Confirmation {transaction_date}",
            "HTMLPart": f'''
            <p>Dear <strong>{sender.first_name}</strong>,</p>

            <p>
                This email confirms that your transfer within 
                <strong>{settings.DEFAULT_FROM_NAME}</strong> has been successfully completed.
            </p>

            <p>
                The transfer was processed on <strong>{transaction_date}</strong> and the amount has been 
                successfully allocated to the recipient's account.
            </p>

            <p>
                You may log in to your account at any time to review your updated balance or 
                view the transaction details in your transaction log.
            </p>

            <p>
                If you did not authorize this transaction or require further assistance, 
                please contact the administration immediately.
            </p>

            <p>
            Kind regards,<br>
            <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
            </p>
            <hr>

            <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
            <p>
                This email and any attachments are confidential and intended solely for the named recipient. 
                If you received this message in error, please notify the sender and delete it from your system.
            </p>
            '''
        }]
    }

    mailjet.send.create(data=data)
    return redirect(f'/transfer_successful/{recordTransactionForSender.id}/{recordTransactionForReciever.id}')

@login_required(login_url="/login")
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
    
    
@login_required(login_url="/login")
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
    
    
@login_required(login_url="/login")
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

    transaction = Transaction.objects.create(
        member=request.user,
        amount=amount,
        transactionReference=reference,
        PODs=file_path,
        transactionType="Deposit",
        transactionStatus="Initiated"
    )
    transaction_id = transaction.id
    user=request.user
    transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
    mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
    data = {
        'Messages': [{
            "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
            "To": [{"Email":user.email, "Name": user.first_name}],
            "Subject": f"Savings Initiated {transaction_date}",
            "HTMLPart": f'''
            <p>Dear <strong>{user.first_name}</strong>,</p>

            <p>
            This email confirms that your savings request was successfully <strong>INITIATED</strong> on 
            <strong>{transaction_date}</strong>.
            </p>

            <p>
                The transaction is currently <strong>UNDER REVIEW</strong>. Once the verification process 
                has been completed, the amount ({amount} XAF) will be credited to your personal K12 savings account.
            </p>

            <p>
                You will receive another email notification confirming that the funds have been successfully 
                credited to your account.
            </p>

            <p>
                If you have any questions regarding this transaction, please feel free to contact the administrator.
            </p>

            <br>

            <p>
            Kind regards,<br>
            <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
            </p>
            <hr>
            <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
            <p>
                This email and any attachments are confidential and intended solely for the named recipient. 
                If you have received this email in error, please notify the sender immediately and delete it 
                from your system. Unauthorized use, disclosure, or distribution of this message is prohibited.
            </p>
            '''
        }]
    }
    mailjet.send.create(data=data)
    return redirect(f'/payment_successful/{transaction_id}')
    
@login_required(login_url="/login")
@transaction.atomic
def change_profile_pictureView(request):
    if not (request.user.is_authenticated and request.user.is_member and request.method == "POST"):
        messages.info(request, "Uploading Profile Pic could not be completed, Please try again")
        return redirect('/change_photo')
    user = request.user
    profile = request.FILES.get('profile')

    if not profile:
        messages.info(request, "Uploading profile photo could not be completed, Please try again")
        return redirect('/change_photo')

    # Validate extension
    allowed_extensions = ['.png', '.jpg', '.jpeg']
    ext = os.path.splitext(profile.name)[1].lower()

    if ext not in allowed_extensions:
        messages.info(request, "Only PNG, JPG, and JPEG files are allowed.")
        return redirect('/upload_pod')

    image = Image.open(profile)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    max_size = (800, 800)
    image.thumbnail(max_size)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=60, optimize=True)

    file_name = f"transactions/{user.first_name}_{user.last_name}.jpg"
    file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))

    loginUserInstance = User.objects.get(username=user.username)
    loginUserInstance.profilePicture=file_path
    loginUserInstance.save()
    
    return redirect(f'/photo_change_successful')
    
@login_required(login_url="/login")
@transaction.atomic
def final_donation_withdrawalView(request):
    if not (request.user.is_authenticated and request.user.is_admin and request.method == "POST"):
        messages.info(request, "Uploading POD could not be completed, Please try again")
        return redirect('/upload_pod')
    donation_id =  request.POST.get('donation_id')
    donation_title = request.POST.get('donation_title')
    withdrawal_amount = int(request.POST.get('withdrawal_amount', 0))
    reciever_username = request.POST.get('reciever_username')
    pop = request.FILES.get('pop')

    if not pop:
        messages.info(request, "Uploading POP could not be completed, Please try again")
        return redirect('/donation_withdrawal_sucessful/{donation_id}')

    # Validate extension
    allowed_extensions = ['.png', '.jpg', '.jpeg']
    ext = os.path.splitext(pop.name)[1].lower()

    if ext not in allowed_extensions:
        messages.info(request, "Only PNG, JPG, and JPEG files are allowed.")
        return redirect('/donation_withdrawal_sucessful/{donation_id}')

    image = Image.open(pop)

    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    max_size = (800, 800)
    image.thumbnail(max_size)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=60, optimize=True)

    file_name = f"transactions/{donation_title}_{reciever_username}.jpg"
    file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))

    groupMainAccountBalance = Account.objects.get(member=User.objects.get(username=settings.MAIN_GROUP_NUMBER)).mainAccountBalance
    newMainGroupAccountBalance = groupMainAccountBalance - withdrawal_amount
    
    membersSavingsBalance = Account.objects.get(member=User.objects.get(username=reciever_username)).memberBalance
    newMembersSavingsBalance = membersSavingsBalance - withdrawal_amount
    
    updateMainAccountInstance = Account.objects.get(member=User.objects.get(username=settings.MAIN_GROUP_NUMBER))
    updateMainAccountInstance.mainAccountBalance = newMainGroupAccountBalance
    updateMainAccountInstance.save()

    updateMembersAccountInstance = Account.objects.get(member=User.objects.get(username=reciever_username))
    updateMembersAccountInstance.memberBalance = newMembersSavingsBalance
    updateMembersAccountInstance.save()
    
    update_withdrawal_request = DonationWithdrawal.objects.get(id=donation_id)
    update_withdrawal_request.donationStatus = "Completed"
    update_withdrawal_request.PODs=file_path
    update_withdrawal_request.save()
    
    create_newTransaction = Transaction(member=User.objects.get(username=reciever_username),amount=withdrawal_amount,transactionType="Donx Withdrawal",transactionReference="Donx Withdrawal",transactionStatus="Successful",PODs=file_path)
    create_newTransaction.save()
    
    return redirect(f'/donation_withdrawal_successful_confirmation/{donation_id}')


@login_required(login_url="/login")
@transaction.atomic
def finalise_withdrawalView(request):
    if not (request.user.is_authenticated and request.user.is_admin and request.method == "POST"):
        messages.info(request, "Uploading POP could not be completed, Please try again")
        withdrawal_id =  request.POST.get('withdrawal_id')
        return redirect(f'/process_withdrawal_request/{withdrawal_id}')
    
    withdrawal_id =  request.POST.get('withdrawal_id')
    membersUsername = request.POST.get('membersUsername')
    recieverMomoName = request.POST.get('recieverMomoName')
    recieverMomoNumber = request.POST.get('recieverMomoNumber')
    withdrawal_amount = int(request.POST.get('withdrawal_amount', 0))
    withdrawalStatus = request.POST.get('withdrawalStatus')
    decision = request.POST.get('decision')
    pop = request.FILES.get('pop')

    if not pop:
        messages.info(request, "Uploading POP could not be completed, Please try again")
        return redirect('/process_withdrawal_request/{withdrawal_id}')

    
    # Validate extension
    allowed_extensions = ['.png', '.jpg', '.jpeg']
    ext = os.path.splitext(pop.name)[1].lower()

    if ext not in allowed_extensions:
        messages.info(request, "Only PNG, JPG, and JPEG files are allowed.")
        return redirect('/process_withdrawal_request/{withdrawal_id}')
    if decision == "Successful":
        image = Image.open(pop)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        max_size = (800, 800)
        image.thumbnail(max_size)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=60, optimize=True)

        file_name = f"withdrawal/{membersUsername}_{decision}.jpg"
        file_path = default_storage.save(file_name, ContentFile(buffer.getvalue()))

        groupMainAccountBalance = Account.objects.get(member=User.objects.get(username=settings.MAIN_GROUP_NUMBER)).mainAccountBalance
        newMainGroupAccountBalance = groupMainAccountBalance - withdrawal_amount
        
        membersSavingsBalance = Account.objects.get(member=User.objects.get(username=membersUsername)).memberBalance
        newMembersSavingsBalance = membersSavingsBalance - withdrawal_amount
        
        updateMainAccountInstance = Account.objects.get(member=User.objects.get(username=settings.MAIN_GROUP_NUMBER))
        updateMainAccountInstance.mainAccountBalance = newMainGroupAccountBalance
        updateMainAccountInstance.save()

        updateMembersAccountInstance = Account.objects.get(member=User.objects.get(username=membersUsername))
        updateMembersAccountInstance.memberBalance = newMembersSavingsBalance
        updateMembersAccountInstance.save()
        
        update_withdrawal_request = Withdrawal.objects.get(id=withdrawal_id)
        update_withdrawal_request.withdrawalStatus = "Successful"
        update_withdrawal_request.POPs=file_path
        update_withdrawal_request.save()
        
        create_newTransaction = Transaction(member=User.objects.get(username=membersUsername),amount=withdrawal_amount,transactionType="Withdrawal",transactionReference="Withdrawal",transactionStatus="Successful",PODs=file_path)
        create_newTransaction.save()
        return redirect(f'/withdrawal_successful_confirmation/{withdrawal_id}')
    
    if decision == "Fraud" or decision == "Rejected":
        update_withdrawal_request = Withdrawal.objects.get(id=withdrawal_id)
        update_withdrawal_request.withdrawalStatus = decision
        update_withdrawal_request.POPs=file_path
        update_withdrawal_request.save()
        
        create_newTransaction = Transaction(member=User.objects.get(username=membersUsername),amount=withdrawal_amount,transactionType="Withdrawal",transactionReference="Withdrawal",transactionStatus=decision,PODs=file_path)
        create_newTransaction.save()
        return redirect(f'/withdrawal_successful_confirmation/{withdrawal_id}') 

    
@login_required(login_url="/login")
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
    
@login_required(login_url="/login")
def donationsView(request):
    if request.user.is_authenticated:
        donations_list=Donation.objects.filter()
        data = {
            'donations_list':donations_list
        }
        return render(request,'members/app_donations.html',context=data)
    else:
        return redirect('/login')
    
@login_required(login_url="/login")
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
    
    
@login_required(login_url="/login")
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
   
   
@login_required(login_url="/login")
@transaction.atomic
def close_donationView(request,donationId):
    if request.user.is_authenticated:
        Donation.objects.filter(id=donationId).update(donationStatus="Completed")
        return redirect(f'/verify_donation_confirmation/{donationId}')
    else:
       return redirect(f'/verify_donation_confirmation/{donationId}') 


@login_required(login_url="/login")
@transaction.atomic
def make_donationView(request,donationId):
    if request.user.is_authenticated:
        donation_instance = Donation.objects.get(id=donationId)
        user = request.user
        membersBalance = Account.objects.filter(member=user).values_list('memberBalance', flat=True).first()
        onGoingDonationCheck = DonationTransaction.objects.filter(donation=donation_instance,member=user).count()
        data = {
            "membersBalance":membersBalance,
            "donation_instance":donation_instance,
            'donationId':donationId,
            'onGoingDonationCheck':onGoingDonationCheck
        }
        return render(request,'members/app_make_donation.html',context=data)
    else:
        return render(request,'members/app_make_donation.html',context=data)
    
@login_required(login_url="/login")
@transaction.atomic
def transferView(request):
    if request.user.is_authenticated:
        return render(request,'members/app_transfer.html')
    else:
        return render(request,'members/app_transfer.html')
    

@login_required(login_url="/login")
@transaction.atomic
def transfer_donationView(request,donationID):
    if request.user.is_authenticated:
        userInstance = request.user
        data = {
            "donations":Donation.objects.filter(member=userInstance)
        }
        return render(request,'members/app_transfer_donation.html',context=data)
    else:
        return render(request,'members/app_transfer_donation.html')
    
@login_required(login_url="/login")
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
            return redirect(f'/make_donation/{donationInstance.id}')
        
        if not request.POST.get('reference'):
            messages.info(request, "Enter a valid donation reference")
            return redirect(f'/make_donation/{donationInstance.id}')
        
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
            donationTransaction_id =recordAsDonation.id
            transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
            mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
            data = {
                'Messages': [{
                    "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                    "To": [{"Email": member_instance.email, "Name":member_instance.first_name}],
                    "Subject": f"Donation Payment Confirmation {transaction_date}",
                    "HTMLPart": f'''
                    <p>Dear <strong>{member_instance.first_name}</strong>,</p>

                    <p>
                        Thank you for your generous contribution. This email confirms that your 
                        donation has been successfully received on <strong>{transaction_date}</strong>.
                    </p>

                    <p>
                        Your support is greatly appreciated and helps strengthen the activities 
                        and initiatives of <strong>{settings.DEFAULT_FROM_NAME}</strong>.
                    </p>

                    <p>
                        You may log in to your account at any time to review your donation record 
                        and transaction history.
                    </p>

                    <p>
                        If you have any questions regarding this payment, please feel free to contact the administration.
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
            return redirect(f'/donation_sucessful/{donationTransaction_id}')

    else:
        messages.info(request,"Enter valid donation amount and reference.")
        return redirect(f'/make_donation/{donationId}')
    
    
    
@login_required(login_url="/login")
def donation_sucessfulView(request,donationId):
    if request.user.is_authenticated:
        donationTransaction = DonationTransaction.objects.get(id=donationId)
        data = {
            'donationTransaction':donationTransaction,
        }
        return render(request,'members/app_donation_success.html',context=data)
    else:
        return redirect('/login')

@login_required(login_url="/login")
def donation_withdrawal_sucessfulView(request,withdrawalID):
    if request.user.is_authenticated:
        donationwithdrawalTransaction = DonationWithdrawal.objects.get(id=withdrawalID)
        data = {
            'donationwithdrawalTransaction':donationwithdrawalTransaction,
        }
        return render(request,'members/app_donation_withdrawal_success.html',context=data)
    else:
        return redirect('/login')
    
    
@login_required(login_url="/login")
def process_withdrawal_requestView(request,withdrawalID):
    if request.user.is_authenticated:
        withdrawalTransaction = Withdrawal.objects.get(id=withdrawalID)
        data = {
            'withdrawalTransaction':withdrawalTransaction,
        }
        return render(request,'members/app_process_withdrawal.html',context=data)
    else:
        return redirect('/login')
    
    
@login_required(login_url="/login")
def withdrawal_successView(request,withdrawalID):
    if request.user.is_authenticated:
        withdrawalTransaction = Withdrawal.objects.get(id=withdrawalID)
        data = {
            'withdrawalTransaction':withdrawalTransaction,
        }
        return render(request,'members/app_withdrawal_success.html',context=data)
    else:
        return redirect('/login')
    

@login_required(login_url="/login")
def transfer_successfulView(request,sendersID,recieverID):
    if request.user.is_authenticated:
        recieverInstance = Transaction.objects.get(id=recieverID)
        senderInstance = Transaction.objects.get(id=sendersID)
        data = {
            'recieverInstance':recieverInstance,
            'senderInstance':senderInstance
        }
        return render(request,'members/app_transfer_success.html',context=data)
    else:
        return redirect('/login')

@login_required(login_url="/login")
def photo_change_successfulView(request):
    if request.user.is_authenticated:
        return render(request,'members/app_change_photo_success.html')
    else:
        return redirect('/login')
    
@login_required(login_url="/login")
def make_withdrawalView(request):
    loginUserInstance = request.user
    memberBalance = Account.objects.get(member=loginUserInstance).memberBalance
    try:
        preferenceDate = PreferenceDate.objects.get(member=loginUserInstance)
    except PreferenceDate.DoesNotExist:
        preferenceDate = None  # or set a default value
    data = {
        'memberBalance': memberBalance,
        'preferenceDate': preferenceDate,
        'currentdate': date.today()
    }
    return render(request, 'members/app_make_withdrawal.html', context=data)
    
    
@login_required(login_url="/login")
def reconcile_transactionView(request,transactionId):
    if request.user.is_authenticated:
        selectedTransactionToReconcile=Transaction.objects.get(id=transactionId)
        data = {
            'selectedTransactionToReconcile':selectedTransactionToReconcile
        }
        return render(request,'members/app_reconcile_payment.html',context=data)
    else:
        return redirect('/login')
    
    
    
@login_required(login_url="/login")
@transaction.atomic
def reconcile_transaction_View(request,transactionId):
    if request.user.is_authenticated and request.method == "POST" and request.POST['username'] and request.POST['amount'] and request.POST['reference'] and request.POST['decision']:
        amount=int(request.POST['amount'])
        username=request.POST['username']
        reference=request.POST['reference']
        decision=request.POST['decision']
        
        if decision == "Verified":
            member_instance = User.objects.get(username=username)
            mainGroup_instance = User.objects.get(username=settings.MAIN_GROUP_NUMBER)

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
            
            mailjet = MailjetClient(auth=(settings.MAILJET_API_KEY, settings.MAILJET_API_SECRET), version='v3.1')
            transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
            data = {
                'Messages': [{
                    "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                    "To": [{"Email": member_instance.email, "Name": member_instance.first_name}],
                    "Subject": f"Savings Transaction Successful {transaction_date}",
                    "HTMLPart": f'''
                    <p>Dear <strong>{member_instance.first_name}</strong>,</p>

                    <p>
                        We are pleased to inform you that your savings transaction has been successfully 
                        received by the BANK and credited to your account on <strong>{transaction_date}</strong>.
                    </p>

                    <p>
                        You can log in to your account to confirm that the amount has been allocated to your savings balance 
                        or check the transaction log for details.
                    </p>

                    <p>
                        Thank you for using <strong>{settings.DEFAULT_FROM_NAME}</strong> to manage your savings. 
                        Your continued commitment helps strengthen our community of members.
                    </p>

                    <p>
                    Kind regards,<br>
                    <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
                    </p>
                    <hr>
                    <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
                    <p>
                        This email and any attachments are confidential and intended solely for the named recipient. 
                        If you have received this email in error, please notify the sender immediately and delete it from your system. 
                        Unauthorized use, disclosure, or distribution of this message is prohibited.
                    </p>
                    '''
                }]
            }
            mailjet.send.create(data=data)
            return redirect(f'/saving_successful/{transactionId}')
        
        if decision == "Rejected" or decision == "Fraud":
            membersTransactionUpdate = Transaction.objects.get(id=transactionId)
            membersTransactionUpdate.transactionStatus=decision
            membersTransactionUpdate.save()
            
            transaction_date = datetime.now().strftime("%d %B %Y, %H:%M")
            
            data = {
                'Messages': [{
                    "From": {"Email": settings.DEFAULT_FROM_EMAIL, "Name": settings.DEFAULT_FROM_NAME},
                    "To": [{"Email": member_instance.email, "Name": member_instance.first_name}],
                    "Subject": f"{transaction_date} Transaction {decision} Notification",
                    "HTMLPart": f'''
                    <p>Dear <strong>{member_instance.first_name}</strong>,</p>

                    <p>
                        We wish to inform you that your savings transaction initiated on 
                        <strong>{transaction_date}</strong> has been marked as <strong>{decision}</strong>.
                    </p>
                    <p>
                        This means that the transaction will not be credited to your account at this time. 
                        Please review your transaction details and contact the administration if you believe this decision is in error.
                    </p>

                    <p>
                        You can log in to your account to view the transaction log for more details.
                    </p>
                    <p>
                        Thank you for your attention to this matter.
                    </p>

                    <p>
                    Kind regards,<br>
                    <strong>{settings.DEFAULT_FROM_NAME} Administration</strong>
                    </p>
                    <hr>
                    <p><strong>CONFIDENTIALITY NOTICE:</strong></p>
                    <p>
                        This email and any attachments are confidential and intended solely for the named recipient. 
                        If you have received this email in error, please notify the sender immediately and delete it from your system. 
                        Unauthorized use, disclosure, or distribution of this message is prohibited.
                    </p>
                    '''
                }]
            }
            mailjet.send.create(data=data)
            return redirect(f'/saving_unsuccessful/{transactionId}')
    else:
        messages.info(request,"Payment could not be reconcile")
        return redirect(f'/reconcile_transaction/{transactionId}')
    
    
    
    
@login_required(login_url="/login")
@transaction.atomic
def finalise_make_withdrawalView(request):
    if not (request.user.is_authenticated and request.user.is_member and request.method == "POST"):
        messages.info(request, "The withdrawal process could not be completed")
        return redirect('/make_withdrawal')
    
    memberBalance = Decimal(request.POST.get('memberBalance'))
    username =  request.POST.get('username')
    recievingMomo = request.POST.get('recievingMomo')
    recievingMomoName = request.POST.get('recievingMomoName')
    withdrawal_amount = int(request.POST.get('withdrawal_amount', 0))
    userInstance = User.objects.get(username=username)
    
    if withdrawal_amount > memberBalance:
        messages.info(request, "Insufficient Fund to complete withdrawal")
        return redirect('/make_withdrawal')
    
    if withdrawal_amount <= 0:
        messages.info(request, "Enter value greater than zero")
        return redirect('/make_withdrawal')
    
    if withdrawal_amount <= memberBalance:
        create_new_withdrawal_log = Withdrawal(member=userInstance,amount=withdrawal_amount,momoName=recievingMomoName,momoNumber=recievingMomo,withdrawalStatus="Initiated",transactionType="Withdrawal")
        create_new_withdrawal_log.save()
        
        create_newTransactionLog = Transaction(member=userInstance,amount=withdrawal_amount,transactionType="Withdrawal",transactionReference="Withdrawal",transactionStatus="Initiated")
        create_newTransactionLog.save()
        
        withdrawalID = create_new_withdrawal_log.id
        return redirect(f'/withdrawal_success/{withdrawalID}')
    
    
    
    
@login_required(login_url="/login")
def pod_previewView(request,transactionID):
    if request.user.is_authenticated:
        data = {
            "select_transaction": Transaction.objects.get(id=transactionID)
        }
        return render(request,'members/app_pod_preview.html',context=data)
    else:
        return render(request,'members/app-pod-preview.html')
