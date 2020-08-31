from voluptuous import ValueInvalid

from {{cookiecutter.pkg_name}}.api import InvalidInput
from {{cookiecutter.pkg_name}}.utils import to_decimal


def strip_str(value):
    if value is None:
        raise ValueInvalid("参数不能为空")
    return str(value).strip()


def decimal(num):
    try:
        return to_decimal(num)
    except Exception as e:
        raise InvalidInput("不是有效的数字") from e
