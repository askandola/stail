from apscheduler.schedulers.background import BackgroundScheduler
from .job import send_verification_emails

def schedule_job():
    scheduler = BackgroundScheduler(daemon=True)
    all_jobs = scheduler.get_jobs()
    for job in all_jobs:
        try:
            scheduler.remove_job(job.id)
        except:
            pass
    scheduler.add_job(send_verification_emails, 'interval', minutes=30, replace_existing=True, id="send_mails")
    print('schedule')
    scheduler.start()
