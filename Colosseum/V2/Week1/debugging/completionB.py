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
