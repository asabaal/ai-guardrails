def merge_sorted_lists(a, b):
    # Merge two sorted lists into a single sorted list
    result = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i])
            i += 1
        else:
            result.append(b[j])
            j += 1
    # Append any remaining elements
    result.extend(a[i:])
    result.extend(b[j:])
    return result
