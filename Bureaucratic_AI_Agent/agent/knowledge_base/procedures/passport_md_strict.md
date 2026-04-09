# Procedure: Passport Application (Moldova) — Strict

## Description
Validates a Moldovan passport application using a fixed verification checklist.
The agent MUST follow the Agent Plan steps in the listed order.

## Required Documents
- Passport or national ID scan
- Accepted formats: JPG, PNG only (PDF is not accepted)
- File size: minimum 10 KB, maximum 10 MB
- Image must be sufficiently clear and legible (not a screenshot, not a photocopy of a photocopy)

## Agent Plan

1. Verify document metadata before reading the file. Check that:
   - The format is JPG or PNG (reject immediately if PDF or other).
   - The file size is between 10 KB and 10 MB (reject if outside range).
   If any metadata check fails, reject immediately without reading the file.

2. Read the first page of the submitted document. Determine whether it is a valid
   identity document (passport or national ID). If it is clearly not an identity
   document, reject immediately with a clear explanation.

3. Extract the applicant's personal data from the document: first name, last name,
   date of birth, document number, and expiry date.

4. Obtain today's date and verify that the document has not expired.

5. Compare the extracted first name and last name against the applicant's form data.
   Note any mismatches.

6. Compile all findings and submit the final validation report.
   Important: complete all steps above before calling submit_report, even if a reject reason was found earlier. The goal is to collect every issue in a single report.

## Validation Rules
- Document format must be JPG or PNG. PDF and other formats are rejected.
- File size must be between 10 KB and 10 MB.
- First name and last name must match form_data (case-insensitive).
- Document must not be expired at the time of submission.
- All required fields must be present and legible.

## Decision Criteria
ACCEPT if all checks pass.
REJECT if any check reveals a mismatch, missing field, expired document, or wrong document type.

## Output Expectations
Extract: first_name, last_name, date_of_birth, document_number, expiry_date.