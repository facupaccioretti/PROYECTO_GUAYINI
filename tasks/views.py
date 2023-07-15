from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm, MailForm, PhoneForm, WhatsappGroupForm, MailGroupForm, PhoneGroupForm
from .models import Mail, Task, Phone, WhatsappGroup, MailGroup, PhoneGroup, AccessToken
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
import messagebird
from messagebird.conversation_message import MESSAGE_TYPE_HSM 
from messagebird.conversation_message import MESSAGE_TYPE_TEXT
import json
import requests
from django.utils.crypto import get_random_string
import time
from django.views.decorators.csrf import csrf_exempt
from .models import AccessToken
import requests
from django.conf import settings
from django.http import JsonResponse


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
    try:
        token = AccessToken.objects.get(user=request.user).token
    except AccessToken.DoesNotExist:
        token = None
    return render(request, 'profile.html', {'token': token})

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
        groups = task.groups.split(";")
        for group in groups:
            print(f"Procesando grupo {group}")
            try:
                whatsapp_group = WhatsappGroup.objects.get(groupname=group.strip())
                print(f"Grupo encontrado: {whatsapp_group}")
                for number in whatsapp_group.members.split(";"):
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
        token_obj = get_object_or_404(Token, token=token)
        user = token_obj.user

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
            print(response)

            if response.status_code == 200:
                success_count += 1
                # Aquí asignamos los valores correspondientes al mensaje en tu base de datos
                mensaje = Task.objects.create(
                    wamID=response.json().get('id'),
                    tittle='',
                    message=mensaje,
                    status='sent',
                    created=datetime.now(),
                    type='template',
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

            # Obtener los miembros del grupo (puedes implementar tu lógica aquí)

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
                    mensaje = Task.objects.create(
                        wamID=response.json().get('id'),
                        tittle='',
                        message=mensaje,
                        status='sent',
                        created=datetime.now(),
                        type='template',
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
    #VERIFICACION FACEBOOK
    if request.method == 'GET':
        # Obtiene los parámetros de consulta de la URL
        hub_mode = request.GET.get('hub.mode')
        hub_challenge = request.GET.get('hub.challenge')
        hub_verify_token = request.GET.get('hub.verify_token')

        # Verifica el valor de hub.verify_token con tu cadena de token configurada
        if hub_verify_token == 'guayini_token_aguantebelgrano':
            # Responde con el valor hub.challenge para completar la verificación
            return HttpResponse(hub_challenge, content_type='text/plain')
        else:
            # Si el token de verificación no coincide, responde con un código de estado 403 (Prohibido)
            return HttpResponse(status=403)
    

    #WEBHOOK PARA ADQUIRIR DATA DE FACEBOOK
    elif request.method == 'POST':
        data = json.loads(request.body)

        # Verifica si es una respuesta a un mensaje enviado previamente
        if 'statuses' in data['entry'][0]['changes'][0]['value']:
            # Extrae los datos relevantes de la respuesta
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
            timestamp = int(data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp'])
            message_text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            status = 'received'

            # Crea una nueva instancia del modelo Task y guarda los datos
            mensaje = Task(
                wamID=message_id,
                tittle='',
                message=message_text,
                status=status,
                created=datetime.fromtimestamp(timestamp),
                type='',
                datecompleted=None,
                dateprogramed=None,
                important=False,
                to=wa_id,
                sender='',
                groups='',
                user=request.user
            )
            mensaje.save()

        return HttpResponse(status=200)
    
    #ERROR PARA OTRAS SOLICITUDES HTTP
    else:
        # Responde con un código de estado 405 (Método no permitido) para otras solicitudes HTTP
        return HttpResponse(status=405)


