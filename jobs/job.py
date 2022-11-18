from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from registrations.models import PendingEmail

def send_verification_emails():
    entries = PendingEmail.objects.all()
    print(entries)
    for entry in entries:
        verification_url = 'https://api.saturnaliatiet.com/request7/verify/' + entry.slug
        html_message = render_to_string('registrations/reg.html', {'verification_url': verification_url})
        mesg = strip_tags(html_message) #incase rendering fails
        subj = "Thank you for registering for Saturnalia'22"
        from_email= settings.EMAIL_HOST_USER
        send_mail(subj, mesg, from_email, [entry.email,],html_message=html_message, fail_silently=False)
        print(entry.email)
        entry.delete()
