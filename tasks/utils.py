import requests
from datetime import datetime
from .models import Task  # Asegúrate de importar el modelo correcto para tus mensajes

def enviar_mensaje(bot, message_text):
    # URL y encabezados de la solicitud a la API de Facebook
    url = f'https://graph.facebook.com/v17.0/{settings.FACEBOOK_SENDER_NUMBER_1}/messages'
    headers = {
        'Authorization': f'Bearer {settings.FACEBOOK_AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }

    # Datos del mensaje a enviar
    data = {
        "messaging_product": "whatsapp",
        "to": bot.to,  # Aquí deberías especificar el número al que deseas enviar el mensaje
        "type": "text",
        "text": message_text,
        "sender": settings.FACEBOOK_SENDER_NUMBER_1,
    }

    # Enviar el mensaje usando la API de Facebook
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        # El mensaje se envió correctamente, puedes asignar los valores correspondientes al mensaje en tu base de datos
        response_data = response.json()
        message_id = response_data['messages'][0]['id']
        mensaje = Task.objects.create(
            wamID=message_id,
            tittle='',
            message=message_text,
            status='sent',
            created=datetime.now(),
            type='text',  # Cambia esto según el tipo de mensaje que estás enviando
            datecompleted=None,
            dateprogramed=None,
            important=False,
            to=bot.to,
            sender=settings.FACEBOOK_SENDER_NUMBER_1,
            groups='',
            user=bot.user
        )
    else:
        # Ocurrió un error al enviar el mensaje
        # Puedes manejar el error de acuerdo a tus necesidades
        pass

