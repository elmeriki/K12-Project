from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser
from k12auth.models import *


# Create your models here.
class Account(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    memberBalance=  models.DecimalField(max_digits=11,decimal_places=2,default=0,blank=True,null=True)
    troubleFundsBalance=  models.DecimalField(max_digits=11,decimal_places=2,default=0,blank=True,null=True)
    mainAccountBalance=  models.DecimalField(max_digits=11,decimal_places=2,default=0,blank=True,null=True)
    registrationAmount=  models.DecimalField(max_digits=11,decimal_places=2,default=0,blank=True,null=True)
    accountNumber = models.CharField(max_length=200,default=0,null=True,blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return self.member.first_name
        
    class Meta:
        verbose_name_plural = "Members Account"
        
# Create your models here.
class Transaction(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    amount=models.DecimalField(max_digits=11,decimal_places=0,default=0,blank=True,null=True)
    transactionType = models.CharField(max_length=200,default=0,null=True,blank=True)
    transactionReference = models.CharField(max_length=200,default="0",null=True,blank=True)
    transactionStatus = models.CharField(max_length=200,default="0",null=True,blank=True)
    PODs = models.FileField(upload_to="POD/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class Donation(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    donationType = models.CharField(max_length=250,default="0",null=True,blank=True)
    description = models.CharField(max_length=250,default="0",null=True,blank=True)
    donationStatus = models.CharField(max_length=250,default="0",null=True,blank=True)
    totalDonationAmount=models.DecimalField(max_digits=11,decimal_places=0,default=0,blank=True,null=True)
    minDonationAmount=models.DecimalField(max_digits=11,decimal_places=0,default=0,blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class DonationTransaction(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    donation = models.ForeignKey(Donation,on_delete=models.CASCADE,null=True,blank=True)
    amount=models.DecimalField(max_digits=11,decimal_places=0,default=0,blank=True,null=True)
    reference = models.CharField(max_length=250,default="0",null=True,blank=True)
    donationStatus = models.CharField(max_length=250,default="0",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class DonationWithdrawal(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    donation = models.ForeignKey(Donation,on_delete=models.CASCADE,null=True,blank=True)
    amount=models.DecimalField(max_digits=11,decimal_places=0,default=0,blank=True,null=True)
    momoName = models.CharField(max_length=250,default="0",null=True,blank=True)
    momoNumber = models.CharField(max_length=250,default="0",null=True,blank=True)
    donationStatus = models.CharField(max_length=250,default="0",null=True,blank=True)
    PODs = models.FileField(upload_to="Donations/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Withdrawal(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    amount=models.DecimalField(max_digits=11,decimal_places=0,default=0,blank=True,null=True)
    momoName = models.CharField(max_length=250,default="0",null=True,blank=True)
    momoNumber = models.CharField(max_length=250,default="0",null=True,blank=True)
    withdrawalStatus = models.CharField(max_length=250,default="0",null=True,blank=True)
    transactionType = models.CharField(max_length=250,default="Withdrawal",null=True,blank=True)
    POPs = models.FileField(upload_to="Withdrawal/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PreferenceDate(models.Model):
    member = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    preference_date = models.DateField(null=True, blank=True)
    preferenceStatus = models.CharField(max_length=250,default="0",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)