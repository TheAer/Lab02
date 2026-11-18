"""Модульні pytest-тести для чистого конвеєра продажів менеджерів (Варіант 3)."""

from __future__ import annotations

from copy import deepcopy

import pytest

from core import (
    ManagerRecord,
    apply_region_factor,
    build_pipeline,
    compose,
    normalize_names,
    pipe,
    reduce_stats,
    with_total_sales,
)


@pytest.fixture
def sample_managers() -> list[ManagerRecord]:
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
    ]


def test_top_n_sorting_and_tie_breaker(sample_managers: list[ManagerRecord]) -> None:
    """Перевіряє коректність Top-N, регіонального коефіцієнта та тай-брейкера за id."""
    pipeline = build_pipeline(
        top_n=3, boost_region="Захід", factor=1.15, min_sales=10000.0
    )
    result = pipeline(sample_managers)

    assert len(result) == 3
    # ID 102 і 105 мають по 16300.0 -> тай-брейкер за id зростанням ставить 102 вище за 105
    assert [m["id"] for m in result] == [102, 105, 104]
    assert [m["rank"] for m in result] == [1, 2, 3]
    assert result[0]["name"] == "Мельник Артем"
    assert result[2]["total_sales"] == 16100.0


def test_no_mutation(sample_managers: list[ManagerRecord]) -> None:
    """Вхідний список і вкладені списки продажів не змінюються після виконання конвеєра."""
    original = deepcopy(sample_managers)
    pipeline = build_pipeline(
        top_n=5, boost_region="Захід", factor=1.2, min_sales=0.0
    )
    ranked = pipeline(sample_managers)

    assert sample_managers == original
    ranked[0]["sales"].append(99999.0)
    assert sample_managers == original


def test_reduce_stats(sample_managers: list[ManagerRecord]) -> None:
    """Перевіряє точність обчислення count, revenue та avg_sales через reduce."""
    pipeline = build_pipeline(
        top_n=3, boost_region="Захід", factor=1.15, min_sales=10000.0
    )
    ranked = pipeline(sample_managers)
    stats = reduce_stats(ranked)

    assert stats["count"] == 3.0
    assert stats["revenue"] == pytest.approx(48700.0)
    assert stats["avg_sales"] == pytest.approx(16233.33)
    assert reduce_stats([]) == {"count": 0.0, "revenue": 0.0, "avg_sales": 0.0}


def test_compose_pipe_and_referential_transparency(
    sample_managers: list[ManagerRecord],
) -> None:
    """Перевіряє еквівалентність compose та pipe і детермінованість обчислень."""
    composed_fn = compose(
        list,
        apply_region_factor("Захід", 1.1),
        with_total_sales(),
        normalize_names(),
    )
    piped_fn = pipe(
        normalize_names(),
        with_total_sales(),
        apply_region_factor("Захід", 1.1),
        list,
    )

    r1 = composed_fn(sample_managers)
    r2 = piped_fn(sample_managers)
    assert r1 == r2
    assert r1[0]["name"] == "Коваленко Олена"
    assert r1[0]["total_sales"] == pytest.approx(14520.0)
