# Procedure: Passport Application (Moldova) — Strict

## Description
Validates a Moldovan passport application using a fixed verification checklist.
The agent MUST follow the Agent Plan steps in the listed order.

## Required Documents
- Passport or national ID scan (JPG, PNG, or PDF)

## Agent Plan

1. Read the first page of the submitted document. Determine whether it is a valid
   identity document (passport or national ID). If it is clearly not an identity
   document, reject immediately with a clear explanation.

2. Extract the applicant's personal data from the document: first name, last name,
   date of birth, document number, and expiry date.

3. Obtain today's date and verify that the document has not expired.

4. Compare the extracted first name and last name against the applicant's form data.
   Note any mismatches.

5. Compile all findings and submit the final validation report.

## Validation Rules
- First name and last name must match form_data (case-insensitive).
- Document must not be expired at the time of submission.
- All required fields must be present and legible.

## Decision Criteria
ACCEPT if all checks pass.
REJECT if any check reveals a mismatch, missing field, expired document, or wrong document type.

## Output Expectations
Extract: first_name, last_name, date_of_birth, document_number, expiry_date.