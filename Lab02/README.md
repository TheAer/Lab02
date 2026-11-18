# Лабораторна робота №2. Функції вищого порядку, lambda, композиція

**Варіант 3:** Продажі менеджерів.

## Опис завдання
Реалізовано функціональний конвеєр обробки записів продажів менеджерів без мутації вхідних даних:
- нормалізація імен (`map` + `lambda`);
- обчислення загального продажу `total_sales` (`map` + `lambda`);
- застосування підвищувального коефіцієнта для заданого регіону;
- фільтрація записів за мінімальним обсягом продажів (`filter` + `lambda`);
- сортування за спаданням продажів (тай-брейкер: `id` зростанням) та відбір `Top-N` з формуванням рейтингу;
- обчислення статистичних показників `count`, `revenue`, `avg_sales` через `functools.reduce`.

## Структура проєкту
- `core.py` — чисті трансформації, композиція (`compose`, `pipe`), збірка конвеєра (`build_pipeline`) та агрегація (`reduce_stats`).
- `app.py` — оболонка вводу-виводу (`load_records`, `render_report`) та CLI-інтерфейс (`argparse`).
- `main.py` — точка входу програми.
- `sample_data.json` — демонстраційний набір вхідних даних.
- `tests/test_core.py` — модульні тести `pytest`.
- `pyproject.toml`, `requirements.txt` — конфігурація середовища, лінтерів та типізації.

## Встановлення та запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Запуск зі стандартними параметрами
python main.py

# Запуск із користувацькими параметрами CLI
python main.py --data sample_data.json --top 3 --boost-region Захід --factor 1.15 --min-sales 10000

# Тести, перевірка типізації та форматування
pytest -v
mypy --strict core.py app.py main.py tests
ruff check .
black --check .
