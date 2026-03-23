from infrastructure.diagnostics.models import HealthCheckSeverity, HealthCheckStatus

CHECKS = []


def register_check(fn):
    """Registers a health check function in the global check registry.

    This decorator adds the decorated function to the CHECKS collection,
    allowing it to be discovered and executed by the health check runner.

    Args:
        fn (Callable): The health check function to register. The function
            must take no arguments and return a HealthCheckResult.

    Returns:
        Callable: The original function, unmodified.

    Side Effects:
        - Appends the function to the global CHECKS list.

    Notes:
        - Intended to be used as a decorator (e.g., @register_check).
        - Registered functions are executed by `run_all_checks`.
    """
    CHECKS.append(fn)
    return fn


def run_all_checks():
    """Executes all registered health checks and aggregates their results.

    Iterates through all functions registered via `register_check`, executes
    each one, and collects their results. If a check raises an exception,
    a fallback failure result is generated to ensure consistent output.

    Returns:
        list: A list of health check results. Each item is either:
            - A HealthCheckResult object returned by a check, or
            - A dictionary representing a failed check with keys:
                - service (str): Name of the check function.
                - status (HealthCheckStatus): FAILED.
                - severity (HealthCheckSeverity): CRITICAL.
                - message (str): Error message from the exception.
                - details (dict): Empty dictionary.

    Raises:
        Exception: This function does not raise exceptions directly. Any
            exceptions from individual checks are caught and converted into
            failure results.

    Behavior:
        - Executes each registered check sequentially.
        - Captures and normalizes exceptions into failure results.
        - Ensures all checks contribute to the final result set, even if some fail.

    Side Effects:
        - Executes all registered health check functions.
        - May trigger network, database, or system interactions depending on checks.

    Notes:
        - The CHECKS registry must be populated prior to invocation.
        - Returned results may be heterogeneous (objects and dicts), so downstream
          consumers should normalize if strict typing is required.
    """
    results = []

    for check in CHECKS:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            results.append(
                {
                    "service": check.__name__,
                    "status": HealthCheckStatus.FAILED,
                    "severity": HealthCheckSeverity.CRITICAL,
                    "message": str(e),
                    "details": {},
                }
            )
    return results
