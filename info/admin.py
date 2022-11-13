from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin

from .models import Query, Sponsor, VerifyEndpoint

# Register your models here.

class QueryResource(ModelResource):
    class Meta:
        model = Query

class SponsorResource(ModelResource):
    class Meta:
        model = Sponsor

class VerifyResource(ModelResource):
    class Meta:
        model = VerifyEndpoint

class QueryAdmin(ImportExportModelAdmin):
    resource_class = QueryResource
    list_display = ['id', 'name', 'email', 'phone_no']
    list_display_links = ['id', 'name']
    list_per_page = 50
    search_fields = ['email', 'name', 'phone_no']

class SponsorAdmin(ImportExportModelAdmin):
    resource_class = SponsorResource
    list_display = ['id', 'name']
    list_display_links = ['id', 'name']

class VerifyAdmin(ImportExportModelAdmin):
    resource_class = VerifyResource
    list_display = ['id', 'endpoint', 'user', 'event']
    list_display_links = ['id', 'endpoint']
    search_fields = ['user__email', 'event__name']

admin.site.register(Query, QueryAdmin)
admin.site.register(Sponsor, SponsorAdmin)
admin.site.register(VerifyEndpoint, VerifyAdmin)

admin.site.login_template = 'info/login.html'
