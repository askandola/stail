from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.resources import ModelResource

from .models import Event, Team, Rule, EventUserTable

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

class TeamResource(ModelResource):
    class Meta:
        model = Team

class TeamAdmin(ImportExportModelAdmin):
    resource_class = TeamResource
    list_display = ['id', 'name', 'key', 'event', 'leader']
    list_display_links = ['id', 'name']
    search_fields = ['leader__name', 'leader__email', 'event__name', 'name']
    list_filter = ['event', 'is_thapar_team']
    list_per_page = 100

class RuleResource(ModelResource):
    class Meta:
        model = Rule

class RuleAdmin(ImportExportModelAdmin):
    resource_class = RuleResource
    list_display = ['id', 'event', 'number']
    list_filter = ['event']
    list_per_page = 100

class EventUserTableAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'user']
    list_filter = ['event', 'user__is_thaparian']
    list_per_page = 100
    search_fields = ['event__name', 'user__email']

admin.site.register(Event, EventAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Rule, RuleAdmin)
admin.site.register(EventUserTable, EventUserTableAdmin)