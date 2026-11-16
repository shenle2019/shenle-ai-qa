"""第 7 章实战：一个能直接用的小型测试数据工具箱。

三个模块：
- ``validators``：手机号 / 邮箱 / 身份证 / 金额的校验
- ``datagen``：唯一手机号、邮箱、姓名、订单号生成
- ``fixtures``：把数据写成 json / csv 文件，供接口和 UI 用例读取
"""

from .datagen import DataGen, unique_email, unique_order_no, unique_phone
from .fixtures import dump_csv, dump_json, load_json, write_text
from .validators import (
    ValidationError,
    is_email,
    is_id_card,
    is_money,
    is_phone,
    require,
)

__all__ = [
    "DataGen",
    "ValidationError",
    "dump_csv",
    "dump_json",
    "is_email",
    "is_id_card",
    "is_money",
    "is_phone",
    "load_json",
    "require",
    "unique_email",
    "unique_order_no",
    "unique_phone",
    "write_text",
]
