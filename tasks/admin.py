from django.contrib import admin
from .models import Task, Mail, Phone, WhatsappGroup, MailGroup, PhoneGroup

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

class MailAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

class PhoneAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

class WhatsappGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

class MailGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

class PhoneGroupAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

# Register your models here.

admin.site.register(Task, TaskAdmin)

admin.site.register(Mail, MailAdmin)

admin.site.register(Phone, PhoneAdmin)

admin.site.register(WhatsappGroup, WhatsappGroupAdmin)

admin.site.register(MailGroup, MailGroupAdmin)

admin.site.register(PhoneGroup, PhoneGroupAdmin)

