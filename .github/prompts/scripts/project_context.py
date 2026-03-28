from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class ProjectContext:
    language: str
    test_framework: str
    test_project_path: Path
    generated_test_file: Path


def _text_or_empty(elem: ET.Element | None) -> str:
    return elem.text.strip() if elem is not None and elem.text else ""


def infer_project_context() -> ProjectContext:
    # Current implementation supports C# project inference.
    csproj_files = sorted(Path("src").rglob("*.csproj"))
    if not csproj_files:
        raise ValueError("No project files found under src/.")

    test_candidates: list[tuple[Path, ET.Element]] = []
    for path in csproj_files:
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        is_test = any(
            _text_or_empty(pg.find("IsTestProject")).lower() == "true"
            for pg in root.findall("PropertyGroup")
        )
        if is_test:
            test_candidates.append((path, root))

    if not test_candidates:
        raise ValueError("No test project detected (IsTestProject=true).")

    test_project_path, root = test_candidates[0]
    package_names = {
        pr.attrib.get("Include", "")
        for ig in root.findall("ItemGroup")
        for pr in ig.findall("PackageReference")
    }

    if "MSTest.TestFramework" in package_names:
        framework = "mstest"
        file_name = "MatrixAiTests.cs"
    elif "xunit" in package_names:
        framework = "xunit"
        file_name = "MatrixAiTests.cs"
    elif "NUnit" in package_names:
        framework = "nunit"
        file_name = "MatrixAiTests.cs"
    else:
        framework = "unknown"
        file_name = "MatrixAiTests.cs"

    generated_file = test_project_path.parent / "Generated" / file_name
    return ProjectContext(
        language="csharp",
        test_framework=framework,
        test_project_path=test_project_path,
        generated_test_file=generated_file,
    )

