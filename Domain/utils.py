def isfloat(string):
    try:
        if string is None:
            return False
        float(string)
        return True
    except ValueError:
        return False