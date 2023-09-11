from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
class Alert(models.Model):
    tittle = models.CharField(max_length=100)
    to = models.TextField(blank=True)
    body = models.TextField()
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)  # blank true
    def __str__(self):
        return self.tittle + '-by ' + self.user.username

class Contact(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='contactos/', blank=True, null=True)
    number = models.TextField(blank=True)
    address = models.EmailField(blank=True)
    description = models.CharField(max_length=1024)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)  # blank true
    def __str__(self):
        return self.name + '-by ' + self.user.username

#BOT ARBOL:
class Bots(MPTTModel):
    bot_id = models.AutoField(primary_key=True)
    tittle = models.CharField(max_length=100)
    activator = models.CharField(max_length=255)
    body = models.TextField()
    response_buttons = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created = models.DateTimeField(auto_now_add=True)  # Blank true

    def __str__(self):
        return self.tittle

    def save(self, *args, **kwargs):
        if self.response_buttons:
            options = self.response_buttons.split(',')
            super().save(*args, **kwargs)

            for option in options:
                new_bot = Bots(
                    tittle=f"Respuesta: - {option}",
                    activator=option.strip(),
                    user=self.user,
                    parent=self
                )
                new_bot.save()

        else:
            super().save(*args, **kwargs)

class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)  # blank true

    def __str__(self):
        return self.token

#BOT VIEJO
""""
class Bots(models.Model):
    bot_id = models.AutoField(primary_key=True)
    tittle = models.CharField(max_length=100)
    activator = models.CharField(max_length=255)
    body = models.TextField()
    response_buttons = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.tittle

    def save(self, *args, **kwargs):
        if self.response_buttons:
            options = self.response_buttons.split(',')
            self.pk = None
            super().save(*args, **kwargs)

            for option in options:
                new_bot = Bots(
                    tittle=f"Respuesta: - {option}",
                    activator=option.strip(),
                    user=self.user,
                )
                new_bot.pk = None
                new_bot.save()

        else:
            super().save(*args, **kwargs)
"""


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
    datecompleted = models.DateTimeField(null=True, blank = True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.TextField(blank=True)

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
#modelo de grupo de contactos}

class Group(models.Model):
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
    
class WhatsappGroup(models.Model):
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

