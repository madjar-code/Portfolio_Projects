This document details the functional and non-functional requirements for the remote gallery project (Personal (Remote) Gallery).

## 1. Goals and Scope

| **Type** | **Description** |
| --- | --- |
| Main Goal | Create a web platform for uploading and viewing a personal photo gallery (RU/EN) with a focus on educational goals in system design. |
| Included (In Scope) | Authentication via Google OAuth and Email/Password, creating entries (Entry) with one or more photos, viewing list of entries and entry details, basic statistics (via cache), administration via Django Admin. |
| Excluded (Out of Scope) | Search by metadata/semantics, advanced filtering, geolocation, publishing photos to public space, commenting, likes, social media sharing. |

## 2. User and Authentication Requirements

### 2.1 Functional Authentication Requirements (FR-AUTH)

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-AUTH-100 | The system must allow users to log in via Google OAuth. | Base User | First login via OAuth creates an account. |
| FR-AUTH-101 | The system must allow users to register with email and password. | Base User | With account confirmation via email. |
| FR-AUTH-102 | The system must allow users to log in with email and password. | Base User | After account confirmation. |
| FR-AUTH-103 | The system must allow users to log out. | Base User | Invalidate session/token. |
| FR-AUTH-104 | The system must restrict access to personal entries to the owner only. | Base User | Access to own Entry/photos — only after login. |
| FR-AUTH-105 | The system must support password recovery via email. | Base User | Send password reset link. |
| FR-AUTH-106 | Administrator must be able to log into the admin panel with login/password. | Admin | Standard Django Admin, admin created via command line. |

### 2.2 Functional User Management Requirements (FR-USER)

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-USER-200 | User must be able to delete their account and related data (soft delete). | Base User | Both user and their photos are deleted (soft) |

## 3. Functional Gallery Requirements

### 3.1 Working with Entries (FR-ENTRY)

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-ENTRY-100 | The system must allow users to create a new entry (Entry) with one or more photos. | Base User | File upload + metadata input (title, description, tags — optional). |
| FR-ENTRY-101 | The system must allow users to view a list of their entries (Index Page). | Base User | Pagination, basic sorting (by creation date). |
| FR-ENTRY-102 | The system must allow users to open a detailed entry page (Detail Page) with viewing all photos and metadata. | Base User | Navigation through photos within Entry. |
| FR-ENTRY-103 | The system must allow users to edit an entry (title, description, photo composition: add/remove). | Base User | Can limit editing to metadata only. |
| FR-ENTRY-104 | The system must allow users to delete an entry (Entry) entirely. | Base User | Delete metadata + photos from Object Storage (or mark as deleted). |

### 3.2 Working with Photos (FR-PHOTO)

| **ID** | **Requirement** | **Role** | **Notes** |
| --- | --- | --- | --- |
| FR-PHOTO-200 | The system must allow uploading multiple photos in one action (multi-upload). | Base User | Display progress, basic validation by format/size. |
| FR-PHOTO-201 | The system must limit the maximum size of one photo and the total number of photos per entry. | System | Limits are set in configuration. |

## 4. Non-Functional Requirements (NFR)

| **ID** | **Requirement** | **Category** | **Notes** |
| --- | --- | --- | --- |
| NFR-001 | The loading time of the main entry list page should not exceed 1 second under normal load. | Performance | Can cache aggregated statistics using Redis. |
| NFR-002 | The system must support at least X active users per day (educational target: tens/hundreds). | Scalability | For portfolio, a realistic estimate is sufficient. |
| NFR-003 | All private operations must be performed only via secure HTTPS protocol. | Security | Basic security level. |
| NFR-004 | Access to other users' entries without explicit permission must be impossible. | Security | Access rights verification at backend level. |
| NFR-005 | Minimum monitoring must be implemented (backend error logs, basic metrics). | Observability | Sentry/file/console logging will work. |