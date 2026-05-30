from __future__ import annotations

import argparse
import json
from pathlib import Path

from project_context import infer_project_context


def infer_app_code_path() -> Path:
    candidates = sorted(
        p for p in Path("src").rglob("*.cs") if ".Tests/" not in p.as_posix() and "/Generated/" not in p.as_posix()
    )
    if not candidates:
        raise ValueError("No application source file found under src/.")
    return candidates[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build AI prompt for test code generation inferred from the current project."
    )
    parser.add_argument("--matrix", required=True)
    parser.add_argument("--app-code", default="")
    parser.add_argument("--output-md", default="artifacts/ai_test_request.md")
    parser.add_argument("--output-json", default="artifacts/ai_test_bundle.json")
    args = parser.parse_args()

    matrix_path = Path(args.matrix)
    context = infer_project_context()
    app_path = Path(args.app_code) if args.app_code else infer_app_code_path()
    prompt_path = Path(args.output_md)
    bundle_path = Path(args.output_json)

    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    app_code = app_path.read_text(encoding="utf-8")

    if context.language != "csharp":
        raise ValueError(f"Unsupported language inferred: {context.language}")

    if context.test_framework == "mstest":
        style_rules = """- Use [TestClass] and [DataTestMethod]
- Use [DataRow] for each matrix row
- Use Assert.AreEqual(expected, actual, $"{{id}}: expected={{expected}}, actual={{actual}}, memo={{memo}}")
"""
    elif context.test_framework == "xunit":
        style_rules = """- Use [Theory] and [InlineData] for matrix rows
- Use Assert.Equal(expected, actual)
"""
    elif context.test_framework == "nunit":
        style_rules = """- Use [TestFixture] and [TestCase] for matrix rows
- Use Assert.That(actual, Is.EqualTo(expected))
"""
    else:
        style_rules = """- Detect and follow the existing test framework style in this repository.
"""

    prompt = f"""# Task
Generate test code from the matrix using the test framework inferred from this repository.

## Output format
- Output ONLY one code block matching the inferred language.
- Target file: {context.generated_test_file.as_posix()}

## Constraints
- Inferred language: {context.language}
- Inferred test framework: {context.test_framework}
- `memo` is a note column and must NOT affect pass/fail logic.
- Use matrix columns dynamically (excluding `expected` and `memo` from input payload if needed).
{style_rules}

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
        "language": context.language,
        "test_framework": context.test_framework,
        "output_file": str(context.generated_test_file),
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
