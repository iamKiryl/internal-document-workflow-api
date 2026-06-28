from django.shortcuts import render
from rest_framework import viewsets

# Create your views here.
from .models import Agreement, Client, DocumentAttachment, MissingDocument
from .serializers import AgreementSerializer, ClientSerializer, DocumentAttachmentSerializer, MissingDocumentSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all().order_by('-created_at')
    serializer_class = ClientSerializer

class AgreementViewSet(viewsets.ModelViewSet):
    queryset = (Agreement.objects
                .select_related('client')
                .prefetch_related('missing_documents__attachments')
                .order_by('-created_at'))
    serializer_class = AgreementSerializer

class MissingDocumentViewSet(viewsets.ModelViewSet):
    queryset = (MissingDocument.objects
                .select_related('agreement', 'agreement__client')
                .prefetch_related('attachments')
                .order_by('-created_at'))
    serializer_class = MissingDocumentSerializer

class DocumentAttachmentViewSet(viewsets.ModelViewSet):
    queryset = (DocumentAttachment.objects
                .select_related('missing_document', 'missing_document__agreement')
                .order_by('-uploaded_at'))
    serializer_class = DocumentAttachmentSerializer