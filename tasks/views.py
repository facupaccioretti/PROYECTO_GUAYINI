from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm, MailForm, PhoneForm, WhatsappGroupForm, MailGroupForm, PhoneGroupForm, BotForm, ContactForm, WhatsappAlertForm, MailAlertForm, PhoneAlertForm
from .models import Mail, Task, Phone, Group, WhatsappGroup, MailGroup, PhoneGroup, AccessToken, Bots, Contact, Alert, WhatsappAlert, MailAlert, PhoneAlert
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta, timezone
from django.shortcuts import render
from twilio.rest import Client
from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
import messagebird
import json
import requests
from django.utils.crypto import get_random_string
import time
from django.views.decorators.csrf import csrf_exempt
from .models import AccessToken
import requests
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from itertools import groupby
from operator import attrgetter
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as sendgridMail
from django.template.loader import render_to_string
from heyoo import WhatsApp
from django.db.models import Q
import pytz
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Agregar esta línea para definir el timezone por defecto
# timezone.activate(pytz.timezone('America/Argentina/Buenos_Aires'))

# Create your views here.
@login_required
def groups(request):
    # Obtener los grupos existentes
    whatsappgroups = WhatsappGroup.objects.filter(user=request.user)
    mailgroups = MailGroup.objects.filter(user=request.user)
    phonegroups = PhoneGroup.objects.filter(user=request.user)

    # Inicializar los formularios
    whatsapp_form = WhatsappGroupForm()
    mail_form = MailGroupForm()
    phone_form = PhoneGroupForm()

    if request.method == "POST":
        if "whatsapp_form_submit" in request.POST:
            print("WhatsApp Form submitted")
            whatsapp_form = WhatsappGroupForm(request.POST)
            if whatsapp_form.is_valid():
                print("WhatsApp Form is valid")
                # Procesar el formulario de WhatsApp y guardar el grupo
                whatsapp_group = whatsapp_form.save(commit=False)
                whatsapp_group.user = request.user
                whatsapp_group.save()
                print("WhatsApp Group saved successfully")
                return redirect('groups')
            else:
                print("WhatsApp Form is not valid")

        
        elif "mail_form_submit" in request.POST:
            # El formulario de Mail se envió
            mail_form = MailGroupForm(request.POST)
            if mail_form.is_valid():
                # Procesar el formulario de Mail y guardar el grupo
                mail_group = mail_form.save(commit=False)
                mail_group.user = request.user
                mail_group.save()
                return redirect('groups')
        
        elif "phone_form_submit" in request.POST:
            # El formulario de Phone se envió
            phone_form = PhoneGroupForm(request.POST)
            if phone_form.is_valid():
                # Procesar el formulario de Phone y guardar el grupo
                phone_group = phone_form.save(commit=False)
                phone_group.user = request.user
                phone_group.save()
                return redirect('groups')

    context = {
        'whatsapp_form': whatsapp_form,
        'mail_form': mail_form,
        'phone_form': phone_form,
        'whatsappgroups': whatsappgroups,
        'mailgroups': mailgroups,
        'phonegroups': phonegroups,
    }

    return render(request, "groups.html", context)

@login_required
def create_groups(request): 
        return render(request, 'create_groups.html')


def landing(request): 
    return render(request, "landing.html")

def step1(request): 
    return render(request, "step1.html")

def home(request): 
    return render(request, "home.html")

def notifications(request): 
    return render(request, "notifications.html")

def signup(request): 

    if request.method == 'GET':
        return render(request, "signup.html", {
            'form': UserCreationForm
    })
    else:
        if request.POST['password1'] == request.POST['password2']:
            #REGISTER USER
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                token = get_random_string(length=32)
                AccessToken.objects.create(user=user, token=token)
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request, "signup.html", {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
        else:
            return render(request, "signup.html", {
                    'form': UserCreationForm,
                    'error': 'Password do not match'
                })

@csrf_exempt
def signin(request):
    if request.method == 'GET':
        response = requests.get('https://guayini.com/send_scheduled_messages_facebook/')
        response2 = requests.get('https://guayini.com/send_scheduled_emails/')
        response3 = requests.get('https://guayini.com/send_scheduled_phone_calls/')
        return render(request, 'signin.html',{
            'form': AuthenticationForm
        })
    else: 
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html',{
            'form': AuthenticationForm,
            'error': 'Username or password is incorrect'
        })
        else:
            login(request, user)
            return redirect('home')

@login_required
def signout(request):
    logout(request)
    return redirect('step1')

@login_required
def profile(request):
    user = request.user
    context = {'user': user,}
    try:
        token = AccessToken.objects.get(user=request.user).token
    except AccessToken.DoesNotExist:
        token = None
    return render(request, 'profile.html', {'token': token})

#NOTIFICATION VIEWS
    # WHATSAPP VIEWS:
@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user).order_by('-created')
    completed_tasks = [task for task in tasks if task.datecompleted]
    pending_tasks = [task for task in tasks if not task.datecompleted]
    grupos = WhatsappGroup.objects.filter(user=request.user)  # Filtrar grupos del usuario actual

    if request.method == "POST":
        
        
        form = TaskForm(request.POST)
        
        if form.is_valid():
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()  # Guardar el objeto Task primero para obtener su ID
            
            selected_group_ids = request.POST.getlist('groups[]')
            
            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = WhatsappGroup.objects.get(groupname=group_id)
                        new_task.groups.add(grupo)  # Agregar grupos seleccionados a la tarea
                    except WhatsappGroup.DoesNotExist:
                        # Manejar el caso en que el grupo no exista en la base de datos
                        print(f"El grupo '{group_id}' no existe en la base de datos.")
            
            new_task.save()  # Guardar la tarea nuevamente con los grupos seleccionados
            return redirect('tasks')
        else:
            print(form.errors)  # Esto mostrará los errores de validación en la consola de desarrollo

    else:
        form = TaskForm()

    context = {
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'form': form,
        'grupos': grupos,
    }

    return render(request, 'tasks.html', context)

@login_required
def create_task(request):
    if request.method == "GET": 
        return render(request, 'create_tasks.html', {"form": TaskForm})
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'create_tasks.html', {"form": TaskForm, "error": "Error creating task."})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        task.dateprogramed = task.dateprogramed.strftime("%Y-%m-%d %H:%M:%S") if task.dateprogramed else ""
        grupos = WhatsappGroup.objects.filter(user=request.user)
        form = TaskForm(instance=task)
        # Obtener los grupos seleccionados en la tarea
        grupos_seleccionados = task.groups.all()
        print("Grupos Seleccionados:", grupos_seleccionados)  # Agrega este print para verificar grupos seleccionados
        return render(
            request,
            'task_detail.html',
            {'task': task, 'grupos': grupos, 'form': form, 'grupos_seleccionados': grupos_seleccionados}
        )
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)

            # Actualizar los grupos seleccionados en el objeto 'task'
            selected_group_ids = request.POST.getlist('groups[]')
            task.groups.set(selected_group_ids)
            
            print("Selected Group IDs:", selected_group_ids)  # Agrega este print para verificar los IDs de los grupos seleccionados
            print("Task Groups:", task.groups.all())  # Agrega este print para verificar los grupos en el objeto task

            form.save()
            print("Form:", form.cleaned_data)  # Agrega este print para verificar los datos del formulario
            return redirect('tasks')
        except ValueError:
            print("Form Errors:", form.errors)  # Agrega este print para verificar los errores del formulario
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': 'Error updating task.'})

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')
    
@login_required  
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user= request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

#NOTIFICATION VIEWS
    # MAIL VIEWS:
@login_required
def mails(request):
    # Obtener la zona horaria de Argentina
    tz = pytz.timezone("America/Argentina/Cordoba")
    # Obtener la fecha y hora actual en la zona horaria especificada
    now = datetime.now(tz)
    
    # Filtrar correos que aún no han sido enviados y tienen fecha programada igual o posterior a hoy
    mails = Mail.objects.filter(user=request.user, dateprogramed__gte=now).order_by('-created')
    return render(request, 'mails.html', {'mails': mails})

def create_mail(request):
    context = {}

    if request.method == "GET":
        grupos = MailGroup.objects.filter(user=request.user)
        context["form"] = MailForm
        context['grupos'] = grupos
        return render(request, 'create_mails.html', context)
    else:
        try:
            form = MailForm(request.POST)
            if form.is_valid():
                new_mail = form.save(commit=False)
                new_mail.user = request.user

                # Verifica si se seleccionaron grupos en el formulario
                selected_group_ids = request.POST.getlist('groups[]')
                if selected_group_ids and any(selected_group_ids):
                    cleaned_groups = [group.strip("[]\"'") for group in selected_group_ids]
                else:
                    cleaned_groups = []

                print(cleaned_groups)
                new_mail.save()

                # Agrega grupos solo si se seleccionaron en el formulario
                if cleaned_groups:
                    print(cleaned_groups)
                    for group_name in cleaned_groups:
                        print(group_name)
                        try:
                            group = MailGroup.objects.get(groupname=group_name, user=request.user)
                            print(group)
                            new_mail.groups.add(group)
                        except MailGroup.DoesNotExist:
                            print(f"El grupo '{group_name}' no existe.")
                
                return redirect('mails')
            else:
                print(form.errors)
                context["form"] = form
                return render(request, 'create_mails.html', context)
        except ValueError:
            context["form"] = MailForm
            context["error"] = "Error creating mail."
            return render(request, 'create_mails.html', context)

@login_required
def mails_completed(request):
    # Obtener la zona horaria de Argentina
    tz = pytz.timezone("America/Argentina/Cordoba")
    # Obtener la fecha y hora actual en la zona horaria especificada
    now = datetime.now(tz)
    
    # Filtrar correos cuya fecha programada es anterior al día de hoy y han sido completados
    mails = Mail.objects.filter(user=request.user, dateprogramed__lt=now).order_by('-created')
    return render(request, 'mails.html', {'mails': mails})

@login_required
def mail_detail(request, mail_id):
    if request.method == 'GET':
        mail = get_object_or_404(Mail, pk=mail_id, user=request.user)
        mail.dateprogramed = mail.dateprogramed.strftime("%Y-%m-%d %H:%M:%S") if mail.dateprogramed else ""
        grupos = MailGroup.objects.filter(user=request.user)
        form = MailForm(instance=mail)
        # Obtener los grupos seleccionados en el correo
        grupos_seleccionados = mail.groups.all()
        print(grupos)
        print(grupos_seleccionados)
        return render(
            request,
            'mail_detail.html',
            {'mail': mail, 'grupos': grupos, 'form': form, 'grupos_seleccionados': grupos_seleccionados}
        )
    else:
        try:
            mail = get_object_or_404(Mail, pk=mail_id, user=request.user)
            form = MailForm(request.POST, instance=mail)

            # Actualizar los grupos seleccionados en el objeto 'mail'
            selected_group_ids = request.POST.getlist('groups[]')
            mail.groups.set(selected_group_ids)

            form.save()
            print(form)
            print(form.errors)
            return redirect('mails')
        except ValueError:
            print(form.errors)
            return render(request, 'mail_detail.html', {'mail': mail, 'form': form, 'error': 'Error updating mail.'})

@login_required
def complete_mail(request, mail_id):
    mail = get_object_or_404(Mail, pk=mail_id, user= request.user)
    if request.method == 'POST':
        mail.datecompleted = timezone.now()
        mail.save()
        return redirect('mails')

@login_required  
def delete_mail(request, mail_id):
    mail = get_object_or_404(Mail, pk=mail_id, user= request.user)
    if request.method == 'POST':
        mail.delete()
        return redirect('mails')

# NOTIFICATION VIEWS:
    # PHONE VIEWS:

@login_required
def phones(request):
    phones = Phone.objects.filter(user=request.user)
    completed_phones = [phone for phone in phones if phone.datecompleted]
    pending_phones = [phone for phone in phones if not phone.datecompleted]
    grupos = PhoneGroup.objects.filter(user=request.user)  # Filtrar grupos del usuario actual   
    
    if request.method == "POST":
        print(request.POST)
        
        form = PhoneForm(request.POST)
        
        if form.is_valid():
            new_phone = form.save(commit=False)
            new_phone.user = request.user
            new_phone.save()  # Guardar el objeto phone primero para obtener su ID
            
            selected_group_ids = request.POST.getlist('groups[]')
            
            for group_id in selected_group_ids:
                try:
                    grupo = PhoneGroup.objects.get(groupname=group_id)
                    new_phone.groups.add(grupo)  # Agregar grupos seleccionados a la notificación de teléfono
                except PhoneGroup.DoesNotExist:
                    # Manejar el caso en el que un grupo no exista
                    pass
            
            new_phone.save()  # Guardar la notificación de teléfono nuevamente con los grupos seleccionados
            return redirect('phones')
        else:
            print(form.errors)  # Esto mostrará los errores de validación en la consola de desarrollo
    else:
        form = PhoneForm()

    context = {
        'completed_phones': completed_phones,
        'pending_phones': pending_phones,
        'form': form,
        'grupos': grupos,
    }
    return render(request, 'phones.html', context)

@login_required
def create_phone(request):
    if request.method == "GET": 
        return render(request, 'create_phones.html', {"form": PhoneForm})
    else:
        try:
            form = PhoneForm(request.POST)
            new_phone = form.save(commit=False)
            new_phone.user = request.user
            new_phone.save()
            return redirect('phones')
        except ValueError:
            return render(request, 'create_phones.html', {"form": MailForm, "error": "Error creating mail."})

@login_required
def phones_completed(request):
    phones = Phone.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    
    return render(request, 'phones.html', {'phones': phones})

@login_required        
def phone_detail(request, phone_id):
    if request.method == 'GET':
        phone = get_object_or_404(Phone, pk=phone_id, user=request.user)
        form = PhoneForm(instance=phone)
        return render(request, 'phone_detail.html', {'phone': phone, 'form': form})
    else:
        try:
            phone = get_object_or_404(Phone, pk=phone_id, user=request.user)
            form = PhoneForm(request.POST, instance=phone)
            form.save()
            return redirect('phones')
        except ValueError:
            return render(request, 'phone_detail.html', {'phone': phone, 'form': form, 'error': 'Error updating phone.'})

@login_required
def complete_phone(request, phone_id):
    phone = get_object_or_404(Phone, pk=phone_id, user= request.user)
    if request.method == 'POST':
        phone.datecompleted = timezone.now()
        phone.save()
        return redirect('phones')

@login_required  
def delete_phone(request, phone_id):
    phone = get_object_or_404(Phone, pk=phone_id, user= request.user)
    if request.method == 'POST':
        phone.delete()
        return redirect('phones')

#GROUPS VIEWS
    #WHATSAPP VIEWS:
@login_required
def whatsappgroups(request):
    whatsappgroups = WhatsappGroup.objects.filter(user=request.user)
    
    return render(request, 'whatsappgroups.html', {'whatsappgroups': whatsappgroups})

@login_required
def create_whatsappgroups(request):
    if request.method == "GET": 
        return render(request, 'create_whatsappgroups.html', {"whatsappform": WhatsappGroupForm})
    else:
        try:
            form = WhatsappGroupForm(request.POST)
            new_whatsappgroup = form.save(commit=False)
            new_whatsappgroup.user = request.user
            new_whatsappgroup.save()
            return redirect('whatsappgroups')
        except ValueError:
            return render(request, 'create_whatsappgroups.html', {"whatsappform": WhatsappGroupForm})

@login_required
def whatsappgroup_detail(request, whatsappgroup_id):
    if request.method == 'GET':
        whatsappgroup = get_object_or_404(WhatsappGroup, pk=whatsappgroup_id, user=request.user)
        whatsappgroupform = WhatsappGroupForm(instance=whatsappgroup)
        return render(request, 'whatsappgroup_detail.html', {'whatsappgroup': whatsappgroup, 'whatsappgroupform': whatsappgroupform})
    else:
        try:
            whatsappgroup = get_object_or_404(WhatsappGroup, pk=whatsappgroup_id, user=request.user)
            whatsappgroupform = WhatsappGroupForm(request.POST, instance=whatsappgroup)
            whatsappgroupform.save()
            return redirect('whatsappgroups')
        except ValueError:
            return render(request, 'whatsappgroup_detail.html', {'whatsappgroup': whatsappgroup, 'whatsappgroupform': whatsappgroupform, 'error': 'Error updating whatsappgroup.'})

@login_required  
def delete_whatsappgroup(request, whatsappgroup_id):
    whatsappgroup = get_object_or_404(WhatsappGroup, pk=whatsappgroup_id, user= request.user)
    if request.method == 'POST':
        whatsappgroup.delete()
        return redirect('groups')

#GROUPS VIEWS
    #MAIL VIEWS:
@login_required
def mailgroups(request):
    mailgroups = MailGroup.objects.filter(user=request.user)
    
    return render(request, 'mailgroups.html', {'mailgroups': mailgroups})

@login_required
def create_mailgroups(request):
    if request.method == "GET": 
        return render(request, 'create_mailgroups.html', {"mailform": MailGroupForm})
    else:
        try:
            form = MailGroupForm(request.POST)
            new_mailgroup = form.save(commit=False)
            new_mailgroup.user = request.user
            new_mailgroup.save()
            return redirect('mailgroups')
        except ValueError:
            return render(request, 'create_mailgroups.html', {"mailform": MailGroupForm})

@login_required
def mailgroup_detail(request, mailgroup_id):
    if request.method == 'GET':
        mailgroup = get_object_or_404(MailGroup, pk=mailgroup_id, user=request.user)
        mailgroupform = MailGroupForm(instance=mailgroup)
        return render(request, 'mailgroup_detail.html', {'mailgroup': mailgroup, 'mailgroupform': mailgroupform})
    else:
        try:
            mailgroup = get_object_or_404(MailGroup, pk=mailgroup_id, user=request.user)
            mailgroupform = MailGroupForm(instance=mailgroup)
            mailgroupform.save()
            return redirect('groups')
        except ValueError:
            return render(request, 'mailgroup_detail.html', {'mailgroup': mailgroup, 'mailgroupform': mailgroupform, 'error': 'Error updating mail group.'})

@login_required  
def delete_mailgroup(request, mailgroup_id):
    mailgroup = get_object_or_404(MailGroup, pk=mailgroup_id, user= request.user)
    if request.method == 'POST':
        mailgroup.delete()
        return redirect('groups')         

#GROUPS VIEWS
    #PHONE VIEWS:
@login_required
def phonegroups(request):
    phonegroups = PhoneGroup.objects.filter(user=request.user)
    
    return render(request, 'phonegroups.html', {'phonegroups': phonegroups})

@login_required
def create_phonegroups(request):
    if request.method == "GET": 
        return render(request, 'create_phonegroups.html', {"phoneform": PhoneGroupForm})
    else:
        try:
            form = PhoneGroupForm(request.POST)
            new_phonegroup = form.save(commit=False)
            new_phonegroup.user = request.user
            new_phonegroup.save()
            return redirect('phonegroups')
        except ValueError:
            return render(request, 'create_phonegroups.html', {"phoneform": PhoneGroupForm})

@login_required  
def delete_phonegroup(request, phonegroup_id):
    phonegroup = get_object_or_404(PhoneGroup, pk=phonegroup_id, user= request.user)
    if request.method == 'POST':
        phonegroup.delete()
        return redirect('groups') 
    
@login_required
def phonegroup_detail(request, phonegroup_id):
    if request.method == 'GET':
        phonegroup = get_object_or_404(MailGroup, pk=phonegroup_id, user=request.user)
        phonegroupform = PhoneGroupForm(instance=phonegroup)
        return render(request, 'phonegroup_detail.html', {'phonegroup': phonegroup, 'phonegroupform': phonegroupform})
    else:
        try:
            phonegroup = get_object_or_404(MailGroup, pk=phonegroup_id, user=request.user)
            phonegroupform = MailGroupForm(instance=phonegroup)
            phonegroupform.save()
            return redirect('groups')
        except ValueError:
            return render(request, 'phonegroup_detail.html', {'phonegroup': phonegroup, 'phonegroupform': phonegroupform, 'error': 'Error updating phone group.'})

#CALENDAR VIEW

@api_view(['GET'])
def get_eventos(request):
    # Obtener todas las tareas desde hace un mes hasta dentro de 3 meses
    fecha_inicio = datetime.now() - timedelta(days=30)
    fecha_fin = datetime.now() + timedelta(days=90)
    tasks = Task.objects.filter(dateprogramed__range=(fecha_inicio, fecha_fin))
    mails = Mail.objects.filter(dateprogramed__range=(fecha_inicio, fecha_fin))
    phones = Phone.objects.filter(dateprogramed__range=(fecha_inicio, fecha_fin))
    
    # Crear una lista de eventos para FullCalendar
    eventos = []
    for task in tasks:
        eventoswhatsapp = {
            'title': task.tittle,
            'start': task.dateprogramed.strftime('%Y-%m-%dT%H:%M:%S'),
            'url': f'/tasks/{task.id}/',  # URL para acceder a la tarea
            'color': 'green'
        }
        eventos.append(eventoswhatsapp)
    for mail in mails:
        eventosmail = {
            'title': mail.tittle,
            'start': mail.dateprogramed.strftime('%Y-%m-%dT%H:%M:%S'),
            'url': f'/mails/{mail.id}/',  # URL para acceder a la tarea
            'color': 'red'
        }
        eventos.append(eventosmail)   
    for phone in phones:
        eventosphone = {
            'title': phone.tittle,
            'start': phone.dateprogramed.strftime('%Y-%m-%dT%H:%M:%S'),
            'url': f'/phones/{phone.id}/',  # URL para acceder a la tarea
            'color': 'blue'
        }
        eventos.append(eventosphone)
    
    return Response(eventos)

@login_required
def calendar(request):
    return render(request, 'calendar.html')

def send_whatsapp_message_twilio(request):
    if request.method == 'POST':
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        
        to = request.POST.get('to')
        body = request.POST.get('body')
        
        message = client.messages.create(
            from_='whatsapp:' + settings.TWILIO_COETEC_NUMBER,
            body=body,
            to='whatsapp:' + to
        )
        
        return redirect('success')
    
    return render(request, 'send_message.html')

def success(request):
    return render(request, 'successWhatsapp.html')

@login_required
def send_scheduled_messages_twilio(request):
    # Obtener la zona horaria deseada, en este caso "America/Argentina/Cordoba"
    tz = pytz.timezone("America/Argentina/Cordoba")
    
    print("ejecutando cronjob")

    # Obtener la fecha y hora actual en la zona horaria deseada
    now = timezone.now().astimezone(tz)

    # Obtiene todas las tareas programadas que aún no se han completado
    tasks = Task.objects.filter(user=request.user, dateprogramed__lte=timezone.now(), datecompleted=None)
    
    # Verifica las fechas y horas programadas y las fechas y horas actuales
    for task in tasks:
        task_date = task.dateprogramed.astimezone(tz)
        print(f"Fecha y hora programada: {task_date}, Fecha y hora actual: {now}")

    # Envía los mensajes de WhatsApp
    for task in tasks:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        print(f"Enviando mensaje a: {task.to}")
        if task.to:
            numbers = task.to.split(",")  # separar los números por coma
            for number in numbers:
                message = client.messages.create(
                    body=task.message,
                    from_='whatsapp:' + settings.TWILIO_COETEC_NUMBER,
                    to=f'whatsapp:' + number.strip()  # eliminar espacios en blanco en el número
                )
        groups = task.groups.split(",")
        for group in groups:
            print(f"Procesando grupo {group}")
            try:
                whatsapp_group = WhatsappGroup.objects.get(groupname=group.strip())
                print(f"Grupo encontrado: {whatsapp_group}")
                for number in whatsapp_group.members.split(","):
                    print(f"Enviando mensaje a {number}")
                    message = client.messages.create(
                        body=task.message,
                        from_='whatsapp:' + settings.TWILIO_COETEC_NUMBER,
                        to=f'whatsapp:' + number.strip()
                    )
            except WhatsappGroup.DoesNotExist:
                print(f"Grupo no encontrado: {group.strip()}")
                pass

        # Marca la tarea como completada
        task.datecompleted = timezone.now()
        task.save()


    return redirect('tasks')

@csrf_exempt
def enviar_mensaje_curl_twilio(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        numero = request.POST.get('numero') or request.FILES.get('numero')

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        if numero is None:
            return JsonResponse({'mensaje': 'Numero de telefono faltante'}, status=400)
        message = client.messages.create(
            body=mensaje,
            from_='whatsapp:' + settings.TWILIO_COETEC_NUMBER,
            to=f'whatsapp:' + numero
        )

        return JsonResponse({'mensaje': 'Mensaje enviado exitosamente'})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})


@csrf_exempt
def enviar_mensaje_curl_messagebird(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '').strip()
        numeros_str = request.POST.get('numeros', '').strip()
        grupos_str = request.POST.get('grupos', '').strip()
        token = request.POST.get('token', '')

        if not numeros_str and not grupos_str:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        numeros = numeros_str.split(',') if numeros_str else []
        grupos = grupos_str.split(',') if grupos_str else []

        client = messagebird.Client(settings.MESSAGEBIRD_ACCESS_KEY)
        success_count = 0
        error_count = 0

        # Obtener todos los tokens de acceso existentes
        access_tokens = AccessToken.objects.values_list('token', flat=True)

        if token in access_tokens:
            if numeros:
                for numero in numeros:
                    print("Enviando el mensaje: " + mensaje)
                    print('A los números: ' + numero)

                    try:
                        msg = client.conversation_start({
                            'channelId': settings.MESSAGEBIRD_CHANNEL_ID,
                            'to': numero,
                            'type': MESSAGE_TYPE_HSM,
                            'content': {
                                'hsm': {
                                    'namespace': 'b7512d00_9a7c_4fb2_9b37_6a693d095188',
                                    'templateName': 'notificaciones',
                                    'language': {
                                        'policy': 'deterministic',
                                        'code': 'es_AR'
                                    },
                                    'params': [
                                        {"default": mensaje},
                                    ]
                                }
                            }
                        })

                        success_count += 1
                    except Exception as e:
                        # Manejar el error específico según tus necesidades
                        print("Error al enviar el mensaje:", str(e))
                        error_count += 1

            if grupos:
                for grupo in grupos:
                    print("Enviando el mensaje: " + mensaje)
                    print('Al grupo: ' + grupo)
                    try:
                        whatsapp_group = WhatsappGroup.objects.get(groupname=grupo.strip())
                        print(f"Grupo encontrado: {whatsapp_group}")
                        for number in whatsapp_group.members.split(","):
                            print(f"Enviando mensaje a {number}")
                            try:
                                msg = client.conversation_start({
                                    'channelId': settings.MESSAGEBIRD_CHANNEL_ID,
                                    'to': '' + number.strip(),
                                    'type': MESSAGE_TYPE_HSM,
                                    'content': {
                                        'hsm': {
                                            'namespace': 'b7512d00_9a7c_4fb2_9b37_6a693d095188',
                                            'templateName': 'notificaciones',
                                            'language': {
                                                'policy': 'deterministic',
                                                'code': 'es_AR'
                                            },
                                            'params': [
                                                {"default": mensaje},
                                            ]
                                        }
                                    }
                                })

                                success_count += 1
                            except Exception as e:
                                # Manejar el error específico según tus necesidades
                                print("Error al enviar el mensaje:", str(e))
                                error_count += 1
                    except WhatsappGroup.DoesNotExist:
                        print(f"Grupo no encontrado: {grupo.strip()}")
                        error_count += 1

            return JsonResponse({'mensaje': 'Mensajes enviados exitosamente: {}'.format(success_count),
                                 'errores': error_count})
        else:
            return JsonResponse({'mensaje': 'Token de acceso inválido'}, status=400)
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})


@csrf_exempt
def enviar_llamada_curl_messagebird(request):
    if request.method == 'POST':
        token = request.POST.get('token', '')
        mensaje = request.POST.get('mensaje', '').strip()
        numeros_str = request.POST.get('numeros', '').strip()
        grupos_str = request.POST.get('grupos', '').strip()
        numerosaux_str = request.POST.get('numerosaux')
        gruposaux_str = request.POST.get('gruposaux')

        if not numeros_str and not grupos_str:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        numeros = numeros_str.split(',') if numeros_str else []
        grupos = grupos_str.split(',') if grupos_str else []
        numeros_auxiliares = numerosaux_str.split(',') if numerosaux_str else []
        grupos_auxiliares = gruposaux_str.split(',') if gruposaux_str else []
        # LISTAS DE NUMEROS (PRINCIPALES Y AUXILIARES)
        numeros_principales_total = []
        numeros_auxiliares_total = []

        # Agregar números principales individuales
        numeros_principales_total.extend(numeros)
        # Agregar números auxiliares individuales
        numeros_auxiliares_total.extend(numeros_auxiliares)
        # Agregar números principales de los grupos
        for grupo in grupos:
            try:
                whatsapp_group = WhatsappGroup.objects.get(groupname=grupo.strip())
                numeros_grupo = whatsapp_group.members.split(",")
                numeros_principales_total.extend(numeros_grupo)
            except WhatsappGroup.DoesNotExist:
                pass
        # Agregar números auxiliares de los grupos auxiliares
        for grupo_auxiliar in grupos_auxiliares:
            try:
                whatsapp_group_auxiliar = WhatsappGroup.objects.get(groupname=grupo_auxiliar.strip())
                numeros_grupo_auxiliar = whatsapp_group_auxiliar.members.split(",")
                numeros_auxiliares_total.extend(numeros_grupo_auxiliar)
            except WhatsappGroup.DoesNotExist:
                pass

        client = messagebird.Client(settings.MESSAGEBIRD_ACCESS_KEY)  # Reemplaza 'YOUR_ACCESS_KEY' con tu propia clave de acceso de MessageBird
        success_count = 0
        error_count = 0
                # Obtener todos los tokens de acceso existentes
        access_tokens = AccessToken.objects.values_list('token', flat=True)

        if token in access_tokens:
            # SI SE PASARON NUMEROS SE INICIA ESTE BUCLE FOR
            if numeros:
                for numero in numeros:
                    print("Enviando llamada: " + mensaje)
                    print('Al número: ' + numero)

                    try:
                        callFlow = {
                            'source': '5493518008514', 
                            'destination': numero,
                            'callFlow': {
                                'steps': [
                                    {
                                        'action': 'say',
                                        'options': {
                                            'payload': mensaje,
                                            'language': 'es-mx',
                                            'voice': 'female'
                                        }
                                    }
                                ]
                            }
                        }

                        response = client.call_create(**callFlow, webhook=None)
                        success_count += 1
                        print(response)
                        #UNA VEZ QUE CREO LA LLAMADA, OBTENGO EL ID 
                        if response.data.status == 'queued': # LA PETICION DE CREACION DE LA LLAMADA ES CORRECTA Y LA API LA ENCOLÓ
                            call_id = response.data.id
                            print('La informacion de la llamada es la siguiente: ')
                            print(call_id)
                            print('DURMIENDO 30 SEGUNDOS PARA VERIFICAR SI CONTESTARON O NO LA LLAMADA')
                            time.sleep(30)
                            try:
                                    call = client.call(call_id)
                                    print('  id                : %s' % call.data.id)
                                    print('  status            : %s' % call.data.status)
                                    print('  source            : %s' % call.data.source)
                                    print('  destination       : %s' % call.data.destination)

                            except messagebird.client.ErrorException as e:
                                    print('An error occurred while creating a call:')
                                    for error in e.errors:
                                            print('  code        : %d' % error.code)
                                            print('  description : %s' % error.description)
                            if call.data.status == 'no_answer' and numeros_auxiliares:

                                for numero_auxiliar in numeros_auxiliares:
                                    print('LLAMADA NO CONTESTADA, LLAMANDO A: ' + numero_auxiliar)
                                        
                                    callFlow = { 'source': '5493518008514', 
                                                    'destination': numero_auxiliar,
                                                    'callFlow': {
                                                        'steps': [
                                                            {
                                                                'action': 'say',
                                                                'options': {
                                                                    'payload': mensaje,
                                                                    'language': 'es-mx',
                                                                    'voice': 'female'
                                                                }
                                                            }
                                                        ]
                                                    }
                                                }
                                    response = client.call_create(**callFlow, webhook=None)
                                    success_count += 1
                                    llamada_auxiliar = True
                                    print(response)
                    except messagebird.client.ErrorException as e:
                        print("Error al enviar la llamada:", e)
                        error_count += 1

            if grupos:
                for grupo in grupos:
                    print("Enviando llamada: " + mensaje)
                    print('Al grupo: ' + grupo)
                    try:
                        whatsapp_group = WhatsappGroup.objects.get(groupname=grupo.strip())
                        print(f"Grupo encontrado: {whatsapp_group}")
                        for number in whatsapp_group.members.split(","):
                            print(f"Llamando a {number}")
                            try:
                                callFlow = {
                                    'source': '5493518008514',  # Reemplaza 'YOUR_CALLER_ID' con tu propio ID de llamante
                                    'destination': number,
                                    'callFlow': {
                                        'steps': [
                                            {
                                                'action': 'say',
                                                'options': {
                                                    'payload': mensaje,
                                                    'language': 'es-mx',
                                                    'voice': 'female'
                                                }
                                            }
                                        ],
                                        'webhook': 'http://127.0.0.1:8000/recibir_webhook/'  # Establece la URL de tu webhook aquí
                                    }
                                }

                                response = client.call_create(**callFlow)
                                success_count += 1
                                print(response)
                            except messagebird.client.ErrorException as e:
                                print("Error al enviar la llamada:", e)
                                error_count += 1
                    except WhatsappGroup.DoesNotExist:
                        print(f"Grupo no encontrado: {grupo.strip()}")
                        error_count += 1
            if llamada_auxiliar:    
                return JsonResponse({'mensaje': 'Llamadas enviadas exitosamente: {}'.format(success_count),
                                    'errores': error_count, 'Llamada a numero auxiliar': 'Si, el numero principal no contestó.'})
            else: 
                return JsonResponse({'mensaje': 'Llamadas enviadas exitosamente: {}'.format(success_count),
                                'errores': error_count})
        else:
            return JsonResponse({'mensaje': 'Token de acceso inválido'}, status=400)
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})


def generate_token(request):
    if request.method == 'POST' and request.user.is_authenticated:
        # Generar un nuevo token de acceso para el usuario y guardar en la base de datos
        AccessToken.objects.filter(user=request.user).delete()
        token = get_random_string(length=32)
        AccessToken.objects.create(user=request.user, token=token)

    return redirect('profile')


#LLAMADAS
#la función "enviar_llamada_curl" maneja los números principales y 
# auxiliares por separado y realiza llamadas adicionales a los números auxiliares 
# en caso de que las llamadas principales no sean contestadas.
@csrf_exempt
def enviar_llamada_curl(request):
    if request.method == 'POST':
        token = request.POST.get('token', '')
        mensaje = request.POST.get('mensaje', '').strip()
        numeros_str = request.POST.get('numeros', '').strip()
        grupos_str = request.POST.get('grupos', '').strip()
        numerosaux_str = request.POST.get('numerosaux')
        gruposaux_str = request.POST.get('gruposaux')

        if not numeros_str and not grupos_str:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        numeros = numeros_str.split(',') if numeros_str else []
        grupos = grupos_str.split(',') if grupos_str else []
        numeros_auxiliares = numerosaux_str.split(',') if numerosaux_str else []
        grupos_auxiliares = gruposaux_str.split(',') if gruposaux_str else []
        # LISTAS DE NUMEROS (PRINCIPALES Y AUXILIARES)
        numeros_principales_total = []
        numeros_auxiliares_total = []

        # Agregar números principales individuales
        numeros_principales_total.extend(numeros)
        # Agregar números auxiliares individuales
        numeros_auxiliares_total.extend(numeros_auxiliares)
        # Agregar números principales de los grupos
        for grupo in grupos:
            try:
                whatsapp_group = WhatsappGroup.objects.get(groupname=grupo.strip())
                numeros_grupo = whatsapp_group.members.split(",")
                numeros_principales_total.extend(numeros_grupo)
            except WhatsappGroup.DoesNotExist:
                pass
        # Agregar números auxiliares de los grupos auxiliares
        for grupo_auxiliar in grupos_auxiliares:
            try:
                whatsapp_group_auxiliar = WhatsappGroup.objects.get(groupname=grupo_auxiliar.strip())
                numeros_grupo_auxiliar = whatsapp_group_auxiliar.members.split(",")
                numeros_auxiliares_total.extend(numeros_grupo_auxiliar)
            except WhatsappGroup.DoesNotExist:
                pass

        client = messagebird.Client(settings.MESSAGEBIRD_ACCESS_KEY)
        success_count = 0
        error_count = 0
        llamadas_no_contestadas = 0
        llamadas_auxiliares = 0

        # Obtener todos los tokens de acceso existentes
        access_tokens = AccessToken.objects.values_list('token', flat=True)

        if token in access_tokens:
            # Si se pasaron números, se inicia este bucle for
            if numeros_principales_total:
                for numero in numeros_principales_total:
                    print("Enviando llamada: " + mensaje)
                    print('Al número: ' + numero)

                    try:
                        callFlow = {
                            'source': '5493518008514',
                            'destination': numero,
                            'callFlow': {
                                'steps': [
                                    {
                                        'action': 'say',
                                        'options': {
                                            'payload': mensaje,
                                            'language': 'es-mx',
                                            'voice': 'female'
                                        }
                                    }
                                ]
                            }
                        }

                        response = client.call_create(**callFlow, webhook=None)
                        success_count += 1
                        print(response)
                        # Una vez que se crea la llamada, se obtiene el ID
                        if response.data.status == 'queued':
                            call_id = response.data.id
                            print('La información de la llamada es la siguiente:')
                            print(call_id)
                            print('DURMIENDO 60 SEGUNDOS PARA VERIFICAR SI CONTESTARON O NO LA LLAMADA')
                            time.sleep(60)
                            try:
                                call = client.call(call_id)
                                print('  id                : %s' % call.data.id)
                                print('  status            : %s' % call.data.status)
                                print('  source            : %s' % call.data.source)
                                print('  destination       : %s' % call.data.destination)

                                if call.data.status == 'no_answer':
                                    llamadas_no_contestadas += 1
                                    if numeros_auxiliares_total:
                                        for numero_auxiliar in numeros_auxiliares_total:
                                            print('LLAMADA NO CONTESTADA, LLAMANDO A: ' + numero_auxiliar)

                                            callFlow = {
                                                'source': '5493518008514',
                                                'destination': numero_auxiliar,
                                                'callFlow': {
                                                    'steps': [
                                                        {
                                                            'action': 'say',
                                                            'options': {
                                                                'payload': mensaje,
                                                                'language': 'es-mx',
                                                                'voice': 'female'
                                                            }
                                                        }
                                                    ]
                                                }
                                            }
                                            response = client.call_create(**callFlow, webhook=None)
                                            success_count += 1
                                            llamadas_auxiliares += 1
                                            print(response)
                            except messagebird.client.ErrorException as e:
                                print('An error occurred while creating a call:')
                                for error in e.errors:
                                    print('  code        : %d' % error.code)
                                    print('  description : %s' % error.description)
                        else:
                            error_count += 1
                    except messagebird.client.ErrorException as e:
                        print("Error al enviar la llamada:", e)
                        error_count += 1

            return JsonResponse({
                'mensaje': 'Llamadas enviadas exitosamente: {}'.format(success_count),
                'errores': error_count,
                'llamadas_no_contestadas': llamadas_no_contestadas,
                'llamadas_auxiliares_enviadas': llamadas_auxiliares
            })

        else:
            return JsonResponse({'mensaje': 'Token de acceso inválido'}, status=400)

    else:
        return JsonResponse({'mensaje': 'Método no permitido'})

#la función "enviar_llamada_alerta" combina todos los números principales y de grupos
#en una sola lista y maneja las llamadas no contestadas y contestadas en 
#función de esta lista combinada.

@csrf_exempt
def enviar_llamada_alerta(request):
    if request.method == 'POST':
        token = request.POST.get('token', '')
        mensaje = request.POST.get('mensaje', '').strip()
        numeros_str = request.POST.get('numeros', '').strip()
        grupos_str = request.POST.get('grupos', '').strip()

        if not numeros_str and not grupos_str:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        numeros = numeros_str.split(',') if numeros_str else []
        grupos = grupos_str.split(',') if grupos_str else []

        if not numeros and not grupos:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        client = messagebird.Client(settings.MESSAGEBIRD_ACCESS_KEY)
        success_count = 0
        error_count = 0
        llamadas_no_contestadas = []
        llamadas_contestadas = []

        # Obtener todos los tokens de acceso existentes
        access_tokens = AccessToken.objects.values_list('token', flat=True)

        if token in access_tokens:
            numeros_totales = numeros + grupos  # Combinar números individuales y grupos en una única lista

            for numero in numeros_totales:
                print("Enviando llamada: " + mensaje)
                print('Al número: ' + numero)

                try:
                    callFlow = {
                        'source': '5493518008514',
                        'destination': numero,
                        'callFlow': {
                            'steps': [
                                {
                                    'action': 'say',
                                    'options': {
                                        'payload': mensaje,
                                        'language': 'es-mx',
                                        'voice': 'female'
                                    }
                                }
                            ]
                        }
                    }

                    response = client.call_create(**callFlow, webhook=None)
                    success_count += 1
                    print(response)

                    # Verificar si la llamada fue contestada
                    if response.data.status == 'queued':
                        call_id = response.data.id
                        print('La información de la llamada es la siguiente:')
                        print(call_id)
                        print('DURMIENDO 50 SEGUNDOS PARA VERIFICAR SI CONTESTARON O NO LA LLAMADA')
                        time.sleep(50)
                        try:
                            call = client.call(call_id)
                            print('  id                : %s' % call.data.id)
                            print('  status            : %s' % call.data.status)
                            print('  source            : %s' % call.data.source)
                            print('  destination       : %s' % call.data.destination)

                            if call.data.status == 'no_answer':
                                llamadas_no_contestadas.append(numero)
                            else:
                                llamadas_contestadas.append(numero)

                        except messagebird.client.ErrorException as e:
                            print('Ocurrió un error al obtener información de la llamada:', e)
                            error_count += 1

                except messagebird.client.ErrorException as e:
                    print("Error al enviar la llamada:", e)
                    error_count += 1

                if call.data.status != 'no_answer':
                    break  # Salir del bucle si la llamada fue contestada

            return JsonResponse({
                'mensaje': 'Llamadas enviadas exitosamente: {}'.format(success_count),
                'errores': error_count,
                'llamadas_contestadas': llamadas_contestadas,
                'llamadas_no_contestadas': llamadas_no_contestadas
            })

        else:
            return JsonResponse({'mensaje': 'Token de acceso inválido'}, status=400)

    else:
        return JsonResponse({'mensaje': 'Método no permitido'})

@csrf_exempt
def enviar_plantilla_wam_curl(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '').strip()
        numeros_str = request.POST.get('numeros', '').strip()
        grupos_str = request.POST.get('grupos', '').strip()
        token = request.POST.get('token', '')

        if not numeros_str and not grupos_str:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        numeros = numeros_str.split(',') if numeros_str else []
        grupos = grupos_str.split(',') if grupos_str else []

        success_count = 0
        error_count = 0

        # Verificar el token de acceso del usuario
        access_token = get_object_or_404(AccessToken, token=token)
        user = access_token.user

        # URL y encabezados de la solicitud a la API de Facebook
        url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
        headers = {
            'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Enviar mensajes a números individuales
        for numero in numeros:
            print("Enviando el mensaje: " + mensaje)
            print('A los números: ' + numero)

            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "template",
                "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                "template": {
                    "name": "notificaciones_marketing",
                    "language": {
                        "code": "es_AR"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": mensaje
                                }
                            ]
                        }
                    ]
                }
            }

            response = requests.post(url, headers=headers, json=data)
            print('La respuesta de Facebook fue: ')
            print(response.json())

            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1

        # Enviar mensajes a grupos
        for grupo in grupos:
            print("Enviando el mensaje: " + mensaje)
            print('Al grupo: ' + grupo)
            whatsapp_group = WhatsappGroup.objects.get(groupname=grupo.strip())
            print(f"Grupo encontrado: {whatsapp_group}")
            for number in whatsapp_group.members.split(","):
                # Obtener los miembros del grupo (puedes implementar tu lógica aquí)
                print(f"Enviando mensaje a {number}")

                data = {
                    "messaging_product": "whatsapp",
                    "to": number,
                    "type": "template",
                    "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                    "template": {
                        "name": "notificaciones_marketing",
                        "language": {
                            "code": "es_AR"
                        },
                        "components": [
                            {
                                "type": "body",
                                "parameters": [
                                    {
                                        "type": "text",
                                        "text": mensaje
                                    }
                                ]
                            }
                        ]
                    }
                }

                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    success_count += 1
                else:
                    error_count += 1

        return JsonResponse({'mensaje': 'Mensajes enviados exitosamente: {}'.format(success_count)})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})


@csrf_exempt
def enviar_plantilla_wam_curl1(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje', '').strip()
        numeros_str = request.POST.get('numeros', '').strip()
        grupos_str = request.POST.get('grupos', '').strip()
        token = request.POST.get('token', '')

        if not numeros_str and not grupos_str:
            return JsonResponse({'mensaje': 'Lista de números vacía. Por favor, seleccione un grupo de contactos o un número'}, status=400)

        numeros = numeros_str.split(',') if numeros_str else []
        grupos = grupos_str.split(',') if grupos_str else []

        success_count = 0
        error_count = 0

        # Verificar el token de acceso del usuario
        access_token = get_object_or_404(AccessToken, token=token)
        user = access_token.user

        # URL y encabezados de la solicitud a la API de Facebook
        url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
        headers = {
            'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Enviar mensajes a números individuales
        for numero in numeros:
            print("Enviando el mensaje: " + mensaje)
            print('A los números: ' + numero)

            data = {
                "messaging_product": "whatsapp",
                "to": numero,
                "type": "template",
                "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                "template": {
                    "name": "notificaciones_marketing",
                    "language": {
                        "code": "es_AR"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": mensaje
                                }
                            ]
                        }
                    ]
                }
            }

            response = requests.post(url, headers=headers, json=data)
            print('La respuesta de Facebook fue: ')
            print(response.json())

            if response.status_code == 200:
                success_count += 1
                # Aquí asignamos los valores correspondientes al mensaje en tu base de datos
                response_data = response.json()
                message_id = response_data['messages'][0]['id']
                mensaje = Task.objects.create(
                    wamID=message_id,
                    tittle='',
                    message=mensaje,
                    status='sent',
                    created=datetime.now(),
                    Type='template',
                    datecompleted=None,
                    dateprogramed=None,
                    important=False,
                    to=numero,
                    sender=settings.FACEBOOK_SENDER_NUMBER_1,
                    groups='',
                    user=user
                )
            else:
                error_count += 1

        # Enviar mensajes a grupos
        for grupo in grupos:
            print("Enviando el mensaje: " + mensaje)
            print('Al grupo: ' + grupo)
            whatsapp_group = WhatsappGroup.objects.get(groupname=grupo.strip())
            print(f"Grupo encontrado: {whatsapp_group}")
            for number in whatsapp_group.members.split(","):
            # Obtener los miembros del grupo (puedes implementar tu lógica aquí)
                print(f"Enviando mensaje a {number}")

                data = {
                    "messaging_product": "whatsapp",
                    "to": number,
                    "type": "template",
                    "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                    "template": {
                        "name": "notificaciones_marketing",
                        "language": {
                            "code": "es_AR"
                        },
                        "components": [
                            {
                                "type": "body",
                                "parameters": [
                                    {
                                        "type": "text",
                                        "text": mensaje
                                    }
                                ]
                            }
                        ]
                    }
                }

                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    success_count += 1
                    # Aquí asignamos los valores correspondientes al mensaje en tu base de datos
                    response_data = response.json()
                    message_id = response_data['messages'][0]['id']
                    mensaje = Task.objects.create(
                        wamID=message_id,
                        tittle='',
                        message=mensaje,
                        status='sent',
                        created=datetime.now(),
                        Type='template',
                        datecompleted=None,
                        dateprogramed=None,
                        important=False,
                        to=number,
                        sender=settings.FACEBOOK_SENDER_NUMBER_1,
                        groups=grupo,
                        user=user
                    )
                else:
                    error_count += 1

        return JsonResponse({'mensaje': 'Mensajes enviados exitosamente: {}'.format(success_count),
                             'Errores': error_count})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})

@csrf_exempt
def webhook_facebook(request):
    processed_messages = set()
    
    if request.method == 'GET':
        # VERIFICACION FACEBOOK
        # Obtiene los parámetros de consulta de la URL
        hub_verify_token = request.GET.get('hub.verify_token')

        # Verifica el valor de hub.verify_token con tu cadena de token configurada
        if hub_verify_token == 'guayini_token_aguantebelgrano':
            # Responde con el valor hub.challenge para completar la verificación
            hub_challenge = request.GET.get('hub.challenge')
            return HttpResponse(hub_challenge, content_type='text/plain')
        else:
            # Si el token de verificación no coincide, responde con un código de estado 403 (Prohibido)
            return HttpResponse(status=403)
    
    elif request.method == 'POST':
            data = json.loads(request.body)
            print("Notificación de Facebook recibida:")
            print(json.dumps(data, indent=4))  # Imprimir con formato para una visualización más clara

            if 'messages' in data['entry'][0]['changes'][0]['value']:
                # Es una notificación de un nuevo mensaje recibido
                wa_id = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
                message_id = data['entry'][0]['changes'][0]['value']['messages'][0]['id']
                timestamp = int(data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp'])
                message_type = data['entry'][0]['changes'][0]['value']['messages'][0]['type']
                status = 'received'

                if message_type == 'text':
                    message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                elif message_type == 'interactive':
                    message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['interactive']['button_reply']['title']

                # Obtener todas las palabras activadoras de los bots
                bots = Bots.objects.all()
                print(f"Mensaje recibido de: {wa_id}")
                print(f"Texto del mensaje: {message_text}")

                # Verificar si el mensaje contiene la palabra activadora de algún bot
                bot_triggered = None
                for bot in bots:
                    if bot.activator in message_text:
                        bot_triggered = bot
                        break

                if bot_triggered:
                    if bot_triggered.response_buttons:
                        response_buttons = bot_triggered.response_buttons.split(',')
                        buttons = []
                        for button_text in response_buttons:
                            buttons.append({
                                "type": "reply",
                                "reply": {
                                    "id": f"{button_text}_postback",
                                    "title": button_text
                                }
                            })

                        interactive_message = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": wa_id,
                            "type": "interactive",
                            "interactive": {
                                "type": "button",
                                "body": {
                                    "text": bot_triggered.body
                                },
                                "action": {
                                    "buttons": buttons
                                }
                            }
                        }

                        url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
                        headers = {
                            'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
                            'Content-Type': 'application/json'
                        }

                        response = requests.post(url, headers=headers, json=interactive_message)
                        print('Respuesta de Facebook:')
                        print(response.text)
                    else:
                        # URL y encabezados de la solicitud a la API de Facebook
                        url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
                        headers = {
                            'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
                            'Content-Type': 'application/json'
                        }

                        # Datos del mensaje a enviar
                        data = {
                            "messaging_product": "whatsapp",
                            "recipient_type": "individual",
                            "to": wa_id,
                            "type": "text",
                            "text": {
                                "body": bot_triggered.body
                            }
                        }

                        # Enviar el mensaje usando la API de Facebook
                        response = requests.post(url, headers=headers, json=data)
                        print('Respuesta de Facebook:')
                        print(response.text)
                        if response.status_code == 200:
                            # El mensaje se envió correctamente, puedes asignar los valores correspondientes al mensaje en tu base de datos
                            response_data = response.json()
                            sent_message_id = response_data.get('message_id', None)
                            if sent_message_id:
                                mensaje = Task.objects.create(
                                    wamID=sent_message_id,
                                    tittle='',
                                    message=message_text,
                                    status='sent',
                                    created=datetime.now(),
                                    Type='text',
                                    datecompleted=None,
                                    dateprogramed=None,
                                    important=False,
                                    to=wa_id,
                                    sender=settings.FACEBOOK_SENDER_NUMBER_1,
                                    groups='',
                                    user=bot_triggered.user
                                )
                        else:
                            # Ocurrió un error al enviar el mensaje
                            # Puedes manejar el error de acuerdo a tus necesidades
                            pass

                # Crea una nueva instancia del modelo Task y guarda los datos
                mensaje = Task(
                    wamID=message_id,
                    tittle='',
                    message=message_text,
                    status=status,
                    created=datetime.fromtimestamp(timestamp),
                    Type='',
                    datecompleted=None,
                    dateprogramed=None,
                    important=False,
                    to=wa_id,
                    sender='',
                    groups='',
                    user=bot_triggered.user if bot_triggered else None
                )
                mensaje.save()
                print(f"Mensaje {message_id} procesado y guardado en la base de datos.")

            return HttpResponse(status=200)
        
    else:
        # Responde con un código de estado 405 (Método no permitido) para otras solicitudes HTTP
        return HttpResponse(status=405)


@login_required
def bot_list(request):
    bots = Bots.objects.filter(user=request.user)

    return render(request, 'bot_list.html', {'bots': bots})


@login_required
def create_bot(request):
    if request.method == "GET": 
        return render(request, 'create_bot.html', {"form": BotForm()})
    else:
        try:
            form = BotForm(request.POST)
            new_bot = form.save(commit=False)
            new_bot.user = request.user  # Asigna el usuario propietario al bot
            new_bot.save()
            return redirect('bot_list')  # Redirige a la página que muestra los bots del usuario
        except ValueError:
            return render(request, 'create_bot.html', {"form": BotForm(), "error": "Error creating bot."})
        
@login_required
def bot_detail(request, bot_id):
    bot = get_object_or_404(Bots, bot_id=bot_id, user=request.user)

    if request.method == "POST":
        form = BotForm(request.POST, instance=bot)
        if form.is_valid():
            form.save()
            return redirect('bot_list')

    else:
        form = BotForm(instance=bot)

    return render(request, 'bot_detail.html', {'bot': bot, 'form': form})

@login_required
def complete_bot(request, bot_id):
    bot = get_object_or_404(Bots, bot_id=bot_id, user=request.user)

    # Lógica para completar el bot, si es necesario

    return redirect('bot_detail', bot_id=bot_id)  # Redirige de vuelta a la vista "bot_detail"

@login_required
def delete_bot(request, bot_id):
    bot = get_object_or_404(Bots, bot_id=bot_id, user=request.user)
    if request.method == 'POST':
        bot.delete()


    return redirect('bot_list')  # Redirige de vuelta a la vista "bot_list" después de eliminar el bot

@csrf_exempt
def send_scheduled_messages_facebook(request):
    if request.method == 'GET':
        # Obtén todas las tareas programadas que aún no se han completado para el usuario autenticado
        tasks = Task.objects.filter(dateprogramed__lte=timezone.now(), datecompleted=None)

        # Obtener la zona horaria deseada, en este caso "America/Argentina/Cordoba"
        tz = pytz.timezone("America/Argentina/Cordoba")
        now = timezone.now().astimezone(tz)

        # URL y encabezados de la solicitud a la API de Facebook
        url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
        headers = {
            'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

        # Envía los mensajes de WhatsApp
        for task in tasks:
            to_list = task.to.split(",") if task.to else []
            groups_list = task.groups.all()

            # Enviar mensajes a números individuales
            for number in to_list:
                print(f"Enviando mensaje a: {number}")

                data = {
                    "messaging_product": "whatsapp",
                    "to": number,
                    "type": "template",
                    "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                    "template": {
                        "name": "notificaciones_marketing",
                        "language": {
                            "code": "es_AR"
                        },
                        "components": [
                            {
                                "type": "body",
                                "parameters": [
                                    {
                                        "type": "text",
                                        "text": task.message
                                    }
                                ]
                            }
                        ]
                    }
                }

                response = requests.post(url, headers=headers, json=data)
                print('La respuesta de Facebook fue: ')
                print(response.json())

                if response.status_code == 200:
                    # Marca la tarea como completada
                    task.datecompleted = timezone.now()
                    task.status = 'sent'
                    task.save()

            # Enviar mensajes a grupos
            for group in groups_list:
                print(f"Enviando mensaje al grupo: {group.groupname}")
                members = group.members.split(",") if group.members else []

                for number in members:
                    print(f"Enviando mensaje a {number}")

                    data = {
                        "messaging_product": "whatsapp",
                        "to": number,
                        "type": "template",
                        "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                        "template": {
                            "name": "notificaciones_marketing",
                            "language": {
                                "code": "es_AR"
                            },
                            "components": [
                                {
                                    "type": "body",
                                    "parameters": [
                                        {
                                            "type": "text",
                                            "text": task.message
                                        }
                                    ]
                                }
                            ]
                        }
                    }

                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 200:
                        # Marca la tarea como completada
                        task.datecompleted = timezone.now()
                        task.status = 'sent'
                        task.save()
            # Fin del bucle de grupos

        return JsonResponse({'mensaje': 'Mensajes enviados exitosamente'})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})
    
    
@login_required
def chats(request):
        # Obtener el usuario actualmente autenticado
    user = request.user
    # Obtener los contactos del usuario
    contactos = Contact.objects.filter(user=user)

    mensajes = Task.objects.filter(user=user)

    return render(request, 'chats.html', {'user': user, 'contactos': contactos, "mensajes": mensajes})

@login_required
def contact_list(request):
    contacts = Contact.objects.filter(user=request.user)
    return render(request, 'contact_list.html', {'contacts': contacts})

@login_required
def contact_detail(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)

    return render(request, 'contact_detail.html', {'contact': contact, 'form': form})

@login_required
def create_contact(request):
    if request.method == "GET": 
        return render(request, 'create_contact.html', {"form": ContactForm()})
    else:
        try:
            form = ContactForm(request.POST, request.FILES)
            new_contact = form.save(commit=False)
            new_contact.user = request.user
            new_contact.save()
            return redirect('contact_list')
        except ValueError:
            return render(request, 'create_contact.html', {"form": ContactForm(), "error": "Error creating contact."})

@login_required
def complete_contact(request, contact_id):
    contact = get_object_or_404(Contact, contact_id=contact_id, user=request.user)

    # Lógica para completar el contact, si es necesario

    return redirect('contact_detail', contact_id=contact_id)  # Redirige de vuelta a la vista "contact_detail"

@login_required
def delete_contact(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    if request.method == 'POST':
        contact.delete()
        return redirect('contact_list')
    
    return render(request, 'delete_contact.html', {'contact': contact})

@login_required
def alerts(request):
    return render(request, 'alerts.html')


@login_required
def whatsapp_alerts(request):
    alerts = WhatsappAlert.objects.filter(user=request.user).order_by('-created')
    grupos = WhatsappGroup.objects.filter(user=request.user)

    if request.method == "POST":
        form = WhatsappAlertForm(request.POST, request.FILES)
        if form.is_valid():
            new_alert = form.save(commit=False)
            new_alert.user = request.user
            new_alert.save()

            selected_group_ids = request.POST.getlist('groups[]')

            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = WhatsappGroup.objects.get(groupname=group_id)
                        new_alert.groups.add(grupo)
                    except WhatsappGroup.DoesNotExist:
                        print(f"El grupo '{group_id}' no existe en la base de datos.")

            new_alert.save()
            return redirect('whatsapp_alerts')
        else:
            print('ERROR EN EL FORMULARIO')
            print(form.errors)
    else:
        form = WhatsappAlertForm()

    context = {
        'alerts': alerts,
        'form': form,
        'grupos': grupos,
    }

    return render(request, 'whatsapp_alerts.html', context)


@login_required
def update_whatsapp_alert(request, alert_id):
    alert = get_object_or_404(WhatsappAlert, id=alert_id, user=request.user)

    if request.method == "POST":
        form = WhatsappAlertForm(request.POST, instance=alert)
        if form.is_valid():
            updated_alert = form.save(commit=False)

            selected_group_ids = request.POST.getlist('groups[]')

            updated_alert.groups.clear()

            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = WhatsappGroup.objects.get(groupname=group_id)
                        updated_alert.groups.add(grupo)
                    except WhatsappGroup.DoesNotExist:
                        print(f"El grupo '{group_id}' no existe en la base de datos.")

            updated_alert.save()
            return redirect('whatsapp_alerts')
        else:
            print('ERROR EN EL FORMULARIO')
            print(form.errors)

    return redirect('whatsapp_alerts')

# Vista para ordenar las alertas de WhatsApp por fecha de creación
def order_whatsapp_alerts_by_created(request):
    alerts = WhatsappAlert.objects.filter(user=request.user).order_by('-created')
    data = render_to_string('whatsapp_alerts.html', {'alerts': alerts})
    return JsonResponse({'data': data})

# Vista para ordenar las alertas de WhatsApp por última fecha de envío
def order_whatsapp_alerts_by_last_sent(request):
    alerts = WhatsappAlert.objects.filter(user=request.user).order_by('-last_sent')
    data = render_to_string('whatsapp_alerts.html', {'alerts': alerts})
    print(data)
    return JsonResponse({'data': data})

@login_required
def alert_detail_whatsapp(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    
    if request.method == "POST":
        form = WhatsappAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            return redirect('alert_list')
    else:
        form = WhatsappAlertForm(instance=alert)

    return render(request, 'alert_detail.html', {'alert': alert, 'form': form})


@login_required
def create_alert(request):
    if request.method == "GET": 
        return render(request, 'create_alerts.html', {"form": WhatsappAlertForm()})
    else:
        try:
            form = WhatsappAlertForm(request.POST, request.FILES)
            new_alert = form.save(commit=False)
            new_alert.user = request.user
            new_alert.save()
            return redirect('alerts_list')
        except ValueError:
            return render(request, 'create_alerts.html', {"form": WhatsappAlertForm(), "error": "Error creating alert."})

@login_required
def complete_alert(request, alert_id):
    alert = get_object_or_404(Alert, bot_id=alert_id, user=request.user)

    # Lógica para completar el bot, si es necesario

    return redirect('alert_detail', alert_id=alert_id)  # Redirige de vuelta a la vista "alert_detail"

@login_required
def delete_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id, user=request.user)
    if request.method == 'POST':
        alert.delete()
        return redirect('alert_list')
    
    return render(request, 'delete_alert.html', {'alert': alert})


#MAIL ALERTS
@login_required
def mail_alerts(request):
    alerts = MailAlert.objects.filter(user=request.user).order_by('-created')
    grupos = MailGroup.objects.filter(user=request.user)

    if request.method == "POST":
        form = MailAlertForm(request.POST, request.FILES)
        if form.is_valid():
            new_alert = form.save(commit=False)
            new_alert.user = request.user
            new_alert.save()

            selected_group_ids = request.POST.getlist('groups[]')

            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = MailGroup.objects.get(groupname=group_id)
                        new_alert.groups.add(grupo)
                    except MailGroup.DoesNotExist:
                        print(f"El grupo '{group_id}' no existe en la base de datos.")

            new_alert.save()
            return redirect('mail_alerts')
        else:
            print('ERROR EN EL FORMULARIO')
            print(form.errors)
    else:
        form = MailAlertForm()

    context = {
        'alerts': alerts,
        'form': form,
        'grupos': grupos,
    }

    return render(request, 'mail_alerts.html', context)


@login_required
def update_mail_alert(request, alert_id):
    alert = get_object_or_404(MailAlert, id=alert_id, user=request.user)

    if request.method == "POST":
        form = MailAlertForm(request.POST, instance=alert)
        if form.is_valid():
            updated_alert = form.save(commit=False)

            selected_group_ids = request.POST.getlist('groups[]')

            updated_alert.groups.clear()

            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = MailGroup.objects.get(groupname=group_id)
                        updated_alert.groups.add(grupo)
                    except MailGroup.DoesNotExist:
                        print(f"El grupo '{group_id}' no existe en la base de datos.")

            updated_alert.save()
            return redirect('mail_alerts')
        else:
            print('ERROR EN EL FORMULARIO')
            print(form.errors)

    return redirect('mail_alerts')


@login_required
def phone_alerts(request):
    alerts = PhoneAlert.objects.filter(user=request.user).order_by('-created')
    grupos = PhoneGroup.objects.filter(user=request.user)

    if request.method == "POST":
        form = PhoneAlertForm(request.POST, request.FILES)
        if form.is_valid():
            new_alert = form.save(commit=False)
            new_alert.user = request.user
            new_alert.save()

            selected_group_ids = request.POST.getlist('groups[]')

            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = PhoneGroup.objects.get(groupname=group_id)
                        new_alert.groups.add(grupo)
                    except PhoneGroup.DoesNotExist:
                        print(f"El grupo '{group_id}' no existe en la base de datos.")

            new_alert.save()
            return redirect('phone_alerts')
        else:
            print('ERROR EN EL FORMULARIO')
            print(form.errors)
    else:
        form = PhoneAlertForm()

    context = {
        'alerts': alerts,
        'form': form,
        'grupos': grupos,
    }

    return render(request, 'phone_alerts.html', context)

@login_required
def update_phone_alert(request, alert_id):
    alert = get_object_or_404(PhoneAlert, id=alert_id, user=request.user)

    if request.method == "POST":
        form = PhoneAlertForm(request.POST, instance=alert)
        if form.is_valid():
            updated_alert = form.save(commit=False)

            selected_group_ids = request.POST.getlist('groups[]')

            updated_alert.groups.clear()

            if selected_group_ids:
                for group_id in selected_group_ids:
                    try:
                        grupo = PhoneGroup.objects.get(groupname=group_id)
                        updated_alert.groups.add(grupo)
                    except PhoneGroup.DoesNotExist:
                        print(f"El grupo '{group_id}' no existe en la base de datos.")

            updated_alert.save()
            return redirect('phone_alerts')
        else:
            print('ERROR EN EL FORMULARIO')
            print(form.errors)

    return redirect('phone_alerts')

# Vista para ordenar las alertas por fecha de creación
def order_phone_alerts_by_created(request):
    alerts = PhoneAlert.objects.filter(user=request.user).order_by('-created')
    data = render_to_string('phone_alerts.html', {'alerts': alerts})
    return JsonResponse({'data': data})

# Vista para ordenar las alertas por última fecha de uso
def order_phone_alerts_by_last_sent(request):
    alerts = PhoneAlert.objects.filter(user=request.user).order_by('-last_sent')
    data = render_to_string('phone_alerts.html', {'alerts': alerts})
    return JsonResponse({'data': data})

#BOTFLOW

@login_required
def bot_flow(request):
    selected_bot_id = request.POST.get('bot_id')
    form = BotForm()
    bots = Bots.objects.filter(user=request.user).order_by('level')
    
    if selected_bot_id:
        selected_bot = get_object_or_404(Bots, bot_id=selected_bot_id)
        bots_for_prev = get_bots_for_preview(selected_bot)
        messages = get_messages_for_preview(bots_for_prev)
    else:
        messages = []

        if request.method == "POST":
            form = BotForm(request.POST, request.FILES)
            if form.is_valid():
                new_bot = form.save(commit=False)
                new_bot.user = request.user
                new_bot.save()
                return redirect('bot_flow')

    grouped_bots = groupby(bots, key=attrgetter('level'))
    grouped_bot_list = [list(group) for key, group in grouped_bots]

    context = {
        'grouped_bots': grouped_bot_list,
        'form': form,
        'messages': messages,
    }

    return render(request, 'bot_flow.html', context)

def get_bots_for_preview(selected_bot):
    bots_for_prev = []
    current_bot = selected_bot

    while current_bot:
        bots_for_prev.append(current_bot)
        current_bot = Bots.objects.filter(user=current_bot.user, tree_id=current_bot.tree_id, level=current_bot.level - 1).first()

    bots_for_prev.reverse()
    return bots_for_prev

def get_messages_for_preview(bots_for_prev):
    messages = []

    for bot in bots_for_prev:
        messages.append(bot.activator)  # Agrega el activador como mensaje de receptor
        messages.append(bot.body)  # Agrega el cuerpo como mensaje de emisor

    return messages



@login_required
def edit_bot(request, bot_id):
    bot = get_object_or_404(Bots, bot_id=bot_id, user=request.user)
    
    if request.method == "POST":
        form = BotForm(request.POST, instance=bot)
        if form.is_valid():
            form.save()
    
    return redirect('bot_flow')  # Redirige de nuevo a la página bot_flow.html


@login_required
def delete_bot(request, bot_id):
    bot = get_object_or_404(Bots, bot_id=bot_id, user=request.user)
    
    if request.method == 'POST':
        bot.delete()
    
    return redirect('bot_flow')

@csrf_exempt
def send_scheduled_emails(request):
    if request.method == 'GET':
        # Obtén todos los correos electrónicos programados que aún no se han enviado
        emails = Mail.objects.filter(dateprogramed__lte=timezone.now(), datecompleted__isnull=True)
        

        # Define la URL de la API de EnvialoSimple
        api_url = "https://api.envialosimple.email/api/v1/mail/send"

        # Define las cabeceras de la solicitud
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2OTUyMzQyODQsImV4cCI6NDg1MDkwNzg4NCwicm9sZXMiOlsiUk9MRV9BRE1JTiIsIlJPTEVfVVNFUiJdLCJraWQiOiI2NTBiMzhlYzk3OTE2MjFmMWMwNmMyODAiLCJhaWQiOiI2NGZmMmVjMTdiMTdmZmVhNDYwMzQ2ZTgiLCJ1c2VybmFtZSI6ImJyaWFuXzExXzkyQGhvdG1haWwuY29tIn0.eJVeRQBypyAYjj9Eu3iLCSggDlOb4cIr4r-3-liCLTothyuZyWgXrF_I6cncLBylzrWMY2YUuwI_EbWUPKxTFvTy5_SivjCABBYyvoMljnDtVMgYYbWu0D0n1IBBvLiP51s1BpY-znza-wEZWntBpayLF3guH_0dUJM9GWAr-3mszyQ9udfpaU7QnQKRgkz24sH91HkVSoitXypqto23B-nF_doLKr6GPo9WjcUEjmg-jnc_u764AiGgdXcB-xBYWlv3p7OhQG2qRsIqYC9hfN5UfaeQMIAiw8PExkSQ5O_U1d5uNQesX1kYF6XArKUOlGNbxPDeBrnEbwBjtQnO0w',
            'Content-Type': 'application/json'
        }

        for email in emails:
            print('ENVIANDO EL MAIL CON TITULO:')
            print(email.tittle)
            # Dividir las direcciones de correo electrónico por ","
            email_addresses = email.adress.split(",")
            print('enviando a los mails: ')
            print(email_address)

            # Incluir miembros del grupo si se seleccionó un grupo
            if email.groups.exists():
                print('existen grupos en esta notificacion, son: ')
                group = email.groups.first()  # Obtiene el primer grupo asociado al correo
                group_members = group.members.split(",")
                print(group_members)
                email_addresses.extend(group_members)


            for email_address in email_addresses:
                # Resto de tu código para enviar el correo electrónico, similar a como lo tenías antes
                email_data = {
                    "from": "notificaciones@guayini.com",
                    "to": email_address.strip(),  # Limpiar espacios en blanco
                    "subject": email.subject,
                    "html": email.message,
                    # Puedes agregar más campos o personalización aquí según tus necesidades
                }

                # Convierte los datos a formato JSON
                payload = json.dumps(email_data)

                # Realiza la solicitud POST a la API de EnvialoSimple
                response = requests.post(api_url, headers=headers, data=payload)
                print('La respuesta de envialosimple fue:')
                print(response.content)
                if response.status_code == 200:
                    # Marca el correo electrónico como enviado
                    email.datecompleted = timezone.now()
                    email.save()

        return JsonResponse({'mensaje': 'Correos electrónicos enviados exitosamente'})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})
    
@csrf_exempt
def send_scheduled_phone_calls(request):
    if request.method == 'GET':
        # Obtén todas las notificaciones programadas de llamadas que aún no se han completado
        phone_calls = Phone.objects.filter(dateprogramed__lte=timezone.now(), datecompleted=None)

        # Obtener la zona horaria deseada, en este caso "America/Argentina/Cordoba"
        tz = pytz.timezone("America/Argentina/Cordoba")
        now = timezone.now().astimezone(tz)

        client = messagebird.Client(settings.MESSAGEBIRD_ACCESS_KEY)  # Reemplaza 'YOUR_ACCESS_KEY' con tu propia clave de acceso de MessageBird
        success_count = 0
        error_count = 0

        for phone_call in phone_calls:
            to_list = phone_call.to.split(",") if phone_call.to else []
            groups_list = [group.groupname for group in phone_call.groups.all()]

            # Enviar llamadas a números individuales
            for number in to_list:
                print(f"Enviando llamada a: {number}")
                try:
                    callFlow = {
                        'source': '5493518008514',  # Reemplaza 'YOUR_CALLER_ID' con tu propio ID de llamante
                        'destination': number,
                        'callFlow': {
                            'steps': [
                                {
                                    'action': 'say',
                                    'options': {
                                        'payload': phone_call.message,
                                        'language': 'es-mx',
                                        'voice': 'female'
                                    }
                                }
                            ]
                        }
                    }

                    response = client.call_create(**callFlow, webhook=None)
                    success_count += 1
                    print(response)

                    if response.data.status == 'queued':
                        call_id = response.data.id
                        print('La información de la llamada es la siguiente:')
                        print(call_id)
                        print('Esperando 30 segundos para verificar si contestaron la llamada o no')
                        time.sleep(30)

                        try:
                            call = client.call(call_id)
                            print('  id                : %s' % call.data.id)
                            print('  status            : %s' % call.data.status)
                            print('  source            : %s' % call.data.source)
                            print('  destination       : %s' % call.data.destination)
                        except messagebird.client.ErrorException as e:
                            print('Ocurrió un error al obtener información de la llamada:')
                            for error in e.errors:
                                print('  code        : %d' % error.code)
                                print('  description : %s' % error.description)

                        if call.data.status == 'no_answer':
                            # Si la llamada no se contestó y hay números auxiliares, realizar llamadas auxiliares
                            numeros_auxiliares = phone_call.numbersaux.split(",") if phone_call.numbersaux else []
                            for numero_auxiliar in numeros_auxiliares:
                                print(f'Llamada no contestada, llamando a: {numero_auxiliar}')
                                callFlow = {
                                    'source': '5493518008514',
                                    'destination': numero_auxiliar,
                                    'callFlow': {
                                        'steps': [
                                            {
                                                'action': 'say',
                                                'options': {
                                                    'payload': phone_call.message,
                                                    'language': 'es-mx',
                                                    'voice': 'female'
                                                }
                                            }
                                        ]
                                    }
                                }
                                response = client.call_create(**callFlow, webhook=None)
                                success_count += 1
                                print(response)
                except messagebird.client.ErrorException as e:
                    print("Error al enviar la llamada:", e)
                    error_count += 1

            # Enviar llamadas a grupos
            for group in groups_list:
                print(f"Enviando llamada al grupo: {group}")
                try:
                    whatsapp_group = WhatsappGroup.objects.get(groupname=group.strip())
                    print(f"Grupo encontrado: {whatsapp_group}")
                    for number in whatsapp_group.members.split(","):
                        print(f"Llamando a {number}")
                        try:
                            callFlow = {
                                'source': '5493518008514',  # Reemplaza 'YOUR_CALLER_ID' con tu propio ID de llamante
                                'destination': number,
                                'callFlow': {
                                    'steps': [
                                        {
                                            'action': 'say',
                                            'options': {
                                                'payload': phone_call.message,
                                                'language': 'es-mx',
                                                'voice': 'female'
                                            }
                                        }
                                    ]
                                }
                            }

                            response = client.call_create(**callFlow)
                            success_count += 1
                            print(response)
                        except messagebird.client.ErrorException as e:
                            print("Error al enviar la llamada:", e)
                            error_count += 1
                except WhatsappGroup.DoesNotExist:
                    print(f"Grupo no encontrado: {group.strip()}")
                    error_count += 1

            # Marca la llamada como completada
            phone_call.datecompleted = timezone.now()
            phone_call.save()

        return JsonResponse({'mensaje': 'Llamadas enviadas exitosamente: {}'.format(success_count),
                             'errores': error_count})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})
    


@csrf_exempt
def send_whatsapp_alerts(request):
    if request.method == 'POST':
        selected_alert_ids = request.POST.getlist('selected_alerts[]')

        # URL y encabezados de la solicitud a la API de Facebook
        url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
        headers = {
            'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

        for alert_id in selected_alert_ids:
            try:
                alert = WhatsappAlert.objects.get(id=alert_id)

                # Construir el mensaje de WhatsApp
                message = f"{alert.body}"

                # Obtener la lista de destinatarios, que incluye tanto 'to' como los miembros de grupos
                recipients = []
                recipients.extend(alert.to.split(",") if alert.to else [])
                for group in alert.groups.all():
                    recipients.extend(group.members.split(","))

                # Enviar mensajes de WhatsApp a cada destinatario
                for recipient in recipients:
                    if recipient:
                        data = {
                            "messaging_product": "whatsapp",
                            "to": recipient,
                            "type": "template",
                            "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                            "template": {
                                "name": "notificaciones_marketing",
                                "language": {
                                    "code": "es_AR"
                                },
                                "components": [
                                    {
                                        "type": "body",
                                        "parameters": [
                                            {
                                                "type": "text",
                                                "text": message
                                            }
                                        ]
                                    }
                                ]
                            }
                        }

                        response = requests.post(url, headers=headers, json=data)
                        print(response)
                        print(response.json())
                        if response.status_code == 200:
                            # Incrementar el contador de envíos y actualizar la fecha del último envío
                            alert.increase_sent_count()
                    else:
                        print("Destinatario no válido:", recipient)

            except WhatsappAlert.DoesNotExist:
                # Manejar el caso en que la alerta no exista en la base de datos
                print(f"La alerta con ID {alert_id} no existe en la base de datos.")

        return redirect('whatsapp_alerts')
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})
    
@csrf_exempt
def send_mail_alerts(request):
    if request.method == 'POST':
        selected_alert_ids = request.POST.getlist('selected_alerts[]')

        for alert_id in selected_alert_ids:
            try:
                alert = MailAlert.objects.get(id=alert_id)

                # Construir el correo electrónico
                email_subject = alert.subject
                email_body = alert.body

                # Obtener la lista de destinatarios, que incluye tanto 'address' como los miembros de grupos
                recipients = []
                recipients.extend(alert.address.split(",") if alert.address else [])
                for group in alert.groups.all():
                    group_members = group.members.split(",")
                    recipients.extend(group_members)

                # Enviar correos electrónicos a cada destinatario
                for recipient in recipients:
                    if recipient:
                        email_data = {
                            "from": "notificaciones@guayini.com",
                            "to": recipient.strip(),  # Limpiar espacios en blanco
                            "subject": email_subject,
                            "html": email_body,
                            # Puedes agregar más campos o personalización aquí según tus necesidades
                        }

                        # Define la URL de la API para enviar correos electrónicos
                        api_url = "https://api.envialosimple.email/api/v1/mail/send"

                        # Define las cabeceras de la solicitud
                        headers = {
                            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE2OTUyMzQyODQsImV4cCI6NDg1MDkwNzg4NCwicm9sZXMiOlsiUk9MRV9BRE1JTiIsIlJPTEVfVVNFUiJdLCJraWQiOiI2NTBiMzhlYzk3OTE2MjFmMWMwNmMyODAiLCJhaWQiOiI2NGZmMmVjMTdiMTdmZmVhNDYwMzQ2ZTgiLCJ1c2VybmFtZSI6ImJyaWFuXzExXzkyQGhvdG1haWwuY29tIn0.eJVeRQBypyAYjj9Eu3iLCSggDlOb4cIr4r-3-liCLTothyuZyWgXrF_I6cncLBylzrWMY2YUuwI_EbWUPKxTFvTy5_SivjCABBYyvoMljnDtVMgYYbWu0D0n1IBBvLiP51s1BpY-znza-wEZWntBpayLF3guH_0dUJM9GWAr-3mszyQ9udfpaU7QnQKRgkz24sH91HkVSoitXypqto23B-nF_doLKr6GPo9WjcUEjmg-jnc_u764AiGgdXcB-xBYWlv3p7OhQG2qRsIqYC9hfN5UfaeQMIAiw8PExkSQ5O_U1d5uNQesX1kYF6XArKUOlGNbxPDeBrnEbwBjtQnO0w',  # Reemplaza con tu token
                            'Content-Type': 'application/json'
                        }

                        # Convierte los datos a formato JSON
                        payload = json.dumps(email_data)

                        # Realiza la solicitud POST a la API de EnvialoSimple
                        response = requests.post(api_url, headers=headers, data=payload)

                        print(response.status_code)
                        print(response.json())

                        if response.status_code == 200:
                            # Incrementar el contador de envíos y actualizar la fecha del último envío
                            alert.increase_sent_count()
                        
                    else:
                        print("Dirección de correo no válida:", recipient)

            except MailAlert.DoesNotExist:
                # Manejar el caso en que la alerta de correo no exista en la base de datos
                print(f"La alerta de correo con ID {alert_id} no existe en la base de datos.")

        return redirect('mail_alerts')
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})
    
@csrf_exempt
def send_phone_alerts(request):
    if request.method == 'POST':
        selected_alert_ids = request.POST.getlist('selected_alerts[]')

        for alert_id in selected_alert_ids:
            try:
                alert = PhoneAlert.objects.get(id=alert_id)

                # Construir el mensaje de la llamada
                phone_message = alert.body

                # Obtener la lista de destinatarios, que incluye tanto 'to' como los miembros de grupos
                recipients = []
                recipients.extend(alert.to.split(",") if alert.to else [])
                for group in alert.groups.all():
                    group_members = group.members.split(",")
                    recipients.extend(group_members)

                # Inicializar contadores para el éxito y errores
                success_count = 0
                error_count = 0

                # Enviar llamadas telefónicas a cada destinatario
                for recipient in recipients:
                    if recipient:
                        try:
                            # Configurar los detalles de la llamada a través de la API de MessageBird
                            call_payload = {
                                "source": '5493518008514',  # Reemplaza con tu propio ID de llamante
                                "destination": recipient,
                                "voice": "female",
                                "language": "es-MX",
                                "ifMachine": "continue",  # Continuar la llamada si se detecta una máquina
                                "record": "true",  # Grabar la llamada (opcional)
                                "message": phone_message,
                            }

                            # Configura las cabeceras de la solicitud a la API de MessageBird
                            headers = {
                                'Authorization': 'AccessKey MESSAGEBIRD_ACCESS_KEY',  # Reemplaza con tu propia clave de acceso de MessageBird
                                'Content-Type': 'application/json',
                            }

                            # Define la URL de la API de MessageBird para crear llamadas
                            api_url = "https://voice.messagebird.com/calls"

                            # Realiza la solicitud POST para crear la llamada
                            response = requests.post(api_url, headers=headers, json=call_payload)

                            if response and response.status_code == 201:
                                # Incrementar el contador de envíos y actualizar la fecha del último envío
                                alert.increase_sent_count()
                                success_count += 1
                            else:
                                print(f"Error al enviar la llamada a {recipient}: {response.text}")
                                error_count += 1

                        except Exception as e:
                            print(f"Error al enviar la llamada a {recipient}: {str(e)}")
                            error_count += 1

                    else:
                        print("Número de teléfono no válido:", recipient)

                print(f"Llamadas enviadas exitosamente: {success_count}")
                print(f"Errores en el envío de llamadas: {error_count}")

            except PhoneAlert.DoesNotExist:
                print(f"La alerta de llamada con ID {alert_id} no existe en la base de datos.")

        return redirect('phone_alerts')
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})

@login_required
def send_whatsapp(request, number, message):
    #messenger = WhatsApp(settings.FACEBOOK_AUTH_TOKEN,settings.FACEBOOK_SENDER_NUMBER_1)
    # Numero de telefono a donde enviar el mensaje 
    destinyNumber = int(number)
    messageToSend = message
    # For sending a Text message
    #messenger.send_message(mensaje, str(to))
    # Guardar mensaje enviado en la base de datos --- modificar para que se mande con request y no con heyoo
    # Enviar el mensaje usando la API de Facebook
    url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
    headers = {
        'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }

    #Busco el ultimo mensaje enviado por el usuario a este numero. Si pasaron + de 24 hs o no hay mensajes debo enviar un 
    # mensaje del tipo template
    try:
        ultimo_mensaje = Task.objects.filter(user=request.user, to=destinyNumber).latest('created')
        print(ultimo_mensaje)

    except Task.DoesNotExist:
                # Maneja el caso si el mensaje no existe en la base de datos
                ultimo_mensaje = None
    # Datos del mensaje a enviar
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": destinyNumber,
        "type": "text",
        "text": { 
            "body": messageToSend
        }
    }

    tz = pytz.timezone('UTC')
    
    if ultimo_mensaje is None or (datetime.now(tz) - ultimo_mensaje.created >= timedelta(hours=24)):
        data = {
                        "messaging_product": "whatsapp",
                        "to": destinyNumber,
                        "type": "template",
                        "sender": settings.FACEBOOK_SENDER_NUMBER_1,
                        "template": {
                            "name": "blank_template",
                            "language": {
                                "code": "es_AR"
                            },
                            "components": [
                                {
                                    "type": "body",
                                    "parameters": [
                                        {
                                            "type": "text",
                                            "text": messageToSend
                                        }
                                    ]
                                }
                            ]
                        }
                }

    # Enviar el mensaje usando la API de Facebook
    response = requests.post(url, headers=headers, json=data)
    print('Respuesta de Facebook:')
    print(response.text)    

    if response.status_code == 200:
        # El mensaje se envió correctamente, puedes asignar los valores correspondientes al mensaje en tu base de datos
        response_data = response.json()
        if "messages" in response_data and len(response_data["messages"]) > 0:
            message_id = response_data["messages"][0]["id"]
        else: 
            message_id = 0
        mensaje = Task.objects.create(
            wamID=message_id,
            tittle='',
            message=messageToSend,
            status='sent',
            created=datetime.now(),
            Type='text',
            datecompleted=None,
            dateprogramed=None,
            important=False,
            to=destinyNumber,
            sender=settings.FACEBOOK_SENDER_NUMBER_1,
            groups='',
            user=request.user
        )
        mensaje.save()
        print(f"Mensaje {message_id} procesado y guardado en la base de datos.")
        return JsonResponse({'message': 'mensaje enviado'})
    else:
        # Ocurrió un error al enviar el mensaje
        # Puedes manejar el error de acuerdo a tus necesidades
        pass

@csrf_exempt
def receive_whatsapp(request):
    if request.method == 'GET':
        # VERIFICACION FACEBOOK
        # Obtiene los parámetros de consulta de la URL
        hub_mode = request.GET.get('hub.mode')
        hub_challenge = request.GET.get('hub.challenge')
        hub_verify_token = request.GET.get('hub.verify_token')

        # Verifica el valor de hub.verify_token con tu cadena de token configurada
        if hub_verify_token == 'TOKENTEST':
            # Responde con el valor hub.challenge para completar la verificación
            return HttpResponse(hub_challenge, content_type='text/plain')
        else:
            # Si el token de verificación no coincide, responde con un código de estado 403 (Prohibido)
            return HttpResponse(status=403)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        print(request.POST)

        # Verifica si es una respuesta a un mensaje enviado previamente
        if 'statuses' in data['entry'][0]['changes'][0]['value']:
            # Es una respuesta a un mensaje enviado previamente
            print("Es una actualizacion de estado de un mensaje anterior")
            message_id = data['entry'][0]['changes'][0]['value']['statuses'][0]['id']
            status = data['entry'][0]['changes'][0]['value']['statuses'][0]['status']

            # Busca el mensaje en tu base de datos usando el campo wamID
            try:
                mensaje = Task.objects.get(wamID=message_id)
                mensaje.status = status
                mensaje.save()
            except Task.DoesNotExist:
                # Maneja el caso si el mensaje no existe en la base de datos
                pass
        else:
            # Es una notificación de un nuevo mensaje recibido
            wa_id = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
            message_id = data['entry'][0]['changes'][0]['value']['messages'][0]['id']

            # Verificar si el ID del mensaje ya ha sido procesado
            if Task.objects.filter(wamID=message_id).exists():
                print(f"Mensaje {message_id} ya ha sido procesado. Ignorando...")
                return HttpResponse(status=200)  # Omitir el procesamiento si ya existe

            timestamp = int(data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp'])
            message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            status = 'received'

            #Tomamos el numero de telefono y el mensaje
            _from = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            mensaje = "Telefono:"+data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            mensaje+= "| Mensaje:"+message_text

            print(f"Mensaje recibido:" + mensaje)
            user = User.objects.get(username="facebook") 

            # Crea una nueva instancia del modelo Task y guarda los datos
            mensaje = Task(
                wamID=message_id,
                tittle='',
                message=message_text,
                status=status,
                created=datetime.fromtimestamp(timestamp),
                Type='',
                datecompleted=None,
                dateprogramed=None,
                important=False,
                to=wa_id,
                sender=_from,
                groups='',
                user=user
            )
            mensaje.save()
            print(f"Mensaje {message_id} procesado y guardado en la base de datos.")
        
        channel_layer = get_channel_layer()
        print(channel_layer)
        async_to_sync(channel_layer.group_send)(
        'tasks',
        {
            'type': 'send_message',
            'message': mensaje.message,
        }
    )
        return HttpResponse(status=200)
    else:
        # Responde con un código de estado 405 (Método no permitido) para otras solicitudes HTTP
        return HttpResponse(status=405)

def get_messages(request, contact_number):
    # Realiza la consulta en la base de datos para recuperar los mensajes
    messages = Task.objects.filter(Q(to=contact_number) | Q(sender=contact_number)).order_by('created')
    # Puedes serializar los mensajes si es necesario
    serialized_messages = [{'message': msg.message, 'status': msg.status, 'created':msg.created} for msg in messages]
    
    return JsonResponse(serialized_messages, safe=False)


