from django.contrib import admin
from .models import Task, Mail, Phone, WhatsappGroup, MailGroup, PhoneGroup, Bots, Contact, Alert, Group, AccessToken


class ReadOnlyCreatedAdmin(admin.ModelAdmin):
    readonly_fields = ("created", )

class TaskAdmin(ReadOnlyCreatedAdmin):
    pass

class MailAdmin(ReadOnlyCreatedAdmin):
    pass

class PhoneAdmin(ReadOnlyCreatedAdmin):
    pass

class WhatsappGroupAdmin(ReadOnlyCreatedAdmin):
    pass

class MailGroupAdmin(ReadOnlyCreatedAdmin):
    pass

class PhoneGroupAdmin(ReadOnlyCreatedAdmin):
    pass

class BotsAdmin(ReadOnlyCreatedAdmin):
    pass

class ContactAdmin(ReadOnlyCreatedAdmin):
    pass

class AlertAdmin(ReadOnlyCreatedAdmin):
    pass

class GroupAdmin(ReadOnlyCreatedAdmin):
    pass

class AccessTokenAdmin(ReadOnlyCreatedAdmin):
    pass

# Register your models here.

admin.site.register(Task, TaskAdmin)
admin.site.register(Mail, MailAdmin)
admin.site.register(Phone, PhoneAdmin)
admin.site.register(WhatsappGroup, WhatsappGroupAdmin)
admin.site.register(MailGroup, MailGroupAdmin)
admin.site.register(PhoneGroup, PhoneGroupAdmin)
admin.site.register(AccessToken, AccessTokenAdmin)
admin.site.register(Alert, AlertAdmin)
admin.site.register(Bots, BotsAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Contact, ContactAdmin)
