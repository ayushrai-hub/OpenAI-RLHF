# ideal_completion.py

def remove_isolated_true(arr):
    result = []
    first_true = False
    for item in arr:
        if item:
            if first_true:
                continue
            first_true = True
            result.append(item)
        else:
            first_true = False
            result.append(item)
    return result