from apscheduler.schedulers.background import BackgroundScheduler
from .job import send_verification_emails, add_all_unverified_to_pending_mails

def schedule_job():
    scheduler = BackgroundScheduler(daemon=True)
    all_jobs = scheduler.get_jobs()
    for job in all_jobs:
        try:
            scheduler.remove_job(job.id)
        except:
            pass
    scheduler.add_job(send_verification_emails, 'interval', seconds=15, replace_existing=True, id="send_mails")
    scheduler.add_job(add_all_unverified_to_pending_mails, 'cron', hour=3, timezone='Asia/Kolkata', replace_existing=True, id='update_db_for_reminder')
    scheduler.start()
