# API Design

Version

v1

Base URL

/api/v1

---

Authentication APIs

POST /register

Description

Register a new user.

Request

{
  "name": "Sharath",
  "email": "user@email.com",
  "password": "password123",
  "role":"Admin"
}

Response

201 Created

---

POST /login

Description

Authenticate user.

Request

{
  "email":"user@email.com",
  "password":"password123"
}

Response

{
   "access_token":"JWT_TOKEN"
}

---

Document APIs

POST /documents/upload

Description

Upload a document.

Headers

Authorization: Bearer Token

Content-Type

multipart/form-data

Response

{
   "document_id":"DOC1001",
   "status":"UPLOADED"
}

---

GET /documents

Description

List uploaded documents.

---

GET /documents/{id}

Description

Get document details.

---

DELETE /documents/{id}

Description

Delete document.

---

Worker APIs

GET /processing/status/{document_id}

Description

Return processing status.

Example

{
   "status":"PROCESSING"
}

---

Notification APIs

GET /notifications

Return user notifications.

---

Health APIs

GET /health

Returns

{
    "status":"UP"
}

---

Response Codes

200 OK

201 Created

400 Bad Request

401 Unauthorized

403 Forbidden

404 Not Found

500 Internal Server Error

---

Authentication

JWT Token

Authorization

Bearer <token>

---

Error Response

{
   "success": false,
   "message": "Document not found"
}
