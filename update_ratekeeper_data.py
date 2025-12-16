"""
单次汇率抓取脚本。

推荐由 Windows 任务计划程序在工作日的指定时间运行。
示例触发时间：
- 10:32
- 10:33
- 10:35
- 10:37
"""

from ratekeeper.rates import initialize, update


def main() -> None:
    """
    初始化存储并更新美元和欧元的汇率。
    """

    initialize()
    update(["USD", "EUR"])


if __name__ == "__main__":
    main()
