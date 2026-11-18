"""Чисте функціональне ядро для обробки продажів менеджерів (Лабораторна №2, Варіант 3)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from functools import reduce
from itertools import islice
from typing import Any, TypedDict, cast


class ManagerRecord(TypedDict, total=False):
    """Типізована структура запису менеджера з продажу."""

    id: int
    name: str
    region: str
    sales: list[float]
    total_sales: float
    rank: int


PipelineFn = Callable[[Iterable[ManagerRecord]], list[ManagerRecord]]


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Правостороння композиція функцій: compose(f, g)(x) == f(g(x))."""

    def _composed(value: Any) -> Any:
        result: Any = value
        for fn in reversed(funcs):
            result = fn(result)
        return result

    return _composed


def pipe(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Лівосторонній конвеєр функцій: pipe(f, g)(x) == g(f(x))."""

    def _piped(value: Any) -> Any:
        result: Any = value
        for fn in funcs:
            result = fn(result)
        return result

    return _piped


def normalize_names() -> Callable[[Iterable[ManagerRecord]], Iterator[ManagerRecord]]:
    """Чиста трансформація (map + lambda): нормалізує ПІБ менеджера у Title Case."""
    return lambda recs: map(
        lambda r: {**r, "name": str(r.get("name", "")).strip().title()},
        recs,
    )


def with_total_sales() -> Callable[[Iterable[ManagerRecord]], Iterator[ManagerRecord]]:
    """Чиста трансформація (map + lambda): обчислює сумарний обсяг продажів менеджера."""
    return lambda recs: map(
        lambda r: {
            **r,
            "total_sales": round(float(sum(r.get("sales") or [])), 2),
        },
        recs,
    )


def apply_region_factor(
    region: str, factor: float
) -> Callable[[Iterable[ManagerRecord]], Iterator[ManagerRecord]]:
    """Чиста трансформація (map + lambda): застосовує регіональний коефіцієнт."""
    target = region.strip().lower()
    return lambda recs: map(
        lambda r: {
            **r,
            "total_sales": round(
                float(r.get("total_sales", 0.0))
                * (
                    factor
                    if str(r.get("region", "")).strip().lower() == target
                    else 1.0
                ),
                2,
            ),
        },
        recs,
    )


def filter_min_sales(
    min_sales: float,
) -> Callable[[Iterable[ManagerRecord]], Iterator[ManagerRecord]]:
    """Чиста трансформація (filter + lambda): відбирає менеджерів із продажами >= min_sales."""
    return lambda recs: filter(
        lambda r: float(r.get("total_sales", 0.0)) >= min_sales,
        recs,
    )


def sort_by_sales_desc() -> Callable[[Iterable[ManagerRecord]], list[ManagerRecord]]:
    """Чиста трансформація: сортує за спаданням total_sales (тай-брейкер: id зростанням)."""
    return lambda recs: sorted(
        recs,
        key=lambda r: (-float(r.get("total_sales", 0.0)), int(r.get("id", 0))),
    )


def take_top(n: int) -> PipelineFn:
    """Чиста трансформація: відбирає Top-N записів та формує рейтинг (rank 1..N)."""

    def _take(recs: Iterable[ManagerRecord]) -> list[ManagerRecord]:
        top_items = islice(recs, max(0, n))
        return [{**r, "rank": idx} for idx, r in enumerate(top_items, start=1)]

    return _take


def reduce_stats(recs: Iterable[ManagerRecord]) -> dict[str, float]:
    """Агрегація через reduce: обчислює count, revenue та avg_sales."""
    init: dict[str, float] = {"count": 0.0, "revenue": 0.0}
    acc = reduce(
        lambda state, r: {
            "count": state["count"] + 1.0,
            "revenue": round(state["revenue"] + float(r.get("total_sales", 0.0)), 2),
        },
        recs,
        init,
    )
    avg_sales = round(acc["revenue"] / acc["count"], 2) if acc["count"] > 0 else 0.0
    return {
        "count": acc["count"],
        "revenue": acc["revenue"],
        "avg_sales": avg_sales,
    }


def build_pipeline(
    *,
    top_n: int = 3,
    boost_region: str = "Захід",
    factor: float = 1.15,
    min_sales: float = 10000.0,
) -> PipelineFn:
    """Збирає повний функціональний конвеєр обробки продажів через compose."""
    raw_pipeline = compose(
        take_top(top_n),
        sort_by_sales_desc(),
        filter_min_sales(min_sales),
        apply_region_factor(boost_region, factor),
        with_total_sales(),
        normalize_names(),
    )
    return cast(PipelineFn, raw_pipeline)
