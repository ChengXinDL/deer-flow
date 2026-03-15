import os
from pydantic import BaseModel, ConfigDict, Field


def _get_env_str(key: str, default: str | None = None) -> str | None:
    """Get string value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value if value.strip() else default


def _get_env_bool(key: str, default: bool | None = None) -> bool | None:
    """Get boolean value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    return value.lower() in ('true', '1', 'yes', 'y', 't')


def _get_env_int(key: str, default: int | None = None) -> int | None:
    """Get integer value from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class VolumeMountConfig(BaseModel):
    """Configuration for a volume mount."""

    host_path: str = Field(..., description="Path on the host machine")
    container_path: str = Field(..., description="Path inside the container")
    read_only: bool = Field(default=False, description="Whether the mount is read-only")


class SandboxConfig(BaseModel):
    """Config section for a sandbox.

    Common options:
        use: Class path of the sandbox provider (required)

    AioSandboxProvider specific options:
        image: Docker image to use (default: enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest)
        port: Base port for sandbox containers (default: 8080)
        base_url: If set, uses existing sandbox instead of starting new container
        auto_start: Whether to automatically start Docker container (default: true)
        container_prefix: Prefix for container names (default: magic-flow-sandbox)
        idle_timeout: Idle timeout in seconds before sandbox is released (default: 600 = 10 minutes). Set to 0 to disable.
        mounts: List of volume mounts to share directories with the container
        environment: Environment variables to inject into the container (values starting with $ are resolved from host env)
    """

    use: str = Field(
        default=_get_env_str("SANDBOX_USE", "src.sandbox.local:LocalSandboxProvider"),
        description="Class path of the sandbox provider (e.g. src.sandbox.local:LocalSandboxProvider)",
    )
    image: str | None = Field(
        default=_get_env_str("SANDBOX_IMAGE", "enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest"),
        description="Docker image to use for the sandbox container",
    )
    port: int | None = Field(
        default=_get_env_int("SANDBOX_PORT", 8080),
        description="Base port for sandbox containers",
    )
    base_url: str | None = Field(
        default=_get_env_str("SANDBOX_BASE_URL"),
        description="If set, uses existing sandbox at this URL instead of starting new container",
    )
    auto_start: bool | None = Field(
        default=_get_env_bool("SANDBOX_AUTO_START", True),
        description="Whether to automatically start Docker container",
    )
    container_prefix: str | None = Field(
        default=_get_env_str("SANDBOX_CONTAINER_PREFIX", "magic-flow-sandbox"),
        description="Prefix for container names",
    )
    idle_timeout: int | None = Field(
        default=_get_env_int("SANDBOX_IDLE_TIMEOUT", 600),
        description="Idle timeout in seconds before sandbox is released (default: 600 = 10 minutes). Set to 0 to disable.",
    )
    mounts: list[VolumeMountConfig] = Field(
        default_factory=list,
        description="List of volume mounts to share directories between host and container",
    )
    environment: dict[str, str] = Field(
        default_factory=dict,
        description="Environment variables to inject into the sandbox container. Values starting with $ will be resolved from host environment variables.",
    )

    model_config = ConfigDict(extra="allow")
