"""Оболонка побічних ефектів та CLI-інтерфейс для конвеєра продажів (Варіант 3)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from core import ManagerRecord, build_pipeline, reduce_stats


def default_records() -> list[ManagerRecord]:
    """Повертає вбудований набір демонстраційних даних про продажі менеджерів."""
    return [
        {
            "id": 101,
            "name": "  коваленко олена  ",
            "region": "Захід",
            "sales": [4200.0, 5100.0, 3900.0],
        },
        {
            "id": 102,
            "name": "мельник артем",
            "region": "Центр",
            "sales": [6000.0, 5500.0, 4800.0],
        },
        {
            "id": 103,
            "name": "шевченко ірина",
            "region": "Схід",
            "sales": [2100.0, 1900.0, 2500.0],
        },
        {
            "id": 104,
            "name": "бондаренко тарас",
            "region": "Захід",
            "sales": [5000.0, 4800.0, 4200.0],
        },
        {
            "id": 105,
            "name": "ткаченко софія",
            "region": "Південь",
            "sales": [7100.0, 6200.0, 3000.0],
        },
        {
            "id": 106,
            "name": "кравчук дмитро",
            "region": "Захід",
            "sales": [3100.0, 2900.0, 2200.0],
        },
    ]


def load_records(file_path: Path | None) -> list[ManagerRecord]:
    """Побічний ефект: завантажує список менеджерів із JSON-файлу або бере стандартні дані."""
    if file_path is None:
        default_json = Path(__file__).with_name("sample_data.json")
        if default_json.exists():
            file_path = default_json
        else:
            return default_records()

    raw_data = json.loads(file_path.read_text(encoding="utf-8"))
    if not isinstance(raw_data, list):
        raise ValueError("JSON-файл повинен містити список записів менеджерів.")
    return cast(list[ManagerRecord], raw_data)


def render_report(
    ranked: list[ManagerRecord],
    stats: dict[str, float],
    *,
    boost_region: str,
    factor: float,
    min_sales: float,
) -> None:
    """Побічний ефект: виводить сформований рейтинг та агреговану статистику у консоль."""
    print(
        f"=== Рейтинг менеджерів з продажу "
        f"(регіон підсилення: {boost_region} x{factor:.2f}, поріг >= {min_sales:.2f}) ==="
    )
    print("-" * 86)
    for rec in ranked:
        sales_str = ", ".join(f"{val:.0f}" for val in rec.get("sales", []))
        print(
            f"#{rec['rank']} | ID {rec['id']} | {rec['name']:<20} | "
            f"Регіон: {rec['region']:<8} | Угоди: [{sales_str}] | "
            f"Підсумок: {rec['total_sales']:9.2f}"
        )
    print("-" * 86)
    print(
        f"Агрегація (reduce): кількість у рейтингу = {int(stats['count'])} | "
        f"загальна виручка (revenue) = {stats['revenue']:.2f} | "
        f"середні продажі (avg_sales) = {stats['avg_sales']:.2f}"
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Розбір параметрів командного рядка."""
    parser = argparse.ArgumentParser(
        description="Функціональний конвеєр обробки продажів менеджерів (Варіант 3)."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=None,
        help="Шлях до JSON-файлу з вхідними даними (за замовчуванням sample_data.json).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Кількість лідерів у рейтингу Top-N (за замовчуванням 3).",
    )
    parser.add_argument(
        "--boost-region",
        type=str,
        default="Захід",
        help="Регіон, для якого застосовується підвищувальний коефіцієнт (за замовчуванням Захід).",
    )
    parser.add_argument(
        "--factor",
        type=float,
        default=1.15,
        help="Регіональний коефіцієнт підсилення продажів (за замовчуванням 1.15).",
    )
    parser.add_argument(
        "--min-sales",
        type=float,
        default=10000.0,
        help="Мінімальний обсяг продажів для потрапляння в рейтинг (за замовчуванням 10000.0).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    """Головна функція оболонки: зчитування даних, запуск чистого конвеєра та вивід."""
    args = parse_args(argv)
    records = load_records(args.data)

    pipeline = build_pipeline(
        top_n=args.top,
        boost_region=args.boost_region,
        factor=args.factor,
        min_sales=args.min_sales,
    )
    ranked_managers = pipeline(records)
    summary_stats = reduce_stats(ranked_managers)

    render_report(
        ranked_managers,
        summary_stats,
        boost_region=args.boost_region,
        factor=args.factor,
        min_sales=args.min_sales,
    )


if __name__ == "__main__":
    main()
