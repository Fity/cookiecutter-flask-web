from decimal import Decimal


def to_decimal(num) -> Decimal:
    if isinstance(num, float):
        return Decimal("{0:.2f}".format(num))
    if not isinstance(num, Decimal):
        return Decimal(num)
    return num
