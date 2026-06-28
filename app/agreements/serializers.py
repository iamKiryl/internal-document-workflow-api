from rest_framework import serializers

from .models import Agreement, Client, DocumentAttachment, MissingDocument


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            "id",
            "name",
            "email",
            "phone",
            "external_id",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class DocumentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAttachment
        fields = (
            "id",
            "missing_document",
            "file",
            "uploaded_at",
        )
        read_only_fields = ("id", "uploaded_at")


class MissingDocumentSerializer(serializers.ModelSerializer):
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = MissingDocument
        fields = (
            "id",
            "agreement",
            "document_type",
            "status",
            "attachments",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class AgreementSerializer(serializers.ModelSerializer):
    client_details = ClientSerializer(source="client", read_only=True)
    missing_documents = MissingDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Agreement
        fields = (
            "id",
            "client",
            "client_details",
            "agreement_number",
            "missing_documents",
            "created_at",
        )
        read_only_fields = ("id", "created_at")