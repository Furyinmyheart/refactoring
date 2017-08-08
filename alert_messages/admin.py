from django.contrib import admin

from alert_messages.models import Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ('date_send', 'from_user', 'text', 'is_read',)


admin.site.register(Message, MessageAdmin)
