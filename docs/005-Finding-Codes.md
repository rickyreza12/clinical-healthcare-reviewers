# Finding Codes

Stable wire codes are the `FindingType` enum values in `backend/domain/enums.py`.

| Code | Meaning | SOP |
|---|---|---|
| `missing_required_document` | A core case record is absent. | SOP-01 |
| `missing_required_field` | A required claim field is blank or absent. | SOP-01 |
| `missing_required_signature` | Required physician signature is absent or invalid. | SOP-01 |
| `identity_mismatch` | Patient ID or DOB differs across documents. | SOP-02 |
| `invalid_hospitalization_chronology` | Discharge precedes admission. | SOP-04 |
| `procedure_date_outside_stay` | Procedure/study date is outside the stay. | SOP-04 |
| `diagnosis_conflict` | Claim diagnosis conflicts with final documented diagnosis. | SOP-03 |
| `uncertain_diagnosis` | Record is uncertain while claim asserts a diagnosis. | SOP-03, SOP-06 |
| `missing_procedure_support` | Required procedure report is absent. | SOP-05 |
| `incomplete_procedure_support` | Required support section is blank. | SOP-05 |
| `indeterminate_review` | Available evidence cannot resolve comparison. | SOP-06 |

Codes are unique enum values and are asserted in `tests/acceptance`.
