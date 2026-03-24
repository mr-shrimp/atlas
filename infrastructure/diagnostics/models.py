from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict


class HealthCheckStatus(Enum):
    """Represents the connectivity or operational state of a system component.

    Enum values:
        CONNECTED (str): Service is fully operational and reachable.
        DISCONNECTED (str): Service is not reachable or not connected.
        DEGRADED (str): Service is operational but experiencing reduced performance
            or partial issues.
        FAILED (str): Service has encountered a failure and is not functioning correctly.
    """

    CONNECTED: str = "CONNECTED"
    DISCONNECTED: str = "DISCONNECTED"
    DEGRADED: str = "DEGRADED"
    FAILED: str = "FAILED"


class HealthCheckSeverity(Enum):
    """Represents the severity level associated with a health check result.

    Enum values:
        INFO (str): Informational state indicating normal operation.
        WARNING (str): Indicates a potential issue or suboptimal condition that
            does not yet critically impact functionality.
        CRITICAL (str): Indicates a severe issue requiring immediate attention.
    """

    INFO: str = "INFO"
    WARNING: str = "WARNING"
    CRITICAL: str = "CRITICAL"


@dataclass
class HealthCheckResult:
    """Represents the result of a single system health check.

    Encapsulates the status, severity, and diagnostic details of a service
    health check, along with a timestamp indicating when the check was performed.

    Attributes:
        service (str): The name or identifier of the service being checked.
        status (HealthCheckStatus): The current status of the service
            (e.g., CONNECTED, DEGRADED, FAILED).
        severity (HealthCheckSeverity): The severity level associated with
            the result (e.g., INFO, WARNING, CRITICAL).
        message (str, optional): A human-readable message describing the result.
            Defaults to an empty string.
        details (Dict[str, Any], optional): Additional structured metadata
            related to the health check (e.g., latency metrics). Defaults to an empty dict.
        timestamp (str): ISO 8601 UTC timestamp indicating when the result
            was generated. Automatically populated at instantiation time.
    """

    service: str
    status: HealthCheckStatus
    severity: HealthCheckSeverity
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self):
        """Converts the health check result into a serializable dictionary.

        Ensures that enum values for status and severity are converted to their
        underlying string representations for compatibility with JSON serialization
        and external consumers.

        Returns:
            dict: A dictionary representation of the health check result with keys:
                - service (str)
                - status (str)
                - severity (str)
                - message (str)
                - details (dict)
                - timestamp (str)

        Raises:
            Exception: Propagates any unexpected errors during serialization.

        Notes:
            - If `status` or `severity` are enums, their `.value` attribute is used.
            - If they are already strings, they are returned as-is.
            - This method is commonly used for API responses, logging, and reporting.
        """
        return {
            "service": self.service,
            "status": self.status.value
            if hasattr(self.status, "value")
            else self.status,
            "severity": self.severity.value
            if hasattr(self.severity, "value")
            else self.severity,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
        }
