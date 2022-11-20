from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from registrations.models import PendingEmail, UnverifiedUser
from info.views import update_db_from_cache

def send_verification_emails():
    entries = PendingEmail.objects.all()
    connection = mail.get_connection(fail_silently=False)
    connection.open()
    from_email= settings.EMAIL_HOST_USER
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
                    context['members_count'] = entry.members_count
                    context['total_fees'] = entry.team_amount + (entry.fees_per_member*entry.members_count)
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
        email = EmailMultiAlternatives(subj, mesg, from_email, [entry.email])
        email.attach_alternative(html_message, 'text/html')
        connection.send_messages([email])
        # send_mail(subj, mesg, from_email, [entry.email,],html_message=html_message, fail_silently=False)
        entry.delete()
    connection.close()

def add_all_unverified_to_pending_mails():
    users = UnverifiedUser.objects.all()
    for user in users:
        entry = PendingEmail(email=user.email, is_main=True, slug=user.slug)
        entry.save()
    update_db_from_cache()
