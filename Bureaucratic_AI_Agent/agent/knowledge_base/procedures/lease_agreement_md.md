# Procedure: Residential Lease Agreement Review (Moldova)

## Description
Reviews a residential lease agreement (contract de locațiune) submitted as a DOCX
document. No form data is provided — all information must be extracted from the document
itself. The agent verifies that the agreement contains all legally required sections and
that each section is sufficiently complete.

## Required Documents
- Lease agreement in DOCX format
- Accepted formats: DOCX only
- Minimum 2 pages of substantive content (not counting blank or title-only pages)

## STEP 0 — Pre-flight gate (evaluate BEFORE calling any tool)

**This step requires NO tools.** All information is already in your context.

Check each condition in order. If any fails, submit your report immediately and stop
without reading the document.

| Condition | Fail if |
|-----------|---------|
| Document present | No document was submitted |
| Format | Not DOCX |

If all pre-flight checks pass, proceed to the Agent Plan below.

## Agent Plan

1. Read page 1 of the document. Confirm it is a residential lease agreement
   (contract de locațiune / rental agreement). If it is clearly a different type of
   document, reject immediately.

2. Read all remaining pages (pages 2, 3, 4, and so on) until you have seen the full
   document content.

3. Go through each of the 8 required sections below one by one. For every section,
   explicitly state: **FOUND and complete**, **FOUND but incomplete**, or **MISSING**.
   Do not skip any section — all 8 must be assessed regardless of what you find.

   | # | Section | What "complete" means |
   |---|---|---|
   | 1 | **Parties** | Landlord and tenant each identified by full name and ID/passport number |
   | 2 | **Property** | Full address: street, number, city; and total surface area (m²) |
   | 3 | **Lease duration** | Explicit start date AND (end date or notice period for indefinite term) |
   | 4 | **Rent** | Monthly amount stated with currency |
   | 5 | **Security deposit** | Amount stated (zero is acceptable, but the clause must be present) |
   | 6 | **Utilities** | Responsibility assigned to landlord or tenant for each major utility |
   | 7 | **Termination** | Conditions under which either party may terminate the agreement |
   | 8 | **Signatures** | Signature lines for both landlord and tenant are present |

4. Compile all findings and submit the final report.
   Report every section marked MISSING or incomplete. Do not stop at the first issue —
   collect all problems before submitting.

## Validation Rules
- Document must be a residential lease agreement.
- All 8 sections listed above must be present and complete.
- If a section is present but lacks essential details (e.g., rent section exists but amount
  is blank), treat it as incomplete and report it.

## Decision Criteria
ACCEPT if all 8 required sections are present and complete.
REJECT if any section is missing or incomplete.

## Output Expectations
Extract: landlord_name, tenant_name, property_address, lease_start, lease_end,
monthly_rent, security_deposit, utilities_responsible_party.
