from django.contrib import admin
from stantions.models import Stantion, Expert


class ExpertInline(admin.StackedInline):
    model = Expert


class StantionAdmin(admin.ModelAdmin):
    list_display = ('org_title', 'reg_number', 'point_address', 'order', 'active',)
    list_filter = ('active', )
    search_fields = ('org_title', 'reg_number', 'point_address', )
    inlines = [
        ExpertInline,
    ]


admin.site.register(Stantion, StantionAdmin)
