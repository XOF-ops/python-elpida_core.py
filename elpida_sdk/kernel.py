from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from immutable_kernel import kernel_check


@dataclass(slots=True)
class KernelCheckResult:
    allowed: bool
    reason: str
    kernel_rule: str
    domain: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KernelGuard:
    """Thin wrapper around immutable kernel checks for SDK/MCP use."""

    @staticmethod
    def check_text(text: str) -> KernelCheckResult:
        res = kernel_check(text)
        if res is None:
            return KernelCheckResult(
                allowed=True,
                reason="passed",
                kernel_rule="",
                domain="",
            )
        return KernelCheckResult(
            allowed=bool(res.get("allowed", False)),
            reason=str(res.get("reasoning", "")),
            kernel_rule=str(res.get("kernel_rule", "")),
            domain=str(res.get("domain", "")),
        )
