---
name: matrix-driven-test-automation
description: Generate and maintain matrix-driven test assets for this repository. Use this when asked to convert Excel test matrix to JSON, validate matrix JSON, generate Gherkin, prepare AI prompt for MSTest generation, or materialize AI output into MSTest files.
---

This skill provides scripts for the matrix-driven testing workflow used in this repository.

## Scope

- Excel (`.xlsx`) matrix creation and review support
- Excel -> JSON conversion (intermediate source of truth)
- JSON validation
- JSON -> Gherkin generation
- AI request generation for MSTest code
- AI response materialization into `.cs` MSTest files

## Script locations

All scripts are under:

- `.github/skills/matrix-driven-test-automation/scripts/`

## Commands

Run from repository root.

```bash
python3 .github/skills/matrix-driven-test-automation/scripts/create_sample_excel.py --output testcases/purchase_matrix.xlsx
python3 .github/skills/matrix-driven-test-automation/scripts/excel_to_json.py --input testcases/purchase_matrix.xlsx --output testcases/purchase_matrix.json
python3 .github/skills/matrix-driven-test-automation/scripts/validate_matrix_json.py --input testcases/purchase_matrix.json
python3 .github/skills/matrix-driven-test-automation/scripts/generate_gherkin.py --input testcases/purchase_matrix.json --output features/purchase.feature
python3 .github/skills/matrix-driven-test-automation/scripts/build_ai_request.py --matrix testcases/purchase_matrix.json --app-code src/PurchaseLibrary/Class1.cs --output-md artifacts/ai_test_request.md --output-json artifacts/ai_test_bundle.json
python3 .github/skills/matrix-driven-test-automation/scripts/materialize_ai_tests.py --input artifacts/sample_ai_response.md --output src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs
```

## Notes

- The matrix schema is shared in `matrix_schema.py`.
- Use `id` as the stable test case key for traceability.
- Keep generated test files under `src/PurchaseLibrary.Tests/Generated/`.
