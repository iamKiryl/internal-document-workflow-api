from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient
import pytest

from agreements.models import MissingDocument, Agreement, Client

pytestmark = pytest.mark.django_db(transaction=True)

TEST_CLIENT_DATA = {
    "name": "Jan Kowalski",
    "email": "jan.kowalski@example.com",
    "phone": "+48123123123",
    "external_id": "SB-1001",
}

AGREEMENT_DATA = {
    "agreement_number": "AG-1001",
}

def test_create_client():
    api_client = APIClient()
    response = api_client.post(
        "/api/clients/",
        TEST_CLIENT_DATA,
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Client.objects.count() == 1
    client = Client.objects.first()
    assert client is not None
    assert client.name == TEST_CLIENT_DATA["name"]
    assert client.email == TEST_CLIENT_DATA["email"]
    assert client.phone == TEST_CLIENT_DATA["phone"]
    assert client.external_id == TEST_CLIENT_DATA["external_id"]

def test_create_agreement():
    client = Client.objects.create(
        name=TEST_CLIENT_DATA["name"],
        email=TEST_CLIENT_DATA["email"]    
        )
    api_client = APIClient()
    response = api_client.post(
        "/api/agreements/",
        {**AGREEMENT_DATA, "client": client.id},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert Agreement.objects.count() == 1
    agreement = Agreement.objects.first()
    assert agreement is not None
    assert agreement.agreement_number == AGREEMENT_DATA["agreement_number"]

def test_create_missing_document():
    client = Client.objects.create(
        name=TEST_CLIENT_DATA["name"],
        email=TEST_CLIENT_DATA["email"]    
        )
    agreement = Agreement.objects.create(
        client=client,
        agreement_number=AGREEMENT_DATA["agreement_number"]
    )
    api_client = APIClient()
    response = api_client.post(
        "/api/missing-documents/",
        {"agreement": agreement.id, "document_type": "ID Card"},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert MissingDocument.objects.count() == 1
    missing_document = MissingDocument.objects.first()
    assert missing_document is not None
    assert missing_document.agreement.id == agreement.id
    assert missing_document.document_type == "ID Card"
    assert missing_document.status == MissingDocument.Status.PENDING

def test_upload_attachment_updates_missing_document_status(settings):   
    settings.CELERY_TASK_ALWAYS_EAGER = True  # Run Celery tasks synchronously for testing

    client = Client.objects.create(
        name=TEST_CLIENT_DATA["name"],
        email=TEST_CLIENT_DATA["email"]    
        )
    agreement = Agreement.objects.create(
        client=client,
        agreement_number=AGREEMENT_DATA["agreement_number"]
    )
    missing_document = MissingDocument.objects.create(
        agreement=agreement,
        document_type="ID Card"
    )

    api_client = APIClient()
    file_content = b"Test file content"
    uploaded_file = SimpleUploadedFile("test_file.txt", file_content, content_type="text/plain")

    response = api_client.post(
        f"/api/missing-documents/{missing_document.id}/upload-attachment/",
        {"file": uploaded_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_201_CREATED
    missing_document.refresh_from_db()
    assert missing_document.status == MissingDocument.Status.PROCESSED  # Assuming the task processes the document and updates the status to PROCESSED
    assert missing_document.attachments.count() == 1
    