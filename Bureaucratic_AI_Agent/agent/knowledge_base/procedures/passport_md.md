# Procedure: Passport Application (Moldova)

## Description
Validates an application for a Moldovan passport. Checks personal data
consistency between the submitted form and the identity document scan.

## Required Documents
- Passport scan or national ID (PDF, JPG, or PNG)

## Validation Rules
- First name, last name, and date of birth in form_data must match the document scan.
- Document must not be expired at the time of submission.
- Document must belong to the applicant (photo check deferred to human review).

## Decision Criteria
ACCEPT if all validation rules pass and the document is legible.
REJECT if any field mismatches, the document is expired, or the scan is unreadable.

## Output Expectations
Extract: first_name, last_name, date_of_birth, document_number, expiry_date.