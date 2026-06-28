from django.db import transaction

from .models import DocumentAttachment, MissingDocument

@transaction.atomic
def upload_attachment_for_missing_document(
    *,
    missing_document: MissingDocument, 
    file) -> DocumentAttachment:
    """
    Uploads a document attachment for a given missing document.

    Args:
        missing_document (MissingDocument): The missing document instance.
        file: The file to be uploaded.

    Returns:
        DocumentAttachment: The created document attachment instance.
    """
    attachment = DocumentAttachment.objects.create(
        missing_document=missing_document,
        file=file
    )

    if missing_document.status == MissingDocument.Status.PENDING:
        missing_document.status = MissingDocument.Status.UPLOADED
        missing_document.save(update_fields=['status'])

    return attachment