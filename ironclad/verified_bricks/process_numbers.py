def process_numbers(nums):
    count = len(nums)
    total = sum(nums)
    mean = total / count if count > 0 else None
    return {"count": count, "sum": total, "mean": mean}
