def get_minmaxdiv(startdiv, numerator, direction=-1):
    print(startdiv)
    startdiv = int(startdiv)
    if startdiv < 2 and direction == 1:
        startdiv += 1
    #elif startdiv > numerator//2 and direction == 1:
    #    raise ValueError("Divisor became too high.")
    if direction == 1:
        rangelist = [startdiv, 2*startdiv, 1]
    elif direction == -1:
        rangelist = [startdiv, startdiv//2, -1]
    else:
        raise ValueError("Wrong input for direction. Choose either -1 or 1.")
    if numerator % startdiv != 0:
        for new_div in range(*rangelist):
            if numerator % new_div == 0:
                print("found it", new_div)
                return new_div
        new_startdiv = int(startdiv*(2*direction))
        print('No value found. Restarting with {} as start value'.format(new_startdiv))
        return get_minmaxdiv(new_startdiv, numerator, direction)
    else:
        return startdiv