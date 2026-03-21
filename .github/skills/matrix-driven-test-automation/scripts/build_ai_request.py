from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build AI prompt for MSTest code generation.")
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--app-code", default="src/PurchaseLibrary/Class1.cs")
    parser.add_argument("--output-md", default="artifacts/ai_test_request.md")
    parser.add_argument("--output-json", default="artifacts/ai_test_bundle.json")
    args = parser.parse_args()

    matrix_path = Path(args.matrix)
    app_path = Path(args.app_code)
    prompt_path = Path(args.output_md)
    bundle_path = Path(args.output_json)

    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    app_code = app_path.read_text(encoding="utf-8")

    prompt = f"""# Task
Generate MSTest code for PurchaseService from the matrix.

## Output format
- Output ONLY one C# code block.
- Target file: src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs

## Constraints
- Namespace: PurchaseLibrary.Tests
- Use [TestClass] and [DataTestMethod]
- Use [DataRow] for each matrix row
- Method name: Evaluate_MatrixCases_FromAi
- Call: PurchaseService.Evaluate(new PurchaseRequest(userType, payment, product))
- Assert: Assert.AreEqual(expected, actual, $"{{id}}: expected={{expected}}, actual={{actual}}")

## Matrix JSON
```json
{json.dumps(matrix, ensure_ascii=False, indent=2)}
```

## Source Code
```csharp
{app_code}
```
"""

    bundle = {
        "matrix_path": str(matrix_path),
        "app_code_path": str(app_path),
        "output_file": "src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs",
        "matrix": matrix,
    }

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.parent.mkdir(parents=True, exist_ok=True)

    prompt_path.write_text(prompt, encoding="utf-8")
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote AI prompt: {prompt_path}")
    print(f"Wrote AI bundle: {bundle_path}")


if __name__ == "__main__":
    main()
