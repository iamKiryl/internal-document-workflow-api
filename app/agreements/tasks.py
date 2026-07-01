import time 

from celery import shared_task
from django.conf import settings
from django.db import transaction

from .models import MissingDocument

@shared_task()
def process_missing_document(missing_document_id: int) -> None:
    """
    Simulates the processing of a missing document.

    Args:
        missing_document_id (int): The ID of the missing document to process.
    """
    try:
        with transaction.atomic():
            missing_document = MissingDocument.objects.select_for_update().get(id=missing_document_id)
            if missing_document.status != MissingDocument.Status.UPLOADED:
                return  

            missing_document.status = MissingDocument.Status.PROCESSING
            missing_document.save(update_fields=['status'])

        if not getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False):
            time.sleep(3)

        with transaction.atomic():
            # Re-fetch the missing document to ensure it's still in PROCESSING state
            missing_document = MissingDocument.objects.select_for_update().get(id=missing_document_id)
            if missing_document.status == MissingDocument.Status.PROCESSING:
                # Update status to PROCESSED
                missing_document.status = MissingDocument.Status.PROCESSED
                missing_document.save(update_fields=['status'])

    except MissingDocument.DoesNotExist:
        pass  # Handle the case where the missing document does not exist
