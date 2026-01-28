# Personal (Remote) Gallery

## 1. Overview

The project is a platform for uploading photos for further viewing. Functions (in general terms):

1. Upload photos with metadata
2. View uploaded photos
3. Authentication and authorization

The platform includes the following parts:

1. **Frontend** (React)
2. **Backend API** (Django)
3. **Admin Panel** (Django Admin)

---

## 2. Project Goals

This is not a business project ⇒ business goals are not applicable here

### Main Development Goals

- Develop business requirements: functional and non-functional
- Develop a complete list of necessary diagrams
- End-to-end project development
- Work with remote object storage
- Apply Redis for specific use cases
- Implement proper deployment

### User Goals

- Easily upload photos individually or in batches
- Find photos in the photo list
- Edit the gallery composition

---

## Project Scope

### 3.1 In Scope (Portfolio)

- Registration + authentication (Google OAuth + Email/Password)
- Create entries with one or more photos
- View entries with photos
- View a single entry with photos (Detail Page)
- View aggregated statistics on entries (via caching)

### 3.2 Out of Scope

- Search entries by metadata (semantics) — RAG
- Efficient filtering and search
- Adding geolocation to photos
- Ability to publish photos to public space

---

## 4. Stakeholders

| **Stakeholder** | **Role in Personal (Remote) Gallery** | **Interest / Expectations** |
| --- | --- | --- |
| Product Owner (you) | Initiator, goal setter, architect | Implement educational and technical project goals |
| End Users | Upload/view photos | Simplicity, stability, convenient UI |
| Technical Reviewers | Evaluate as educational/portfolio project | Readable architecture, good design |
| Infrastructure | Cloud hosting, S3, OAuth providers | Correct integration, compliance with limits |

---

## 5. Terms and Key Concepts

| **Term** | **Definition** |
| --- | --- |
| Entry | A record with metadata associated with one or more photos |
| Photo | A single specific photo |
| Index Page | A page with a list of Entries, from which you can view each entry with photos in detail (Detail Page) |

---

## 6. System Context

The system interacts with:

- Google OAuth — authentication
- Email Service — sending emails to users
- Static File Storage — storing static data
- Object Storage — storing user photos
- PostgreSQL — entry metadata, user data

---

## 7. Risks

| Risk | Description |
| --- | --- |
| Spam with photo entries | This will fill up all storage ⇒ need to explicitly set limits and implement compression |
| Photo duplication | Need to implement idempotency |
| Statistics on photo count loads slowly | Apply caching |