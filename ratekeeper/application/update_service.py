"""
汇率更新服务。
"""

from typing import List

from ratekeeper.infrastructure.db import init_database
from ratekeeper.infrastructure.showapi_client import fetch_and_store_rates


class RatekeeperUpdater:
    """
    ratekeeper 汇率更新服务封装。

    对上层提供 update_rates 接口，
    内部调用 showapi 并写入 SQLite。
    """

    @staticmethod
    def init_storage() -> None:
        """
        初始化存储（创建数据库和表）。
        """
        init_database()

    @staticmethod
    def update_rates(codes: List[str]) -> None:
        """
        更新指定币种的汇率数据。

        :param codes: 币种代码列表，如 ["USD", "EUR"]。
        """
        fetch_and_store_rates(codes)
