from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from .models import User 
from .models import UnverifiedUser

# Register your models here.

class UserResource(ModelResource):
    events_registered = Field()
    
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college')
        export_order = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college', 'events_registered')
    
    def dehydrate_events_registered(self, user):
        evs = ""
        for queryset in [user.event_registrations.all(), user.leader_team_set.all(), user.team_set.all()]:
            for item in queryset:
                name = getattr(item.event, "name", "unknown")
                evs = evs + name + ", "
        return evs

class UserModelAdmin(ImportExportModelAdmin):
    resource_class = UserResource

    list_display = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college', 'events_count')
    list_display_links = ('id', 'email')
    list_filter = ('is_thaparian',)
    list_per_page = 50
    search_fields = ('email', 'name', 'phone_no', 'roll_no', 'college')

    def events_count(self, item):
        return item.event_registrations.count()+item.leader_team_set.count()+item.team_set.count()

# class EmailVerificationResource(ModelResource):
#     class Meta:
#         model = EmailVerification

# class EmailVerificationAdmin(ImportExportModelAdmin):
#     resource_class = EmailVerificationResource
#     list_display = ('id', 'slug', 'user')
#     list_per_page = 50
#     search_fields = ('user__email', 'slug')

class UnverifiedUserResource(ModelResource):
    class Meta:
        model = UnverifiedUser

class UnverifiedUserAdmin(ImportExportModelAdmin):
    resource_class = UnverifiedUserResource
    list_display = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college', 'slug')
    list_per_page = 50
    search_fields = ('email', 'name', 'phone_no', 'roll_no', 'college', 'slug')

admin.site.register(User, UserModelAdmin)
# admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(UnverifiedUser, UnverifiedUserAdmin)