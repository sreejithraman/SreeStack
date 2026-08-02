from __future__ import annotations

from pathlib import Path
from typing import Any

from ..apple import delivery_environment
from ..delivery import describe, run_delivery
from ..errors import AdapterError
from .base import AdapterContext


class ProjectDeliveryAdapter:
    name = "project-delivery"

    def _surface(self, context: AdapterContext) -> tuple[dict[str, Any], dict[str, Any]]:
        config = context.config
        if not config.delivery or config.surface_name not in {"device", "testflight"}:
            raise AdapterError("project delivery needs a configured device or testflight surface")
        description = describe(config.delivery, config.working_directory)
        surface = description["surfaces"].get(config.surface_name)
        if surface is None:
            raise AdapterError(f"delivery command does not support {config.surface_name}")
        return description, surface

    def start(self, record: dict[str, Any], context: AdapterContext) -> dict[str, Any]:
        _, surface = self._surface(context)
        arguments = dict(context.approvals.get("delivery_arguments", {}))
        surface_name = context.config.surface_name or ""
        with delivery_environment(
            context.state_root,
            surface=surface_name,
            operation="start",
            required="apple" in surface["start_credentials"],
        ) as environment:
            result = run_delivery(
                command=context.config.delivery or (),
                operation_argv=surface["start"],
                surface=surface_name,
                operation="start",
                arguments=arguments,
                required_arguments=surface["required_arguments"],
                worktree=context.config.working_directory,
                showroom_dir=context.showroom_dir,
                environment=environment,
            )
        owner = surface["lifecycle_owner"]
        provider = result["provider"] or surface["provider"]
        if surface["provider"] and result["provider"] not in {None, surface["provider"]}:
            raise AdapterError("delivery result provider does not match its description")
        if owner == "manual" and (provider or result["provider_resource_id"]):
            raise AdapterError("manual delivery result cannot claim a provider resource")
        if (
            owner == "provider"
            and result["verification"]["status"] == "passed"
            and not result["provider_resource_id"]
        ):
            raise AdapterError("verified provider-owned delivery result needs provider_resource_id")
        return {
            "status": "active",
            "type": context.config.surface_name,
            "lifecycle_owner": owner,
            "cleanup_policy": "provider" if owner == "provider" else "lease",
            "provider": provider,
            "provider_resource_id": result["provider_resource_id"],
            "surface": result["location"],
            "verification": result["verification"],
            "evidence_paths": result["evidence_paths"],
            "log_paths": result["log_paths"],
            "availability_limitations": result["availability_limitations"],
            "timestamps": {"expires_at": None if owner == "provider" else record["timestamps"]["expires_at"]},
            "resources": {
                "delivery": {
                    "command": list(context.config.delivery or ()),
                    "verify": list(surface["verify"]),
                    "required_arguments": list(surface["required_arguments"]),
                    "arguments": arguments,
                    "surface": context.config.surface_name,
                    "verify_credentials": list(surface["verify_credentials"]),
                }
            },
        }

    def verify(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        if context is None:
            raise AdapterError("delivery worktree is unavailable")
        delivery = record.get("resources", {}).get("delivery", {})
        command = tuple(delivery.get("command", ()))
        verify_argv = tuple(delivery.get("verify", ()))
        surface = delivery.get("surface")
        if not command or not verify_argv or surface not in {"device", "testflight"}:
            raise AdapterError("delivery record is missing its verification command")
        with delivery_environment(
            context.state_root,
            surface=surface,
            operation="verify",
            required="apple" in delivery.get("verify_credentials", ()),
        ) as environment:
            result = run_delivery(
                command=command,
                operation_argv=verify_argv,
                surface=surface,
                operation="verify",
                arguments=dict(delivery.get("arguments", {})),
                required_arguments=tuple(delivery.get("required_arguments", ())),
                worktree=context.project.worktree_root,
                showroom_dir=context.showroom_dir,
                environment=environment,
            )
        expected_provider = record.get("provider")
        if expected_provider and result["provider"] not in {None, expected_provider}:
            raise AdapterError("delivery verification provider changed")
        if record.get("lifecycle_owner") == "manual" and (
            result["provider"] or result["provider_resource_id"]
        ):
            raise AdapterError("manual delivery verification cannot claim a provider resource")
        expected_resource = record.get("provider_resource_id")
        if (
            expected_resource
            and result["provider_resource_id"]
            and result["provider_resource_id"] != expected_resource
        ):
            raise AdapterError("delivery verification provider resource changed")
        if (
            record.get("lifecycle_owner") == "provider"
            and result["verification"]["status"] == "passed"
            and not (result["provider_resource_id"] or record.get("provider_resource_id"))
        ):
            raise AdapterError("verified provider-owned delivery result needs provider_resource_id")
        return {
            "surface": result["location"],
            "verification": result["verification"],
            "provider": result["provider"] or record.get("provider"),
            "provider_resource_id": result["provider_resource_id"] or record.get("provider_resource_id"),
            "evidence_paths": result["evidence_paths"],
            "log_paths": result["log_paths"],
            "availability_limitations": result["availability_limitations"],
        }

    def stop(self, record: dict[str, Any], context: AdapterContext | None) -> dict[str, Any]:
        return {
            "status": "stopped",
            "verification": {"status": "stale", "detail": "Showroom record stopped; external resource is unchanged"},
        }


def get_adapter() -> ProjectDeliveryAdapter:
    return ProjectDeliveryAdapter()
