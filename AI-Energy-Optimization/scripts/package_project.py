"""Create a clean source ZIP with an auditable file manifest and byte verification."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    excluded = {
        "node_modules",
        ".venv",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "dist",
        "build",
        "runtime",
    }
    files = []
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or path.resolve() == output:
            continue
        if any(part in excluded or part.endswith(".egg-info") for part in rel.parts):
            continue
        if path.suffix == ".pyc" or path.name in {
            ".env",
            "pytest-final.txt",
            "DELIVERY_MANIFEST.json",
        }:
            continue
        if rel.parts[0] == "experiments" and path.suffix.lower() in {
            ".png",
            ".jpg",
            ".webp",
        }:
            continue
        files.append((path, rel))
    manifest = {
        "files": [
            {
                "path": rel.as_posix(),
                "bytes": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path, rel in files
        ],
        "excluded": "Dependencies, caches, runtime state, build output, internal browser screenshots and the manifest itself. Original application image assets are preserved.",
    }
    manifest_path = ROOT / "DELIVERY_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    files.append((manifest_path, Path("DELIVERY_MANIFEST.json")))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, rel in files:
            archive.write(path, Path("AI-Energy-Optimization") / rel)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        for path, rel in files:
            assert (
                hashlib.sha256(
                    archive.read("AI-Energy-Optimization/" + rel.as_posix())
                ).digest()
                == hashlib.sha256(path.read_bytes()).digest()
            )
        assert (
            "AI-Energy-Optimization/frontend/src/assets/hero.png" in archive.namelist()
        )
        for name in [
            "README.md",
            "SETUP.md",
            "setup.py",
            "requirements.txt",
            "TESTING.md",
            "RESEARCH_GAP_MAPPING.md",
            "MODEL_EVALUATION.md",
            "PHASE_IMPLEMENTATION.md",
            "API_DOCUMENTATION.md",
        ]:
            assert "AI-Energy-Optimization/" + name in archive.namelist()
    print(
        json.dumps(
            {
                "archive": str(output),
                "bytes": output.stat().st_size,
                "files": len(files),
                "integrity": "CRC and all-file SHA256 passed",
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            }
        )
    )


if __name__ == "__main__":
    main()
