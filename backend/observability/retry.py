from dataclasses import dataclass


@dataclass(frozen=True)
class RetryOutcome:
    retries: int
    outcome: str


def retry_outcome(retries: int, succeeded: bool) -> RetryOutcome:
    if retries < 0:
        raise ValueError("retries must not be negative")
    return RetryOutcome(retries, "success" if succeeded else "failed")
