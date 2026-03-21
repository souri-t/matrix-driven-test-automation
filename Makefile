.PHONY: matrix validate gherkin ai-request ai-materialize test demo json-to-excel

matrix:
	python3 .github/skills/matrix-driven-test-automation/scripts/create_sample_excel.py --output testcases/purchase_matrix.xlsx
	python3 .github/skills/matrix-driven-test-automation/scripts/excel_to_json.py --input testcases/purchase_matrix.xlsx --output testcases/purchase_matrix.json

validate:
	python3 .github/skills/matrix-driven-test-automation/scripts/validate_matrix_json.py --input testcases/purchase_matrix.json

gherkin:
	python3 .github/skills/matrix-driven-test-automation/scripts/generate_gherkin.py --input testcases/purchase_matrix.json --output features/purchase.feature

ai-request:
	python3 .github/skills/matrix-driven-test-automation/scripts/build_ai_request.py --matrix testcases/purchase_matrix.json --app-code src/PurchaseLibrary/Class1.cs --output-md artifacts/ai_test_request.md --output-json artifacts/ai_test_bundle.json

ai-materialize:
	python3 .github/skills/matrix-driven-test-automation/scripts/materialize_ai_tests.py --input artifacts/sample_ai_response.md --output src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs

json-to-excel:
	python3 .github/skills/matrix-driven-test-automation/scripts/json_to_excel.py --input testcases/purchase_matrix.json --output testcases/purchase_matrix_from_json.xlsx

test:
	dotnet test MatrixDrivenSample.sln

demo: matrix validate gherkin ai-request ai-materialize test
