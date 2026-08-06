# Enterprise Document Processing System (EDPMS)

## Version

1.0

## Author

Sharath Kumar

---

# Overview

The Enterprise Document Processing System (EDPMS) is a microservices-based application that automates document upload, processing, extraction, storage, and notification.

The application is built using Flask microservices running inside Docker containers.

---

# Goals

- Secure authentication
- Upload PDF/Image documents
- Process documents asynchronously
- Store document metadata
- Notify users after completion
- Containerized deployment
- Easy horizontal scaling

---

# Technology Stack

Backend
- Python 3.10.6
- Flask

Database
- PostgreSQL

Messaging
- Kafka

Caching
- Redis (Future)

Containerization
- Docker
- Docker Compose

Reverse Proxy
- Custom apache_base

Monitoring
- Prometheus
- Grafana

CI/CD
- GitHub Actions

---

# High Level Architecture

                    User
                      |
                      |
                 apache_base Gateway
                      |
                      |
                service_bridge
                      |
        -------------------------------
        |              |              |
        |              |              |
 Auth Service    Document Service   Notification
        |              |
        |              |
        ------- PostgreSQL ----------
                      |
                   Kafka
                      |
                Worker Service

---

# Containers

Container 1

Name:
apachebase

Responsibilities
- SSL Termination
- Route Requests

---

Container 2

Name:
auth-service

Responsibilities

- User Registration
- Login
- JWT Authentication
- Role Management

---

Container 3

Name:
document-service

Responsibilities

- Upload Documents
- Validate Files
- Store Metadata
- Publish Kafka Events

---

Container 4

Name:
worker-service

Responsibilities

- Consume Kafka Messages
- Process Documents
- Extract Data
- Update Status

---

Container 5

Name:
notification-service

Responsibilities

- Email Notification
- Status Notification

---

Container 6

Name:
postgres

Responsibilities

- Store Users
- Store Documents
- Store Audit Logs

---

Container 7

Name:
kafka

Responsibilities

- Asynchronous Communication

---

Data Flow

User

↓

apache_base

↓

Authentication

↓

Document Upload

↓

Store Metadata

↓

Kafka Producer

↓

Worker

↓

Update Database

↓

Notification

↓

User

---

Deployment

Docker Compose

Docker Network

Persistent Volumes

Environment Variables

---

Security

JWT Authentication

Password Hashing

HTTPS

Role Based Access

Input Validation
