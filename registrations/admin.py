from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field

from .models import User, UnverifiedUser, PendingEmail

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

    list_display = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college', 'events_name')
    list_display_links = ('id', 'email')
    list_filter = ('is_thaparian',)
    list_per_page = 100
    search_fields = ('email', 'name', 'phone_no', 'roll_no', 'college')

    def events_name(self, user):
        evs = ""
        for queryset in [user.event_registrations.all(), user.leader_team_set.all(), user.team_set.all()]:
            for item in queryset:
                evs = evs + item.event.name + ", "
        return evs

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
        fields = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college')
        export_order = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college')

class UnverifiedUserAdmin(ImportExportModelAdmin):
    resource_class = UnverifiedUserResource
    list_display = ('id', 'email', 'name', 'phone_no', 'is_thaparian', 'roll_no', 'college', 'slug')
    list_per_page = 100
    search_fields = ('email', 'name', 'phone_no', 'roll_no', 'college', 'slug')

class PendingEmailModelResource(ModelResource):
    class Meta:
        model = PendingEmail

class PendingEmailAdmin(ImportExportModelAdmin):
    resource_class = PendingEmailModelResource
    list_display = ('id', 'email', 'is_main', 'is_event', 'is_create_team', 'is_join_team')
    list_per_page = 100
    search_fields = ('email',)

admin.site.register(User, UserModelAdmin)
# admin.site.register(EmailVerification, EmailVerificationAdmin)
admin.site.register(UnverifiedUser, UnverifiedUserAdmin)
admin.site.register(PendingEmail, PendingEmailAdmin)