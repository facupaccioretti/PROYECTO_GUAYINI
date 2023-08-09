from django.forms import ModelForm
from django import forms
from .models import Task, Mail, Phone, WhatsappGroup, MailGroup, PhoneGroup, Alert, Bots, Contact
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

class AlertForm(forms.ModelForm):
    class Meta:
        model = Alert
        fields = ['tittle', 'to', 'body', 'description']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'image', 'number', 'address', 'description']


class BotForm(forms.ModelForm):
    class Meta:
        model = Bots
        fields = ['tittle', 'activator', 'body']

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['tittle', 'message', 'to', 'groups', 'dateprogramed', 'important']
        widgets = {
            'tittle' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a tittle'}),
            'message' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your message'}),
            'to': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your contact'}),
            'groups': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your contact group'}),
            'dateprogramed' : DateTimePickerInput(options={"format": "YYYY-MM-DD HH:mm", "showClose": True,  "showClear": True,   "showTodayButton": True}),
            'important' : forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }

class MailForm(forms.ModelForm):
    class Meta:
        model = Mail
        fields = ['tittle', 'message', 'subject', 'adress', 'dateprogramed', 'important']
        widgets = {
            'tittle' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a tittle'}),
            'message' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a your message'}),
            'subject' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a your subject'}), 
            'adress' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the receiver email adress'}),
            'dateprogramed' : DateTimePickerInput(options={"format": "YYYY-MM-DD HH:mm", "showClose": True,  "showClear": True,   "showTodayButton": True}),
            'important' : forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['tittle', 'message', 'subject', 'adress', 'dateprogramed', 'important']
        widgets = {
            'tittle' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a tittle'}),
            'message' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a your message'}),
            'subject' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a your subject'}), 
            'adress' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the receiver email adress'}),
            'dateprogramed' : DateTimePickerInput(options={"format": "YYYY-MM-DD HH:mm", "showClose": True,  "showClear": True,   "showTodayButton": True}),
            'important' : forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }

class WhatsappGroupForm(forms.ModelForm):
    class Meta:
        model = WhatsappGroup
        fields = ['groupname', 'description', 'members']
        widgets = {
            'groupname' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the group name'}),
            'description' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write the group description'}),
            'members' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write the group members separated by ";"'})       
        }

class MailGroupForm(forms.ModelForm):
    class Meta:
        model = MailGroup
        fields = ['groupname', 'description', 'members']
        widgets = {
            'groupname' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the group name'}),
            'description' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write the group description'}),
            'members' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write the group members separated by ";"'})       
        }

class PhoneGroupForm(forms.ModelForm):
    class Meta:
        model = PhoneGroup
        fields = ['groupname', 'description', 'members']
        widgets = {
            'groupname' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the group name'}),
            'description' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write the group description'}),
            'members' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write the group members separated by ";"'})       
        }

