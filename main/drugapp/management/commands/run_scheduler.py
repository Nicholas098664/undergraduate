import logging
import time
from datetime import timedelta
from django.core.management.base import BaseCommand
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import now
from django.db.models import Q
from drugapp.models import Medication  # Replace 'drugapp' with your app name
import zoneinfo

logger = logging.getLogger(__name__)

def send_sms(to_number, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_number,
        )
        logger.info(f"Sent SMS to {to_number}")
    except Exception as e:
        logger.error(f"Failed to send SMS to {to_number}: {e}")

def job_send_medication_reminders():
    local_tz = zoneinfo.ZoneInfo('Africa/Lagos')
    current_datetime_utc = now()  # timezone-aware UTC datetime
    current_datetime_local = current_datetime_utc.astimezone(local_tz)
    current_time_local = current_datetime_local.time()

    # Define a 2-minute window in local time to catch reminders in case of slight delay
    window_start = (current_datetime_local - timedelta(minutes=2)).time()
    window_end = current_time_local

    print(f"Current local datetime: {current_datetime_local}")
    print(f"Window start: {window_start}")
    print(f"Window end: {window_end}")

    meds = Medication.objects.filter(
        dose_time__gte=window_start,
        dose_time__lte=window_end,
        start_date__lte=current_datetime_local.date(),
    ).filter(
        Q(end_date__gte=current_datetime_local.date()) | Q(end_date__isnull=True)
    )

    print("Job running... checking medications")
    print(f"Medications found: {meds.count()}")

    for med in meds:
        user_phone = getattr(med.user.profile, 'phone_number', None)
        if user_phone:
            message = f"Hi {med.user.username}, it's time to take your medication: {med.drug_name} ({med.dosage})"
            send_sms(user_phone, message)
            logger.info(f"Reminder sent for {med.drug_name} to {med.user.username}")

class Command(BaseCommand):
    help = "Run APScheduler to send medication reminders"

    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()
        scheduler.add_job(job_send_medication_reminders, 'interval', minutes=1)
        scheduler.start()

        print("Scheduler started!")
        logger.info("Scheduler started.")

        try:
            while True:
                time.sleep(2)
        except KeyboardInterrupt:
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
