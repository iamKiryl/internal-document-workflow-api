from django.contrib import admin

# Register your models here.

from .models import Agreement, Client, DocumentAttachment, MissingDocument

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'phone', 'external_id', 'created_at')
    search_fields = ('name', 'email', 'phone', 'external_id')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('id', 'agreement_number', 'client', 'created_at')
    search_fields = ('agreement_number', 'client__name')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(MissingDocument)
class MissingDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'agreement', 'document_type', 'status', 'created_at')
    search_fields = ('agreement__agreement_number', 'document_type')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',)

@admin.register(DocumentAttachment)
class DocumentAttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'missing_document', 'file', 'uploaded_at')
    search_fields = ('missing_document__document_type',)
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)