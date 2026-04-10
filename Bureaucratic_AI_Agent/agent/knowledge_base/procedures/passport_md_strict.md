# Procedure: Passport Application (Moldova) — Strict

## Description
Validates a Moldovan passport application using a fixed verification checklist.
The agent MUST follow the Agent Plan steps in the listed order.

## Required Documents
- Passport or national ID scan
- Accepted formats: JPG, PNG only (PDF is not accepted)
- File size: minimum 10 KB, maximum 10 MB
- Image must be sufficiently clear and legible (not a screenshot, not a photocopy of a photocopy)

## STEP 0 — Pre-flight gate (evaluate BEFORE calling any tool)

**This step requires NO tools.** All information is already in your context.

Check each condition in order. If any fails, submit your report immediately and stop
without reading the document.

| Condition | Fail if |
|-----------|---------|
| Document present | No document was submitted |
| Format | Not JPG or PNG |
| File size | Less than 10 KB (10,240 bytes) or more than 10 MB |

If all pre-flight checks pass, proceed to the Agent Plan below.

## Agent Plan

1. Read the first page of the submitted document. Determine whether it is a valid
   identity document (passport or national ID). If it is clearly not an identity
   document, reject immediately with a clear explanation.

2. Obtain today's date and verify that the document has not expired.

3. Extract the applicant's personal data from the document: first name, last name,
   date of birth, document number, and expiry date. Compare first name and last name
   against the applicant's form data and note any mismatches.

4. Compile all findings and submit the final validation report.
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