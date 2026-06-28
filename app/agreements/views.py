from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

# Create your views here.
from .models import Agreement, Client, DocumentAttachment, MissingDocument
from .serializers import AgreementSerializer, AttachmentUploadSerializer, ClientSerializer, DocumentAttachmentSerializer, MissingDocumentSerializer
from .services import upload_attachment_for_missing_document

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

    @action(
        detail=True,
        methods=["post"],
        url_path="upload-attachment",
        serializer_class=AttachmentUploadSerializer,
        parser_classes=[MultiPartParser, FormParser],    )

    def upload_attachment(self, request, pk=None):
        missing_document = self.get_object()

        serializer = AttachmentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attachment = upload_attachment_for_missing_document(
            missing_document=missing_document,
            file=serializer.validated_data["file"],
        )

        response_serializer = DocumentAttachmentSerializer(attachment)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

class DocumentAttachmentViewSet(viewsets.ModelViewSet):
    queryset = (DocumentAttachment.objects
                .select_related('missing_document', 'missing_document__agreement')
                .order_by('-uploaded_at'))
    serializer_class = DocumentAttachmentSerializer