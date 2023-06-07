"""GUAYINI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),
    path('signup/', views.signup, name='signup'),        
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='singin'),
    path('profile/', views.profile, name='profile'),
    path('groups/', views.groups, name='groups'),
    path('create_groups/', views.create_groups, name='create_groups'),
    # WHATSAPP GROUPS PATHS
    path('whatsappgroups/', views.whatsappgroups, name='whatsappgroups'),
    path('create_whatsappgroups/', views.create_whatsappgroups, name='create_whatsappgroups'),
    path('groups/<int:whatsappgroup_id>/', views.whatsappgroup_detail, name='whatsappgroup_detail'),
    path('groups/<int:whatsappgroup_id>/delete/', views.delete_whatsappgroup, name='delete_whatsappgroup'),
    # MAIL GROUPS PATHS
    path('mailgroups/', views.mailgroups, name='mailgroups'),
    path('create_mailgroups/', views.create_mailgroups, name='create_mailgroups'),
    path('groups/<int:mailgroup_id>/', views.mailgroup_detail, name='mailgroup_detail'),
    path('groups/<int:mailgroup_id>/delete/', views.delete_mailgroup, name='delete_mailgroup'),
    # PHONE GROUPS PATHS
    path('phonegroups/', views.phonegroups, name='phonegroups'),
    path('create_phonegroups/', views.create_phonegroups, name='create_phonegroups'),
    path('groups/<int:phonegroup_id>/', views.phonegroup_detail, name='phonegroup_detail'),
    path('groups/<int:phonegroup_id>/delete/', views.delete_phonegroup, name='delete_phonegroup'),
    # WHATSAPP NOTIFICATION PATHS
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/completed/', views.tasks_completed, name='task_completed'),
    path('create_tasks/', views.create_task, name='create_tasks'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    # MAIL NOTIFICATION PATHS
    path('mails/', views.mails, name='mails'),
    path('mails/completed', views.mails_completed, name='mail_completed'),
    path('create_mails/', views.create_mail, name='create_mails'),
    path('mails/<int:mail_id>/', views.mail_detail, name='mail_detail'),
    path('mails/<int:mail_id>/complete/', views.complete_mail, name='complete_mail'),
    path('mails/<int:mail_id>/delete/', views.delete_mail, name='delete_mail'),
    # PHONE NOTIFICATION PATHS
    path('phones/', views.phones, name='phones'),
    path('phones/completed', views.phones_completed, name='phone_completed'),
    path('create_phones/', views.create_phone, name='create_phones'),
    path('phones/<int:phone_id>/', views.phone_detail, name='phone_detail'),
    path('phones/<int:phone_id>/complete/', views.complete_phone, name='complete_phone'),
    path('phones/<int:phone_id>/delete/', views.delete_phone, name='delete_phone'),
    #CALENDAR PATH
    path('calendar/', views.calendar, name='calendar'),
    path('eventos/', views.get_eventos, name='eventos'),
    #WHATSAPP TWILLIO PATH
    path('send_message_twilio/', views.send_whatsapp_message_twilio, name='whatsapp_message_twilio'),
    path('success_message/', views.success, name='success'),
    path('send_scheduled_messages_twilio/', views.send_scheduled_messages_twilio, name='send_scheduled_messages_twilio'),
    path('enviar_mensaje_curl_twilio/', views.enviar_mensaje_curl_twilio, name='enviar_mensaje_twilio'),
    path('send_scheduled_messages_messagebird/', views.send_scheduled_messages_messagebird, name='send_scheduled_messages_messagebird'),
    path('send_scheduled_messages_messagebird_sandbox_HSM/', views.send_scheduled_messages_messagebird_sandbox_HSM, name='send_scheduled_messages_messagebird_sandbox_HSM'),
    path('send_scheduled_messages_messagebird_sandbox_TEXT/', views.send_scheduled_messages_messagebird_sandbox_TEXT, name='send_scheduled_messages_messagebird_sandbox_TEXT'),
    path('mesagebird_conversation_start/', views.mesagebird_conversation_start, name='mesagebird_conversation_start'),
    path('enviar_mensaje_curl/', views.enviar_mensaje_curl_messagebird, name='enviar_mensaje_curl_messagebird'),
    path('generate_token/', views.generate_token, name='generate_token'),
    path('recibir_webhook/', views.recibir_webhook, name='recibir_webhook'),
    path('enviar_llamada_curl/', views.enviar_llamada_curl_messagebird, name='enviar_llamada_curl_messagebird')
    
]
