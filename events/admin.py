from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Event

# Register your models here.

class EventResource(ModelResource):
    class Meta:
        model = Event

class EventAdmin(ImportExportModelAdmin):
    resource_class = EventResource
    list_display = ['id', 'name', 'date', 'time', 'intra_thapar', 'usersRegistered']
    list_display_links = ['id', 'name']
    list_filter = ['intra_thapar']
    list_per_page = 100

    def usersRegistered(self, obj):
        return obj.users.count()

admin.site.register(Event, EventAdmin)