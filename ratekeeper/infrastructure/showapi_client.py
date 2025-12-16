"""
showapi 接口调用与写库逻辑。

当前使用接口：105-30
请求方式：HTTPS POST，Content-Type: application/x-www-form-urlencoded
"""

from typing import Any, Dict, List, Optional

import requests
import logging
from ratekeeper.infrastructure.db import get_latest_row, insert_rate_batch
from ratekeeper.config import SHOWAPI_APPKEY  # 🔸 从项目配置读取 appKey
from ratekeeper.infrastructure.db import APP_DIR
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename=APP_DIR / "ratekeeper_update.log",
    filemode="a",
)

# showapi 接口配置
SHOWAPI_URL = "https://route.showapi.com/105-30"


def _to_float(value: Any) -> Optional[float]:
    """
    安全地将接口返回值转换为 float。
    空字符串或无效值返回 None。
    """
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def fetch_rates_from_showapi(code: str) -> List[Dict[str, Any]]:
    """
    调用 showapi 获取指定币种的汇率列表，并转换为内部统一结构。

    :param code: 币种代码，例如 "USD"、"EUR"。
    :return: 每个元素为 dict 的列表，包含写库所需字段。
    """
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    params = {"appKey": SHOWAPI_APPKEY}
    data = {"code": code}

    resp = requests.post(
        SHOWAPI_URL,
        params=params,
        data=data,
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    j = resp.json()

    # 顶层错误判断
    if j.get("showapi_res_code") != 0:
        raise RuntimeError(
            f"showapi error: res_code={j.get('showapi_res_code')}, "
            f"err={j.get('showapi_res_error')}"
        )

    body = j.get("showapi_res_body", {})
    if body.get("ret_code") != 0:
        raise RuntimeError(f"showapi body error: ret_code={body.get('ret_code')}")

    lst = body.get("list", []) or []
    records: List[Dict[str, Any]] = []

    for item in lst:
        # item 示例：
        # {
        #   "hui_in": "704.62",
        #   "time": "20:47:05",
        #   "chao_out": "707.58",
        #   "chao_in": "704.62",
        #   "hui_out": "707.58",
        #   "name": "美元",
        #   "zhesuan": "706.86",
        #   "code": "USD",
        #   "day": "2025-12-11"
        # }

        code_en = item.get("code", code)
        name_cn = item.get("name") or code_en  # 保底不为 None

        records.append(
            {
                "currency_name": code_en,
                "currency_name_cn": name_cn,
                "spot_buying_rate": _to_float(item.get("hui_in")),
                "cash_buying_rate": _to_float(item.get("chao_in")),
                "spot_selling_rate": _to_float(item.get("hui_out")),
                "cash_selling_rate": _to_float(item.get("chao_out")),
                "boc_translation_rate": _to_float(item.get("zhesuan")),
                "publication_date": item.get("day"),
                "publication_time": item.get("time"),
            }
        )

    return records


def _is_duplicate(latest: Dict[str, Any], new_rec: Dict[str, Any]) -> bool:
    """
    判断 new_rec 是否与 latest 记录重复。

    当前策略：比较五个价格字段是否完全一致。
    """
    if latest is None:
        return False

    fields = [
        "spot_buying_rate",
        "cash_buying_rate",
        "spot_selling_rate",
        "cash_selling_rate",
        "boc_translation_rate",
    ]
    return all(latest.get(f) == new_rec.get(f) for f in fields)


def fetch_and_store_rates(codes: List[str]) -> None:
    """
    拉取多个币种的汇率数据，并在去重后写入数据库。

    :param codes: 币种代码列表，例如 ["USD", "EUR"]。
    """
    to_insert: List[Dict[str, Any]] = []

    for code in codes:
        try:
            records = fetch_rates_from_showapi(code)
        except Exception as exc:  # noqa: BLE001
            logging.error(f"fetch {code} failed: {exc}")
            continue

        for rec in records:
            latest = get_latest_row(rec["currency_name"])
            if _is_duplicate(latest, rec):
                logging.info(
                    f"skip duplicate {rec['currency_name']} "
                    f"@ {rec['publication_date']} {rec['publication_time']}"
                )
                continue
            to_insert.append(rec)

    if to_insert:
        insert_rate_batch(to_insert)
        logging.info(f"inserted {len(to_insert)} new records.")
    else:
        logging.info("no new records to insert.")
