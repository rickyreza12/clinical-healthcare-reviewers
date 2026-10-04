from backend.review.service import review_case


def finding(case_id: int, code: str):
    result = review_case(f"CASE-{case_id:03}")
    return next((item for item in result["findings"] if item.type.value == code), None), result
