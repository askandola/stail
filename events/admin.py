from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Event, Visit, Team, Rule

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

class VisitAdmin(admin.ModelAdmin):
    list_display = ['id', 'hits', 'event']

class TeamResource(ModelResource):
    class Meta:
        model = Team

class TeamAdmin(ImportExportModelAdmin):
    resource_class = TeamResource
    list_display = ['id', 'name', 'key', 'event', 'leader']
    list_display_links = ['id', 'name']
    list_filter = ['event']
    list_per_page = 100

class RuleResource(ModelResource):
    class Meta:
        model = Rule

class RuleAdmin(ImportExportModelAdmin):
    resource_class = RuleResource
    list_display = ['id', 'event', 'number']
    list_filter = ['event']
    list_per_page = 100

admin.site.register(Event, EventAdmin)
admin.site.register(Visit, VisitAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Rule, RuleAdmin)