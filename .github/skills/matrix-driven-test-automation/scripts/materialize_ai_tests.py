from __future__ import annotations

import argparse
import re
from pathlib import Path


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
    parser = argparse.ArgumentParser(description="Extract C# test code from AI response.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="src/PurchaseLibrary.Tests/Generated/PurchaseServiceMatrixAiTests.cs")
    args = parser.parse_args()

    text = Path(args.input).read_text(encoding="utf-8")
    code = extract_csharp_code(text)

    required_tokens = ["[TestClass]", "[DataTestMethod]", "PurchaseService.Evaluate", "PurchaseRequest"]
    missing = [t for t in required_tokens if t not in code]
    if missing:
        raise ValueError(f"Generated code seems invalid. Missing tokens: {missing}")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(code, encoding="utf-8")

    print(f"Generated test file: {output}")


if __name__ == "__main__":
    main()
