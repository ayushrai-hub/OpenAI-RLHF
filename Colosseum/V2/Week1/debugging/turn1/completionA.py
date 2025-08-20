def deepfilter(func, array):
    if array == []:
        return array
    elif type(array) is not list:
        if func(array):
            return array
        else:
            return []
    else:
        filtered = [deepfilter(func, x) for x in array]
        return [x for x in filtered if x != []]

def is_even(n): return n % 2 == 0
deepfilter(is_even, [1, 2, [3, 4, 5], 6]) # returns [2, [4], 6]
