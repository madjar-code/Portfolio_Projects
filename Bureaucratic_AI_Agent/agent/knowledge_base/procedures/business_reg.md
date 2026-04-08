# Procedure: Individual Entrepreneur Registration (Moldova)

## Description
Validates a pre-registration application for an individual entrepreneur (ÎI) in Moldova.
No document upload is required at this stage — only the submitted form data is validated.
Document verification (identity scan) occurs in a separate follow-up procedure.

## Required Documents
None. This procedure validates form data only.

## Agent Plan

1. Confirm that all required fields are present in the form data: first_name, last_name,
   idno, business_name, business_activity, address, email, phone.
   If any required field is missing or empty, reject immediately and list the missing fields.

2. Validate the IDNO (Moldovan personal identification number): must be exactly 13 digits,
   numeric only. Reject if the format is incorrect.

3. Validate the email address format. Reject if it is not a valid email.

4. Validate the phone number: must contain only digits, spaces, dashes, or a leading +,
   and be between 7 and 15 digits long. Reject if invalid.

5. Check that business_name is non-empty and does not consist only of special characters
   or numbers. A business name must contain at least one word.

6. Check that business_activity describes a legitimate type of commercial activity
   (not blank, not a single character, not obviously nonsensical).

7. Submit the validation report with all findings.

## Validation Rules
- All 8 fields are required: first_name, last_name, idno, business_name,
  business_activity, address, email, phone.
- IDNO: exactly 13 numeric digits.
- Email: standard email format (contains @, valid domain).
- Phone: 7–15 digits, may include +, spaces, or dashes.
- business_name: at least one meaningful word.
- business_activity: non-empty, descriptive text.

## Decision Criteria
ACCEPT if all validation rules pass.
REJECT if any field is missing, malformed, or fails validation.

## Output Expectations
validated_fields: list of fields that passed validation.
issues_found: one entry per failed check with field name and reason.
