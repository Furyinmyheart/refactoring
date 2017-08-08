from django.contrib import admin
from .models import Request, TyreVendor, TsMark, TsModel, RequestTaskLog, TaskHelpText


class TaskHelpTextAdmin(admin.ModelAdmin):
    list_display = ('error_text', 'help_text',)
    search_fields = ('error_text',)


admin.site.register(Request)
admin.site.register(TyreVendor)
admin.site.register(TsMark)
admin.site.register(TsModel)
admin.site.register(RequestTaskLog)
admin.site.register(TaskHelpText, TaskHelpTextAdmin)
