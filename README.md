# Internal Document Workflow API

A production-like backend API for managing agreement-related missing documents, file uploads and asynchronous document processing workflows.

The project is inspired by internal business systems where agreements may have missing required documents, users upload attachments, and the backend processes them asynchronously through a status-based workflow.

## Overview

This project demonstrates a backend workflow for handling missing documents related to client agreements.

The API allows users to:

- create clients;
- create agreements;
- register missing documents for agreements;
- upload document attachments;
- process uploaded documents asynchronously;
- track document status changes;
- test the main API workflows.

The main workflow is:

```text
pending → uploaded → processing → processed
```

## Tech Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Celery
- RabbitMQ
- Docker Compose
- Pytest
- pytest-django
- DRF test client

## Architecture

```mermaid
flowchart LR
    Client[API Client] --> API[Django REST Framework API]
    API --> DB[(PostgreSQL)]
    API --> Media[Local media storage]
    API --> Broker[RabbitMQ]
    Broker --> Worker[Celery Worker]
    Worker --> DB
```

## Document Processing Workflow

```mermaid
flowchart TD
    A[Missing document created] --> B[Status: pending]
    B --> C[Attachment uploaded via API]
    C --> D[Status: uploaded]
    D --> E[Celery task started]
    E --> F[Status: processing]
    F --> G[Status: processed]
```

## Features

- Relational data model for clients, agreements, missing documents and attachments.
- REST API built with Django REST Framework ViewSets and serializers.
- Multipart file upload endpoint for missing document attachments.
- Service layer for business logic related to attachment upload.
- Database transactions for consistent attachment creation and status updates.
- `transaction.on_commit` usage to start background processing only after successful database commit.
- Asynchronous document processing with Celery and RabbitMQ.
- Status-based workflow for uploaded documents.
- Local infrastructure with Docker Compose.
- API tests with Pytest, pytest-django and DRF test client.

## Domain Model

The project uses four main entities:

### Client

Represents a client/customer.

Main fields:

- `name`
- `email`
- `phone`
- `external_id`

### Agreement

Represents an agreement connected to a client.

Main fields:

- `client`
- `agreement_number`

### MissingDocument

Represents a required document that is missing for a specific agreement.

Main fields:

- `agreement`
- `document_type`
- `status`

Available statuses:

```text
pending
uploaded
processing
processed
rejected
```

### DocumentAttachment

Represents an uploaded file attached to a missing document.

Main fields:

- `missing_document`
- `file`
- `uploaded_at`

## API Endpoints

Base URL:

```text
http://127.0.0.1:8000/api/
```

### Clients

```http
GET /api/clients/
POST /api/clients/
GET /api/clients/{id}/
PUT /api/clients/{id}/
PATCH /api/clients/{id}/
DELETE /api/clients/{id}/
```

Example request:

```json
{
  "name": "Jan Kowalski",
  "email": "jan.kowalski@example.com",
  "phone": "+48123123123",
  "external_id": "SB-1001"
}
```

### Agreements

```http
GET /api/agreements/
POST /api/agreements/
GET /api/agreements/{id}/
PUT /api/agreements/{id}/
PATCH /api/agreements/{id}/
DELETE /api/agreements/{id}/
```

Example request:

```json
{
  "client": 1,
  "agreement_number": "AGR-2026-001"
}
```

### Missing Documents

```http
GET /api/missing-documents/
POST /api/missing-documents/
GET /api/missing-documents/{id}/
PUT /api/missing-documents/{id}/
PATCH /api/missing-documents/{id}/
DELETE /api/missing-documents/{id}/
```

Example request:

```json
{
  "agreement": 1,
  "document_type": "Signed agreement scan"
}
```

### Upload Attachment

```http
POST /api/missing-documents/{id}/upload-attachment/
```

Multipart form field:

```text
file
```

After upload, the missing document status changes from:

```text
pending → uploaded
```

Then a Celery task starts and moves the document through:

```text
uploaded → processing → processed
```

### Attachments

```http
GET /api/attachments/
POST /api/attachments/
GET /api/attachments/{id}/
PUT /api/attachments/{id}/
PATCH /api/attachments/{id}/
DELETE /api/attachments/{id}/
```

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd internal-document-workflow-api
```

### 2. Create and activate virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env`

Create a `.env` file in the project root:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True

POSTGRES_DB=documents_db
POSTGRES_USER=documents_user
POSTGRES_PASSWORD=documents_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://
```

### 5. Start infrastructure

```bash
docker compose up -d
```

This starts:

- PostgreSQL on port `5432`;
- RabbitMQ on port `5672`;
- RabbitMQ Management UI on port `15672`.

RabbitMQ Management UI:

```text
http://localhost:15672
```

Default credentials:

```text
guest / guest
```

### 6. Run migrations

```bash
cd app
python manage.py migrate
```

### 7. Create superuser

```bash
python manage.py createsuperuser
```

### 8. Start Django development server

```bash
python manage.py runserver
```

Django API will be available at:

```text
http://127.0.0.1:8000/api/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

### 9. Start Celery worker

Open a separate terminal:

```bash
cd app
source ../.venv/bin/activate
celery -A config worker -l info
```

The worker should discover the task:

```text
agreements.tasks.process_missing_document
```

## Running Tests

Make sure PostgreSQL is running:

```bash
docker compose up -d
```

Then run tests from the `app` directory:

```bash
cd app
pytest
```

Expected result:

```text
4 passed
```

The tests cover:

- client creation;
- agreement creation;
- missing document creation;
- attachment upload workflow with status processing.

## Project Structure

```text
internal-document-workflow-api/
├── app/
│   ├── agreements/
│   │   ├── migrations/
│   │   ├── tests/
│   │   │   └── test_api.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── tasks.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── config/
│   │   ├── celery.py
│   │   ├── settings.py
│   │   └── urls.py
│   └── manage.py
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## What This Project Demonstrates

This project demonstrates practical backend engineering concepts:

- designing relational data models with Django ORM;
- building REST APIs with Django REST Framework;
- handling multipart file uploads;
- separating business logic into a service layer;
- using `transaction.atomic` for consistent database operations;
- using `transaction.on_commit` for safe background task execution;
- implementing asynchronous processing with Celery and RabbitMQ;
- building status-based business workflows;
- testing API workflows with Pytest and DRF test client;
- running local infrastructure with Docker Compose.

## Future Improvements

Potential improvements:

- JWT authentication;
- permissions and role-based access control;
- OpenAPI/Swagger documentation;
- more detailed file validation;
- virus scan or OCR-like file processing simulation;
- S3-compatible object storage integration;
- GitHub Actions CI pipeline;
- pagination, filtering and search;
- audit log for document status changes.
