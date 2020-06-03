def int_to_bigint(num):
    return num * (10 ** 18)


def int_to_bighexa(num):
    num = hex(int_to_bigint(num))
    return num


def from_bigint(num):
    if isinstance(num,int):
        return num / (10 ** 18)
    elif isinstance(num,float):
        return num / 10 ** 18


def from_bighexa(num):
    num = int(num, 16)
    return from_bigint(num)


def from_hex(num):
    return int(num, 16)


def sell_icx_find_ratio(icx, ratio):
    return icx / ratio


def sell_tap_find_ratio(tap, ratio):
    return tap * ratio


def float_from_bighexa(num):
    return float.fromhex(num) / (10 ** 18)


def float_to_bighexa(num):
    float.hex(num * (10 ** 18))



def float_value(num):
    num = int(format(num * (10 ** 18), ".0f"))
    return num
