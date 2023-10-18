from django.forms import ModelForm
from django import forms
from .models import Task, Mail, Phone, WhatsappGroup, MailGroup, PhoneGroup, WhatsappAlert, Bots, Contact, MailAlert, PhoneAlert
from bootstrap_datepicker_plus.widgets import DateTimePickerInput

class WhatsappAlertForm(forms.ModelForm):
    class Meta:
        model = WhatsappAlert
        fields = ['tittle', 'to', 'body', 'description']

class MailAlertForm(forms.ModelForm):
    class Meta:
        model = MailAlert
        fields = ['tittle', 'address', 'body', 'description']

class PhoneAlertForm(forms.ModelForm):
    class Meta:
        model = PhoneAlert
        fields = ['tittle', 'to', 'body', 'description']


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'image', 'number', 'address', 'description']


class BotForm(forms.ModelForm):
    class Meta:
        model = Bots
        fields = ['tittle', 'activator', 'body', 'response_buttons']

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
            'adress' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the receiver email adress separated by ","'}),
            'groups' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your contact group'}),
            'dateprogramed' : DateTimePickerInput(options={"format": "YYYY-MM-DD HH:mm", "showClose": True,  "showClear": True,   "showTodayButton": True}),
            'important' : forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'})
            
        }

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = ['tittle', 'message', 'to', 'dateprogramed', 'important']
        widgets = {
            'tittle' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write a tittle'}),
            'message' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a your message'}), 
            'to' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Write the receiver number'}),
            'dateprogramed' : DateTimePickerInput(options={"format": "YYYY-MM-DD HH:mm", "showClose": True,  "showClear": True,   "showTodayButton": True}),
            'important' : forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }

class WhatsappGroupForm(forms.ModelForm):
    class Meta:
        model = WhatsappGroup
        fields = ['groupname', 'description', 'members']
        widgets = {
            'groupname' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escriba el nombre del grupo'}),
            'description' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escriba una descripción del grupo'}),
            'members' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escriba los miembros del grupo separados por ","'})       
        }
        labels = {
            'groupname': 'Nombre del Grupo',
            'description': 'Descripción',
            'members': 'Miembros',
        }

class MailGroupForm(forms.ModelForm):
    class Meta:
        model = MailGroup
        fields = ['groupname', 'description', 'members']
        widgets = {
            'groupname' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escriba el nombre del grupo'}),
            'description' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escriba una descripción del grupo'}),
            'members' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escriba los miembros del grupo separados por ","'})       
        }
        labels = {
            'groupname': 'Nombre del Grupo',
            'description': 'Descripción',
            'members': 'Miembros',
        }

class PhoneGroupForm(forms.ModelForm):
    class Meta:
        model = PhoneGroup
        fields = ['groupname', 'description', 'members']
        widgets = {
            'groupname' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Escriba el nombre del grupo'}),
            'description' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escriba una descripción del grupo'}),
            'members' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Escriba los miembros del grupo separados por ","'})       
        }
        labels = {
            'groupname': 'Nombre del Grupo',
            'description': 'Descripción',
            'members': 'Miembros',
        }
