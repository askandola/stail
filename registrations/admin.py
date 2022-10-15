from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin

from .models import User

# Register your models here.

class UserResource(ModelResource):
    class Meta:
        model = User
        fields = '__all__'

class UserModelAdmin(ImportExportModelAdmin):
    resource_class = UserResource

    list_display = ('id', 'email', 'name', 'college')
    list_display_links = ('id', 'email')
    list_filter = ('is_thaparian',)
    list_per_page = 50

admin.site.register(User, UserModelAdmin)