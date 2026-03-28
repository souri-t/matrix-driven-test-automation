from __future__ import annotations

import argparse
import re
from pathlib import Path

from project_context import infer_project_context


def extract_csharp_code(text: str) -> str:
    patterns = [
        r"```csharp\s*(.*?)\s*```",
        r"```cs\s*(.*?)\s*```",
        r"```C#\s*(.*?)\s*```",
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.DOTALL)
        if m:
            return m.group(1).rstrip() + "\n"
    raise ValueError("No C# code block found")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract generated test code from AI response using inferred project context."
    )
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    context = infer_project_context()
    if context.language != "csharp":
        raise ValueError(f"Unsupported language inferred: {context.language}")

    text = Path(args.input).read_text(encoding="utf-8")
    code = extract_csharp_code(text)

    if context.test_framework == "mstest":
        required_tokens = ["[TestClass]", "Data", "Assert."]
    elif context.test_framework == "xunit":
        required_tokens = ["[Theory]", "InlineData", "Assert."]
    elif context.test_framework == "nunit":
        required_tokens = ["[Test", "TestCase", "Assert."]
    else:
        required_tokens = ["Assert."]

    missing = [t for t in required_tokens if t not in code]
    if missing:
        raise ValueError(f"Generated code seems invalid. Missing tokens: {missing}")

    output = Path(args.output) if args.output else context.generated_test_file
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(code, encoding="utf-8")

    print(f"Generated test file: {output}")


if __name__ == "__main__":
    main()
