from backend.domain.enums import ReviewStatus


def aggregate_status(findings) -> ReviewStatus:
    return ReviewStatus.NEEDS_REVIEW if findings else ReviewStatus.CLEAR
