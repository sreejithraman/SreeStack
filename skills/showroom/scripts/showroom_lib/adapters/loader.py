from __future__ import annotations

from typing import Any

from ..errors import AdapterError
from .base import EvidenceAdapter, RegisteredSurfaceAdapter
from .ios import get_adapter as ios_adapter
from .project_delivery import get_adapter as project_delivery_adapter
from .web_local import get_adapter as web_adapter


def load_adapter(name: str) -> Any:
    factories = {
        "evidence-only": EvidenceAdapter,
        "registered": RegisteredSurfaceAdapter,
        "ios-simulator": ios_adapter,
        "project-delivery": project_delivery_adapter,
        "web-local": web_adapter,
    }
    factory = factories.get(name)
    if factory is None:
        raise AdapterError(f"adapter is not installed: {name}")
    return factory()
