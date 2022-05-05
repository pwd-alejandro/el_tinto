import json
import logging
from collections import namedtuple

from django.db import models

from el_tinto.utils.ses_sns import get_permanent_bounced_emails_from_bounce_obj, get_emails_from_complaint_obj

logger = logging.getLogger(__name__)

NOTIFICATION_STATUSES = namedtuple('NOTIFICATION_STATUSES', 'new processed failed')._make(range(3))

class SNSNotification(models.Model):
    """Stores incoming notifications from SNS for later processing of bounces and complaints"""
    STATE_CHOICES = (
        (NOTIFICATION_STATUSES.new, "New"),
        (NOTIFICATION_STATUSES.processed, "Processed"),
        (NOTIFICATION_STATUSES.failed, "Failed"),

    )
    headers = models.JSONField(default=dict, )
    data = models.JSONField(default=dict, )
    added_dt = models.DateTimeField(auto_now_add=True, db_index=True)
    state = models.SmallIntegerField(default=NOTIFICATION_STATUSES.new, choices=STATE_CHOICES, db_index=True)
    last_processed_dt = models.DateTimeField(null=True, blank=True, db_index=True)
    processing_error = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        """Settings"""
        verbose_name = "SNS Notification"
        verbose_name_plural = "SNS Notifications"

    def __str__(self):
        return str(self.pk)

    def process(self):
        """Attempt to see if this notification is any of use (Bounce or complaint).
        If so - try to find emails and send to GSL in platform via celery task"""
        try:
            if self.data.get('Type') == "Notification":
                message = json.loads(self.data['Message'])
                event_type = message.get('eventType')
                if event_type == 'Open':
                    bounce_obj = message.get('bounce', {})
                    bounced_recipients = get_permanent_bounced_emails_from_bounce_obj(bounce_obj)
                    for email in bounced_recipients:
                        print(email)
                else:
                    raise ValueError("Wrong type of notification")
            else:
                raise ValueError("Not a Notification")
        except Exception as e:
            logger.debug(f"Processing SNS Notification failed with {e}")
            self.state = NOTIFICATION_STATUSES.failed
            self.processing_error = str(e)
        self.save(update_fields=['state'])
