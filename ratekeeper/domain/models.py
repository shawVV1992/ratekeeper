"""
领域模型定义。
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RatekeeperRate:
    """
    汇率历史记录模型。

    所有字段含义与数据库表 exchange_rates 一一对应。
    """

    currency_name: str
    currency_name_cn: str
    spot_buying_rate: Optional[float]
    cash_buying_rate: Optional[float]
    spot_selling_rate: Optional[float]
    cash_selling_rate: Optional[float]
    boc_translation_rate: Optional[float]
    publication_date: str
    publication_time: str

    @classmethod
    def from_row(cls, row: Dict[str, Any]) -> "RatekeeperRate":
        """
        从数据库查询结果（dict）构建 RatekeeperRate 实例。
        """
        return cls(
            currency_name=row["currency_name"],
            currency_name_cn=row["currency_name_cn"],
            spot_buying_rate=row["spot_buying_rate"],
            cash_buying_rate=row["cash_buying_rate"],
            spot_selling_rate=row["spot_selling_rate"],
            cash_selling_rate=row["cash_selling_rate"],
            boc_translation_rate=row["boc_translation_rate"],
            publication_date=row["publication_date"],
            publication_time=row["publication_time"],
        )
