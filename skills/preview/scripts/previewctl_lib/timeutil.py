from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from .errors import ConfigurationError


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ConfigurationError(f"invalid timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def now() -> datetime:
    override = os.environ.get("PREVIEWCTL_NOW")
    return parse_time(override) if override else datetime.now(timezone.utc)


def format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def expires_at(current: datetime, hours: float | None) -> str | None:
    return None if hours is None else format_time(current + timedelta(hours=hours))
