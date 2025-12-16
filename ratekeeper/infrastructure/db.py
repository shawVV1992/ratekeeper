"""
SQLite 数据库访问封装。

数据库文件位置（推荐方案 A）：
    Windows: %LOCALAPPDATA\\ratekeeper\\fx_rates.db

示例路径：
    C:\\Users\\<用户名>\\AppData\\Local\\ratekeeper\\fx_rates.db
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

# -----------------------------------------------------------------------------
# 数据库文件路径设置（方案 A）
# -----------------------------------------------------------------------------

# 获取用户本地应用数据目录（如 C:\Users\<User>\AppData\Local）
LOCAL_APPDATA = os.getenv("LOCALAPPDATA")

if LOCAL_APPDATA is None:
    # 理论上 Windows 都会有这个环境变量，这里只是兜底
    APP_DIR = Path.cwd() / "ratekeeper_data"
else:
    APP_DIR = Path(LOCAL_APPDATA) / "ratekeeper"

# 确保目录存在
APP_DIR.mkdir(parents=True, exist_ok=True)

# 最终数据库文件路径
DB_PATH = APP_DIR / "ratekeeper.db"


@contextmanager
def get_conn():
    """
    获取 SQLite 连接的上下文管理器。
    使用方式：
        with get_conn() as conn:
            ...
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_database() -> None:
    """
    初始化数据库和表结构。
    如果数据库文件不存在，会自动创建。
    如果表不存在，则创建表。
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS exchange_rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                -- 货币代码（英文），例如 USD/EUR
                currency_name                 TEXT NOT NULL,

                -- 货币名称（中文），例如 美元/欧元
                currency_name_cn              TEXT NOT NULL,

                -- 现汇买入（hui_in）
                spot_buying_rate              REAL,
                -- 现钞买入（chao_in）
                cash_buying_rate              REAL,
                -- 现汇卖出（hui_out）
                spot_selling_rate             REAL,
                -- 现钞卖出（chao_out）
                cash_selling_rate             REAL,
                -- 中行折算价（zhesuan）
                boc_translation_rate          REAL,

                -- 发布日期与发布时间
                publication_date              TEXT NOT NULL,  -- 格式: YYYY-MM-DD
                publication_time              TEXT NOT NULL,  -- 格式: HH:MM:SS

                -- 插入时间（本地）
                created_at                    TEXT NOT NULL DEFAULT (datetime('now')),

                -- 同一币种同一发布时间只存一条记录
                UNIQUE(currency_name, publication_date, publication_time)
            );
            """
        )
        conn.commit()


def insert_rate_batch(records: List[Dict[str, Any]]) -> None:
    """
    批量写入汇率记录。

    :param records: 每个元素为 dict，包含字段：
        currency_name, currency_name_cn,
        spot_buying_rate, cash_buying_rate,
        spot_selling_rate, cash_selling_rate, boc_translation_rate,
        publication_date, publication_time
    """
    if not records:
        return

    with get_conn() as conn:
        cur = conn.cursor()
        rows = [
            (
                r["currency_name"].upper(),
                r["currency_name_cn"],
                r.get("spot_buying_rate"),
                r.get("cash_buying_rate"),
                r.get("spot_selling_rate"),
                r.get("cash_selling_rate"),
                r.get("boc_translation_rate"),
                r["publication_date"],
                r["publication_time"],
            )
            for r in records
        ]
        cur.executemany(
            """
            INSERT OR IGNORE INTO exchange_rates (
                currency_name,
                currency_name_cn,
                spot_buying_rate,
                cash_buying_rate,
                spot_selling_rate,
                cash_selling_rate,
                boc_translation_rate,
                publication_date,
                publication_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()


def query_history_rows(
    currency_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    查询历史汇率原始行数据（用于上层封装为模型）。

    :param currency_name: 币种代码，如 "USD"。
    :param start_date: 起始日期（含），"YYYY-MM-DD"，可选。
    :param end_date: 结束日期（含），"YYYY-MM-DD"，可选。
    :return: dict 列表。
    """
    with get_conn() as conn:
        cur = conn.cursor()
        sql = """
            SELECT
                currency_name,
                currency_name_cn,
                spot_buying_rate,
                cash_buying_rate,
                spot_selling_rate,
                cash_selling_rate,
                boc_translation_rate,
                publication_date,
                publication_time
            FROM exchange_rates
            WHERE currency_name = ?
        """
        params: List[Any] = [currency_name.upper()]

        if start_date:
            sql += " AND publication_date >= ?"
            params.append(start_date)
        if end_date:
            sql += " AND publication_date <= ?"
            params.append(end_date)

        sql += " ORDER BY publication_date ASC, publication_time ASC"
        cur.execute(sql, params)
        rows = cur.fetchall()

    return [
        {
            "currency_name": r[0],
            "currency_name_cn": r[1],
            "spot_buying_rate": r[2],
            "cash_buying_rate": r[3],
            "spot_selling_rate": r[4],
            "cash_selling_rate": r[5],
            "boc_translation_rate": r[6],
            "publication_date": r[7],
            "publication_time": r[8],
        }
        for r in rows
    ]


def get_latest_row(currency_name: str) -> Optional[Dict[str, Any]]:
    """
    获取某币种最新的一条记录（按日期和时间降序）。

    :param currency_name: 币种代码。
    :return: dict 或 None。
    """
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT
                currency_name,
                currency_name_cn,
                spot_buying_rate,
                cash_buying_rate,
                spot_selling_rate,
                cash_selling_rate,
                boc_translation_rate,
                publication_date,
                publication_time
            FROM exchange_rates
            WHERE currency_name = ?
            ORDER BY publication_date DESC, publication_time DESC
            LIMIT 1
            """,
            (currency_name.upper(),),
        )
        row = cur.fetchone()

    if row is None:
        return None

    return {
        "currency_name": row[0],
        "currency_name_cn": row[1],
        "spot_buying_rate": row[2],
        "cash_buying_rate": row[3],
        "spot_selling_rate": row[4],
        "cash_selling_rate": row[5],
        "boc_translation_rate": row[6],
        "publication_date": row[7],
        "publication_time": row[8],
    }
