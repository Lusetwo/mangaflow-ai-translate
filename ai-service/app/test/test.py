
from __future__ import annotations

import csv
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# =========================
# 配置
# =========================

BASE_URL = "https://api.binance.com"
SYMBOL = "SOLUSDT"
INTERVAL = "1h"

# 下跌目标：上月收盘价下跌 1%
DROP_PCT = Decimal("0.01")

# 上涨限制：本月开盘价上涨 33%
RISE_PCT = Decimal("0.33")

OUTPUT_CSV = Path("sol_monthly_sequence_results.csv")


# =========================
# HTTP 客户端
# =========================

session = requests.Session()

retry = Retry(
    total=5,
    connect=5,
    read=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
)

adapter = HTTPAdapter(max_retries=retry)
session.mount("https://", adapter)


def api_get(path: str, params: dict) -> list:
    response = session.get(
        f"{BASE_URL}{path}",
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    result = response.json()

    if not isinstance(result, list):
        raise RuntimeError(f"Binance API 返回异常：{result}")

    return result


# =========================
# 时间处理
# =========================

def month_start_ms(year: int, month: int) -> int:
    dt = datetime(year, month, 1, tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


def next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def month_range(start_year: int, start_month: int,
                end_year: int, end_month: int):
    year, month = start_year, start_month

    while (year, month) <= (end_year, end_month):
        yield year, month
        year, month = next_month(year, month)


def month_name(year: int, month: int) -> str:
    return f"{year:04d}-{month:02d}"


# =========================
# 拉取历史数据
# =========================

def get_first_kline() -> dict:
    """
    获取交易对最早可查询的 1 小时 K 线。
    """
    data = api_get(
        "/api/v3/klines",
        {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "startTime": 0,
            "limit": 1,
        },
    )

    if not data:
        raise RuntimeError(
            f"没有查询到 {SYMBOL} 的历史 K 线，请检查交易对或 API 状态。"
        )

    return parse_kline(data[0])


def parse_kline(k: list) -> dict:
    return {
        "open_time": int(k[0]),
        "open": Decimal(k[1]),
        "high": Decimal(k[2]),
        "low": Decimal(k[3]),
        "close": Decimal(k[4]),
        "close_time": int(k[6]),
    }


def get_month_klines(year: int, month: int) -> list[dict]:
    """
    每月最多 744 根 1 小时 K 线，
    使用单次请求获取该月数据。
    """
    start = month_start_ms(year, month)

    next_year, next_m = next_month(year, month)
    end = month_start_ms(next_year, next_m) - 1

    data = api_get(
        "/api/v3/klines",
        {
            "symbol": SYMBOL,
            "interval": INTERVAL,
            "startTime": start,
            "endTime": end,
            "limit": 1000,
        },
    )

    return [parse_kline(k) for k in data]


# =========================
# 月内先后顺序判断
# =========================

def analyze_month(
    year: int,
    month: int,
    previous_close: Decimal | None,
    candles: list[dict],
) -> dict:
    name = month_name(year, month)

    if not candles:
        return {
            "month": name,
            "status": "NO_DATA",
            "reason": "该月没有获取到 K 线",
        }

    monthly_open = candles[0]["open"]

    if previous_close is None:
        return {
            "month": name,
            "status": "UNVERIFIABLE",
            "reason": "没有上月收盘价，无法计算下跌目标",
            "monthly_open": monthly_open,
            "monthly_high": max(c["high"] for c in candles),
            "monthly_low": min(c["low"] for c in candles),
            "monthly_close": candles[-1]["close"],
        }

    # 下跌目标基于上月收盘价
    down_target = previous_close * (Decimal("1") - DROP_PCT)

    # 上涨限制基于本月开盘价
    up_target = monthly_open * (Decimal("1") + RISE_PCT)

    first_event = None
    event_time = None
    event_candle = None
    reason = ""

    for candle in candles:
        o = candle["open"]
        h = candle["high"]
        l = candle["low"]

        # K 线开盘时已经位于目标价的另一侧，
        # 则视为开盘时就已触及该目标。
        down_at_open = o <= down_target
        up_at_open = o >= up_target

        if down_at_open and up_at_open:
            first_event = "AMBIGUOUS"
            event_time = candle["open_time"]
            event_candle = candle
            reason = "同一根 K 线开盘同时满足两个目标"
            break

        if down_at_open:
            first_event = "DOWN_FIRST"
            event_time = candle["open_time"]
            event_candle = candle
            reason = "开盘价已达到下跌目标"
            break

        if up_at_open:
            first_event = "UP_FIRST"
            event_time = candle["open_time"]
            event_candle = candle
            reason = "开盘价已达到上涨限制"
            break

        down_hit = l <= down_target
        up_hit = h >= up_target

        if down_hit and up_hit:
            # OHLC 只知道该小时的最高价、最低价，
            # 不知道哪一个价位先被触及。
            first_event = "AMBIGUOUS"
            event_time = candle["open_time"]
            event_candle = candle
            reason = "同一根 1 小时 K 线同时触及两个目标，顺序无法确认"
            break

        if down_hit:
            first_event = "DOWN_FIRST"
            event_time = candle["open_time"]
            event_candle = candle
            reason = "先触及下跌目标"
            break

        if up_hit:
            first_event = "UP_FIRST"
            event_time = candle["open_time"]
            event_candle = candle
            reason = "先触及上涨限制"
            break

    if first_event == "DOWN_FIRST":
        status = "PASS"
    elif first_event == "UP_FIRST":
        status = "FAIL"
    elif first_event == "AMBIGUOUS":
        status = "AMBIGUOUS"
    else:
        status = "FAIL"
        reason = "整月未触及下跌目标，也未先触及上涨限制"

    monthly_high = max(c["high"] for c in candles)
    monthly_low = min(c["low"] for c in candles)
    monthly_close = candles[-1]["close"]

    drop_pct = (monthly_low - previous_close) / previous_close * 100
    rise_pct = (monthly_high - monthly_open) / monthly_open * 100

    event_time_text = (
        datetime.fromtimestamp(
            event_time / 1000, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC")
        if event_time is not None
        else ""
    )

    return {
        "month": name,
        "status": status,
        "reason": reason,
        "previous_close": previous_close,
        "monthly_open": monthly_open,
        "down_target": down_target,
        "up_target": up_target,
        "monthly_high": monthly_high,
        "monthly_low": monthly_low,
        "monthly_close": monthly_close,
        "max_drop_vs_previous_close_pct": drop_pct,
        "max_rise_vs_month_open_pct": rise_pct,
        "first_event_time_utc": event_time_text,
        "event_candle_open": event_candle["open"] if event_candle else "",
        "event_candle_high": event_candle["high"] if event_candle else "",
        "event_candle_low": event_candle["low"] if event_candle else "",
    }


# =========================
# CSV 输出
# =========================

def decimal_text(value) -> str:
    if value is None or value == "":
        return ""
    if isinstance(value, Decimal):
        return format(
            value.quantize(Decimal("0.01")),
            "f",
        )
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def export_csv(rows: list[dict]):
    if not rows:
        return

    fields = list(dict.fromkeys(
        key for row in rows for key in row.keys()
    ))

    with OUTPUT_CSV.open(
        "w", newline="", encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                key: decimal_text(value)
                for key, value in row.items()
            })


# =========================
# 主程序
# =========================

def main():
    first = get_first_kline()
    first_dt = datetime.fromtimestamp(
        first["open_time"] / 1000,
        tz=timezone.utc,
    )

    now = datetime.now(timezone.utc)

    # 只统计完整自然月；当前月不纳入统计。
    if now.month == 1:
        last_year, last_month = now.year - 1, 12
    else:
        last_year, last_month = now.year, now.month - 1

    print(f"交易对：{SYMBOL}")
    print("数据来源：Binance Spot Kline API")
    print(f"时间周期：{INTERVAL}")
    print(f"最早可查询 K 线：{first_dt:%Y-%m-%d %H:%M UTC}")
    print(f"统计至：{month_name(last_year, last_month)}")
    print("规则：先触及下跌目标算符合；先触及上涨限制算不符合。")
    print("同一小时内两个目标都被触及，列为顺序不确定。")

    rows = []
    previous_close = None
    previous_month_name = None
    gaps = []

    for year, month in month_range(
        first_dt.year,
        first_dt.month,
        last_year,
        last_month,
    ):
        name = month_name(year, month)
        candles = get_month_klines(year, month)

        if not candles:
            gaps.append(name)
            rows.append({
                "month": name,
                "status": "NO_DATA",
                "reason": "月份缺少 K 线数据",
            })
            # 数据缺失后，不再使用上一个已知月收盘价
            # 作为紧邻上月的收盘价。
            previous_close = None
            previous_month_name = name
            time.sleep(0.15)
            continue

        if previous_month_name is not None:
            py, pm = map(int, previous_month_name.split("-"))
            expected_y, expected_m = next_month(py, pm)
            expected = month_name(expected_y, expected_m)

            if name != expected:
                gaps.append(
                    f"{previous_month_name} 后应为 {expected}，实际为 {name}"
                )
                previous_close = None

        row = analyze_month(
            year,
            month,
            previous_close,
            candles,
        )
        rows.append(row)

        # 下一月的基准是本月最后一根小时 K 线的收盘价。
        previous_close = candles[-1]["close"]
        previous_month_name = name

        time.sleep(0.15)

    export_csv(rows)

    pass_rows = [r for r in rows if r["status"] == "PASS"]
    fail_rows = [r for r in rows if r["status"] == "FAIL"]
    ambiguous_rows = [r for r in rows if r["status"] == "AMBIGUOUS"]
    unverifiable_rows = [
        r for r in rows if r["status"] in ("UNVERIFIABLE", "NO_DATA")
    ]

    print("\n" + "=" * 100)
    print("统计汇总")
    print("=" * 100)
    print(f"检查月份总数：{len(rows)}")
    print(f"符合（先跌 1%）：{len(pass_rows)}")
    print(f"不符合（先涨 33% 或未触及下跌目标）：{len(fail_rows)}")
    print(f"顺序不确定：{len(ambiguous_rows)}")
    print(f"无法判断 / 数据缺失：{len(unverifiable_rows)}")

    for title, selected in [
        ("符合月份", pass_rows),
        ("不符合月份", fail_rows),
        ("顺序不确定月份", ambiguous_rows),
        ("无法判断 / 数据缺失月份", unverifiable_rows),
    ]:
        print(f"\n--- {title}（{len(selected)}）---")
        for r in selected:
            print(
                f"{r['month']} | "
                f"状态={r['status']} | "
                f"相对上月收盘最大跌幅="
                f"{decimal_text(r.get('max_drop_vs_previous_close_pct'))}% | "
                f"本月开盘至最高涨幅="
                f"{decimal_text(r.get('max_rise_vs_month_open_pct'))}% | "
                f"事件时间={r.get('first_event_time_utc', '')} | "
                f"{r.get('reason', '')}"
            )

    print("\n月份连续性检查：")
    if gaps:
        for gap in gaps:
            print(f"发现断档或数据缺失：{gap}")
    else:
        print("未发现月份断档。")

    print(f"\nCSV 已输出至：{OUTPUT_CSV.resolve()}")
    print(
        "\n重要：1 小时 K 线内同时触及两个目标时，"
        "不能据 OHLC 断定先后。若要消除这些不确定月份，"
        "应进一步用 1 分钟 K 线复核。"
    )


if __name__ == "__main__":
    main()
