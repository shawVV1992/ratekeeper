"""
ratekeeper 包初始化。

对外建议通过 ratekeeper.api 中的函数使用：
- ratekeeper_init
- ratekeeper_update
"""

from .rates import initialize, update
__all__ = ["rates"]

