from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from registrations.models import PendingEmail, UnverifiedUser
from events.models import Team, EventUserTable
from info.views import update_db_from_cache
from registrations.serializers import UserSerializer
from django.core.cache import cache

EMAIL_HOST_USERS = [settings.EMAIL_HOST_USER1, settings.EMAIL_HOST_USER2, settings.EMAIL_HOST_USER3]
EMAIL_HOST_PASSWORDS = [settings.EMAIL_HOST_PASSWORD1, settings.EMAIL_HOST_PASSWORD2, settings.EMAIL_HOST_PASSWORD3]

def send_verification_emails():
    curr = cache.get('currentEmailIndex', 0)
    entries = PendingEmail.objects.all()
    print(entries, curr)
    connection = mail.get_connection(username=EMAIL_HOST_USERS[curr], password=EMAIL_HOST_PASSWORDS[curr], fail_silently=False)
    connection.open()
    from_email= EMAIL_HOST_USERS[curr]
    for entry in entries:
        if entry.is_event:
            context = {'eventName': entry.event}
            if entry.is_create_team:
                context['createTeam'] = True
                context['teamName'] = entry.team_name
                context['teamKey'] = entry.team_key
                if entry.fees_required:
                    context['fees_required'] = True
                    context['fees_message'] = True
                    context['team_amount'] = entry.team_amount
                    context['fees_per_member'] = entry.fees_per_member
                    if context['eventName']=='Battle of the Bands':
                        context['members_count'] = entry.members_count if entry.members.count>8 else 0
                        context['total_fees'] = entry.team_amount + (entry.fees_per_member*context['members_count'])
                    else:
                        context['members_count'] = entry.members_count
                        context['total_fees'] = entry.team_amount + (entry.fees_per_member*entry.members_count)
                    context['ignoreMessage'] = entry.ignore_message
            elif entry.is_join_team:
                context['joinTeam'] = True
                context['teamName'] = entry.team_name
                if entry.fees_required:
                    context['fees_required'] = True
                    context['fees_reminder'] = True
            elif entry.fees_required:
                context['fees_required'] = True
                context['fees_message'] = True
                context['individual_fees'] = entry.individual_fees
                context['ignoreMessage'] = entry.ignore_message
            if entry.qr_url!=None and entry.qr_url!='':
                context['qr_url'] = entry.qr_url
            subj = f"Thank you for registering for {entry.event}"
            html_message = render_to_string('events/mail.html', context)
            mesg = strip_tags(html_message)
        else:
            verification_url = 'https://api.saturnaliatiet.com/request7/verify/' + entry.slug
            context = {
                'verification_url': verification_url
            }
            if entry.main_vrf_skip:
                context['skip_verification'] = True
            html_message = render_to_string('registrations/reg.html', context)
            mesg = strip_tags(html_message)
            subj = "Thank you for registering for Saturnalia'22"
        email = EmailMultiAlternatives(subj, mesg, from_email, [entry.email], cc=['mukundgupta1919@gmail.com'])
        email.attach_alternative(html_message, 'text/html')
        connection.send_messages([email])
        # send_mail(subj, mesg, from_email, [entry.email,],html_message=html_message, fail_silently=False)
        entry.delete()
    curr += 1
    curr %= 3
    cache.set('currentEmailIndex', curr)
    connection.close()

def clearEventsCache():
    cache.delete_many(['all', 'competitions', 'events'])

def add_all_unverified_to_pending_mails():
    users = UnverifiedUser.objects.all()
    for user in users:
        entry = PendingEmail(email=user.email, is_main=True, slug=user.slug)
        entry.save()
    update_db_from_cache()

def reminderForPayment():
    teams = Team.objects.filter(amount_paid=False).all()
    for team in teams:
        email = PendingEmail(email=team.leader.email)
        email.is_event = True
        email.event = team.event.name
        email.fees_required = True
        email.is_create_team = True
        email.team_name = team.name
        email.team_key = team.key
        email.team_amount = team.event.fees_amount
        email.fees_per_member = team.event.fees_per_member
        email.members_count = team.max_count
        email.ignore_message = True
        email.save()
    users = EventUserTable.objects.filter(amount_paid=False)
    for user in users:
        email = PendingEmail(email=user.user.email)
        email.is_event = True
        email.event = user.event.name
        email.fees_required = True
        email.individual_fees = user.event.fees_amount
        email.ignore_message = True
        email.save()

def move_to_verified():
    users = UnverifiedUser.objects.all()
    for user in users:
        data = UserSerializer(user).data.copy()
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            user.delete()
