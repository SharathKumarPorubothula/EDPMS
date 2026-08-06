# Database Design

Database

PostgreSQL

---

Database Name

edpms_users

---

Table: users

Purpose

Store application users.

Columns

id
name
email
password_hash
role
is_active
created_at
updated_at

Primary Key

id

Unique

email

---


---

Database Name

edpms_documents

---
Table: documents

Purpose

Store uploaded documents.

Columns

id
document_id
user_id
filename
file_path
file_size
file_type
status
created_at
updated_at

Foreign Key

user_id → users.id

---

---

Database Name

edpms_extracted_data

---

Table: extracted_data

Purpose

Store extracted fields.

Columns

id
document_id
field_name
field_value
confidence
created_at

Foreign Key

document_id → documents.id

---

---

Database Name

edpms_notifications

---

Table: notifications

Purpose

Track notification history.

Columns

id
user_id
document_id
notification_type
status
sent_at

---

---

Database Name

edpms_audit_logs

---

Table: audit_logs

Purpose

Track user activity.

Columns

id
user_id
action
module
ip_address
created_at

---

Indexes

users.email

documents.document_id

documents.status

documents.created_at

audit_logs.created_at

---

Relationships

User

1

↓

Many

Documents

↓

One

↓

Many

Extracted Data

↓

One

↓

Many

Notifications
