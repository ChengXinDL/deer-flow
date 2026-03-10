import re
from pathlib import Path

from .types import Skill


def parse_skill_file(skill_file: Path, category: str, relative_path: Path | None = None) -> Skill | None:
    """
    Parse a SKILL.md file and extract metadata.

    Args:
        skill_file: Path to the SKILL.md file
        category: Category of the skill ('public' or 'custom')

    Returns:
        Skill object if parsing succeeds, None otherwise
    """
    if not skill_file.exists() or skill_file.name != "SKILL.md":
        return None

    try:
        content = _read_file_with_fallback_encoding(skill_file)

        # Extract YAML front matter
        # Pattern: ---\nkey: value\n---
        front_matter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)

        if not front_matter_match:
            return None

        front_matter = front_matter_match.group(1)

        # Parse YAML front matter (simple key-value parsing)
        metadata = {}
        for line in front_matter.split("\n"):
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip()

        # Extract required fields
        name = metadata.get("name")
        description = metadata.get("description")

        if not name or not description:
            return None

        license_text = metadata.get("license")

        return Skill(
            name=name,
            description=description,
            license=license_text,
            skill_dir=skill_file.parent,
            skill_file=skill_file,
            relative_path=relative_path or Path(skill_file.parent.name),
            category=category,
            enabled=True,  # Default to enabled, actual state comes from config file
        )

    except Exception as e:
        print(f"Error parsing skill file {skill_file}: {e}")
        return None


def _read_file_with_fallback_encoding(file_path: Path) -> str:
    """
    Read file content with fallback encoding support.
    
    Tries UTF-8 first, then falls back to other common encodings.
    Replaces invalid characters with a placeholder if all encodings fail.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
    """
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"]
    
    for encoding in encodings:
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    
    try:
        return file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return file_path.read_bytes().decode("utf-8", errors="replace")
