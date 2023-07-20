from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Bots(models.Model):
    bot_id = models.AutoField(primary_key=True)  # Campo para el ID único del bot
    tittle = models.CharField(max_length=100)
    activator = models.CharField(max_length=255)  # El contenido que activa al bot
    body = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tittle

class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    # Otros campos necesarios

    def __str__(self):
        return self.token

#Notification Models:

class Task(models.Model):
    wamID = models.TextField(blank=True)
    tittle = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    status = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    Type = models.TextField(blank=True)
    datecompleted = models.DateTimeField(null=True, blank = True)
    dateprogramed = models.DateTimeField(null = True, blank = True)
    important = models.BooleanField(default=False)
    to = models.TextField(blank=True)
    sender = models.TextField(blank=True)
    groups = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tittle + '-by ' + self.user.username
    
class Mail(models.Model):
    tittle = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    subject = models.CharField(max_length=200)
    adress = models.EmailField(blank = True)
    created = models.DateTimeField(auto_now_add=True)
    dateprogramed = models.DateTimeField(null = True, blank = True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tittle + '-by ' + self.user.username
    
class Phone(models.Model):
    tittle = models.CharField(max_length=100)
    message = models.TextField(blank=True)
    subject = models.CharField(max_length=200)
    adress = models.EmailField(blank = True)
    created = models.DateTimeField(auto_now_add=True)
    dateprogramed = models.DateTimeField(null = True, blank = True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tittle + '-by ' + self.user.username

#Group Models:

class WhatsappGroup(models.Model):
    groupname = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.groupname + '-by ' + self.user.username

class MailGroup(models.Model):
    groupname = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.groupname + '-by ' + self.user.username

class PhoneGroup(models.Model):
    groupname = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    members = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.groupname + '-by ' + self.user.username

