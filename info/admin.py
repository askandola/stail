from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin

from .models import Query, Sponsor

# Register your models here.

class QueryResource(ModelResource):
    class Meta:
        model = Query

class SponsorResource(ModelResource):
    class Meta:
        model = Sponsor

class QueryAdmin(ImportExportModelAdmin):
    resource_class = QueryResource
    list_display = ['id', 'name', 'email', 'phone_no']
    list_display_links = ['id', 'name']
    list_per_page = 50

class SponsorAdmin(ImportExportModelAdmin):
    resource_class = SponsorResource
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']

admin.site.register(Query, QueryAdmin)
admin.site.register(Sponsor, SponsorAdmin)
