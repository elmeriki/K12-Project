from django.db import models
from django.contrib.auth.models import AbstractUser
from k12auth.models import *

class User(AbstractUser):
    is_member = models.BooleanField(default=False,blank=True,null=True)
    is_cashier = models.BooleanField(default=False,blank=True,null=True)
    is_manager = models.BooleanField(default=False,blank=True,null=True)
    is_admin = models.BooleanField(default=False,blank=True,null=True)
    membershipTitle = models.CharField(max_length=200,default=0,null=True,blank=True)
    position = models.CharField(max_length=200,default=0,null=True,blank=True)
    
    def __str__(self):
        return self.username
    
    class Meta(AbstractUser.Meta):
       swappable = 'AUTH_USER_MODEL'

