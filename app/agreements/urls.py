from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import ClientViewSet, AgreementViewSet, MissingDocumentViewSet, DocumentAttachmentViewSet

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("agreements", AgreementViewSet, basename="agreement")
router.register("missing-documents", MissingDocumentViewSet, basename="missing-document")
router.register("attachments", DocumentAttachmentViewSet, basename="attachment")

urlpatterns = [
    path("", include(router.urls)),
]