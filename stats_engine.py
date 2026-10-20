"""
Pure-Python statistics engine (no numpy / statistics module).
Merge sort, mean, median, mode, variance, std dev, quartiles,
IQR outlier detection and Pearson correlation - all written from scratch.
"""


def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))


def merge(left, right):
    sorted_arr = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            sorted_arr.append(left[i])
            i += 1
        else:
            sorted_arr.append(right[j])
            j += 1
    sorted_arr.extend(left[i:])     # leftovers from either side
    sorted_arr.extend(right[j:])
    return sorted_arr


def _sqrt(x):
    """Square root using Newton's method."""
    if x <= 0:
        return 0.0
    guess = x / 2.0 if x > 1 else 1.0
    for _ in range(40):
        guess = (guess + x / guess) / 2.0
    return guess


def calculate_mean(data):
    if not data:
        return 0.0
    total = 0
    for num in data:
        total += num
    return total / len(data)


def calculate_median(data):
    if not data:
        return 0.0
    sorted_data = merge_sort(list(data))
    n = len(sorted_data)
    mid = n // 2
    if n % 2 == 1:
        return float(sorted_data[mid])
    return (sorted_data[mid - 1] + sorted_data[mid]) / 2.0


def calculate_mode(data):
    if not data:
        return []
    frequency = {}
    for num in data:
        frequency[num] = frequency.get(num, 0) + 1
    max_count = max(frequency.values())
    return [num for num, count in frequency.items() if count == max_count]


def calculate_variance(data):
    """Population variance (divides by n)."""
    if len(data) < 2:
        return 0.0
    mean_val = calculate_mean(data)
    total = 0.0
    for x in data:
        total += (x - mean_val) ** 2
    return total / len(data)


def calculate_std_dev(data):
    return _sqrt(calculate_variance(data))


def calculate_quartiles(data):
    """Q1 and Q3 = medians of the lower and upper halves."""
    if len(data) < 4:
        return 0.0, 0.0
    sorted_data = merge_sort(list(data))
    n = len(sorted_data)
    mid = n // 2
    lower_half = sorted_data[:mid]
    upper_half = sorted_data[mid:] if n % 2 == 0 else sorted_data[mid + 1:]
    return calculate_median(lower_half), calculate_median(upper_half)


def detect_outliers_iqr(data):
    """Flag values outside Q1 - 1.5*IQR and Q3 + 1.5*IQR."""
    if len(data) < 4:
        return {"clean_data": list(data), "outliers": []}

    q1, q3 = calculate_quartiles(data)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    clean_data, outliers = [], []
    for x in data:
        if x < lower_bound or x > upper_bound:
            outliers.append(x)
        else:
            clean_data.append(x)

    return {
        "q1": q1, "q3": q3, "iqr": iqr,
        "lower_bound": lower_bound, "upper_bound": upper_bound,
        "clean_data": clean_data, "outliers": outliers,
    }


def calculate_pearson_correlation(x_data, y_data):
    if len(x_data) != len(y_data) or len(x_data) < 2:
        return 0.0
    mean_x, mean_y = calculate_mean(x_data), calculate_mean(y_data)
    covariance = var_x = var_y = 0.0
    for i in range(len(x_data)):
        dx, dy = x_data[i] - mean_x, y_data[i] - mean_y
        covariance += dx * dy
        var_x += dx ** 2
        var_y += dy ** 2
    if var_x == 0 or var_y == 0:
        return 0.0
    return covariance / _sqrt(var_x * var_y)


if __name__ == "__main__":
    sample = [42, 12, 7, 12, 89, 23, 7, 12]
    print("sorted :", merge_sort(sample))
    print("mean   :", round(calculate_mean(sample), 2))
    print("median :", calculate_median(sample))
    print("mode   :", calculate_mode(sample))
    raw = [12, 15, 14, 16, 15, 13, 15, 14, 999, -50, 16, 14]
    res = detect_outliers_iqr(raw)
    print("outliers:", res["outliers"], "| clean mean:", round(calculate_mean(res["clean_data"]), 2))
