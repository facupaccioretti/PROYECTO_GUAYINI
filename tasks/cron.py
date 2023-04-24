import os
import django
from django.conf import settings
from django.core.wsgi import get_wsgi_application
from django.utils import timezone
from datetime import datetime
import requests
from twilio.rest import Client


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "GUAYINI.settings")
django.setup()
application = get_wsgi_application()

from models import Task

def send_scheduled_messages():
    # Obtiene todas las tareas programadas que aún no se han completado
    tasks = Task.objects.filter(dateprogramed__lte=timezone.now(), datecompleted=None)

    # Envía los mensajes de WhatsApp
    for task in tasks:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=task.message,
            from_='whatsapp:' + settings.TWILIO_WHATSAPP_NUMBER,
            to=f'whatsapp:+5493515927657' # PROXIMAMENTE: {request.user.profile.phone_number}'
        )
        # Marca la tarea como completada
        task.datecompleted = timezone.now()
        task.save()

    return

send_scheduled_messages()