"""
ratekeeper 对外统一接口。

推荐外部程序只调用这里的三个函数：
- initialize()
- update()
- find()
"""

from typing import List, Optional

from ratekeeper.application.update_service import RatekeeperUpdater
from ratekeeper.domain.models import RatekeeperRate

# 内部服务实例，保持简单的全局单例
_updater_service = RatekeeperUpdater()


def initialize() -> None:
    """
    初始化 ratekeeper 存储环境（创建数据库和表）。
    建议在程序启动时调用一次。
    """
    _updater_service.init_storage()


def update(codes: Optional[List[str]] = None) -> None:
    """
    主动更新指定币种的汇率到本地数据库。

    :param codes: 币种代码列表，例如 ["USD", "EUR"]。
                  默认为 ["USD", "EUR"]。
    """
    if codes is None:
        codes = ["USD", "EUR"]
    _updater_service.update_rates(codes)


