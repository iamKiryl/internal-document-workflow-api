from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    external_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name   
    
class Agreement(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='agreements')
    
    agreement_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Agreement {self.agreement_number} for {self.client.name}"
    

class MissingDocument(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UPLOADED = "uploaded", "Uploaded"
        PROCESSING = "processing", "Processing"
        PROCESSED = "processed", "Processed"
        REJECTED = "rejected", "Rejected"
    
    agreement = models.ForeignKey(Agreement, on_delete=models.CASCADE, related_name='missing_documents')
    document_type = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.document_type} {self.status} for Agreement {self.agreement.agreement_number}"
    

class DocumentAttachment(models.Model):
    missing_document = models.ForeignKey(MissingDocument, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Attachment for missing document {self.missing_document_id})"