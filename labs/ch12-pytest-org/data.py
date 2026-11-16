"""分页参数的边界表：一处定义，参数化复用。"""

from __future__ import annotations

PAGE_SIZE_CASES = [
    (1, 200),
    (10, 200),
    (100, 200),
    (101, 422),
    (0, 422),
    (-1, 422),
]

PAGE_SIZE_IDS = ["min", "normal", "max", "over", "zero", "negative"]

USER_PAYLOADS = [
    ({"name": "u-minimal"}, 201),
    ({"name": "u-role", "role": "tester"}, 201),
    ({"name": ""}, 422),
    ({}, 422),
    ({"name": "x" * 200}, 201),
]

USER_PAYLOAD_IDS = ["minimal", "with-role", "empty-name", "missing-name", "long-name"]
