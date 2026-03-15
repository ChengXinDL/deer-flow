import os
from pathlib import Path

from pydantic import BaseModel, Field


def _get_env_str(key: str, default: str | None = None) -> str | None:
    """Get string value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value if value.strip() else default


class SkillsConfig(BaseModel):
    """Configuration for skills system"""

    path: str | None = Field(
        default=_get_env_str("SKILLS_PATH"),
        description="Path to skills directory. If not specified, defaults to ../skills relative to backend directory",
    )
    container_path: str = Field(
        default=_get_env_str("SKILLS_CONTAINER_PATH", "/mnt/skills"),
        description="Path where skills are mounted in the sandbox container",
    )

    def get_skills_path(self) -> Path:
        """
        Get the resolved skills directory path.

        Returns:
            Path to the skills directory
        """
        if self.path:
            # Use configured path (can be absolute or relative)
            path = Path(self.path)
            if not path.is_absolute():
                # If relative, resolve from current working directory
                path = Path.cwd() / path
            return path.resolve()
        else:
            # Default: ../skills relative to backend directory
            from src.skills.loader import get_skills_root_path

            return get_skills_root_path()

    def get_skill_container_path(self, skill_name: str, category: str = "public") -> str:
        """
        Get the full container path for a specific skill.

        Args:
            skill_name: Name of the skill (directory name)
            category: Category of the skill (public or custom)

        Returns:
            Full path to the skill in the container
        """
        return f"{self.container_path}/{category}/{skill_name}"
