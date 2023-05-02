from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm, MailForm, PhoneForm, WhatsappGroupForm, MailGroupForm, PhoneGroupForm
from .models import Mail, Task, Phone, WhatsappGroup, MailGroup, PhoneGroup
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime, timedelta
import pytz
from django.shortcuts import render
from twilio.rest import Client
from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect




# Agregar esta línea para definir el timezone por defecto
timezone.activate(pytz.timezone('America/Argentina/Buenos_Aires'))

# Create your views here.
@login_required
def groups(request):
    whatsappgroups = WhatsappGroup.objects.filter(user=request.user)
    mailgroups = MailGroup.objects.filter(user=request.user)
    phonegroups = PhoneGroup.objects.filter(user=request.user)
    return render(request, "groups.html", {'whatsappgroups': whatsappgroups, 'mailgroups': mailgroups, 'phonegroups': phonegroups})

@login_required
def create_groups(request): 
        return render(request, 'create_groups.html')


def landing(request): 
    return render(request, "landing.html")

def home(request): 
    return render(request, "home.html")

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

@csrf_protect
def signin(request):
    if request.method == 'GET':
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
            return redirect('calendar')

@login_required
def signout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    user = request.user
    context = {'user': user,}
    return render(request, 'profile.html',)

#NOTIFICATION VIEWS
    # WHATSAPP VIEWS:
@login_required       
def tasks(request):
    tasks = Task.objects.filter(user=request.user)
    
    return render(request, 'tasks.html', {'tasks': tasks})

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
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
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
    mails = Mail.objects.filter(user=request.user)    
    return render(request, 'mails.html', {'mails': mails})

@login_required
def create_mail(request):
    if request.method == "GET": 
        return render(request, 'create_mails.html', {"form": MailForm})
    else:
        try:
            form = MailForm(request.POST)
            new_mail = form.save(commit=False)
            new_mail.user = request.user
            new_mail.save()
            return redirect('mails')
        except ValueError:
            return render(request, 'create_mails.html', {"form": MailForm, "error": "Error creating mail."})

@login_required
def mails_completed(request):
    mails = Mail.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    
    return render(request, 'mails.html', {'mails': mails})

@login_required        
def mail_detail(request, mail_id):
    if request.method == 'GET':
        mail = get_object_or_404(Mail, pk=mail_id, user=request.user)
        form = MailForm(instance=mail)
        return render(request, 'mail_detail.html', {'mail': mail, 'form': form})
    else:
        try:
            mail = get_object_or_404(Mail, pk=mail_id, user=request.user)
            form = MailForm(request.POST, instance=mail)
            form.save()
            return redirect('mails')
        except ValueError:
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
    return render(request, 'phones.html', {'phones': phones})

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



def send_whatsapp_message(request):
    if request.method == 'POST':
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        client = Client(account_sid, auth_token)
        
        to = request.POST.get('to')
        body = request.POST.get('body')
        
        message = client.messages.create(
            from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
            body=body,
            to='whatsapp:' + to
        )
        
        return redirect('success')
    
    return render(request, 'send_message.html')

def success(request):
    return render(request, 'successWhatsapp.html')


@login_required
def send_scheduled_messages(request):
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
        numbers = task.to.split(",")  # separar los números por coma
        for number in numbers:
            message = client.messages.create(
                body=task.message,
                from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
                to=f'whatsapp:' + number.strip()  # eliminar espacios en blanco en el número
            )
        # Marca la tarea como completada
        task.datecompleted = timezone.now()
        task.save()

    return redirect('tasks')




@csrf_exempt
def enviar_mensaje_curl(request):
    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        numero = request.POST.get('numero') or request.FILES.get('numero')

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        if numero is None:
            return JsonResponse({'mensaje': 'Numero de telefono faltante'}, status=400)
        message = client.messages.create(
            body=mensaje,
            from_='whatsapp:+14155238886',
            to=f'whatsapp:' + numero
        )

        return JsonResponse({'mensaje': 'Mensaje enviado exitosamente'})
    else:
        return JsonResponse({'mensaje': 'Método no permitido'})
    

