def isfloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False