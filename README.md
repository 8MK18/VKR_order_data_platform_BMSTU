# ВКР: Интеллектуальная платформа обработки и прогнозирования статуса заказов

Проект выполнен по требованиям ВКР курса «Архитектор данных (Data Architect Pro)».

## Цель
Разработать технический проект единой системы сбора, обработки, хранения и анализа данных о заказах с использованием ETL, DWH и методов машинного обучения.

## Целевая переменная
`order_status` — статус заказа.

## Архитектура
CSV / REST API → Airflow → Staging PostgreSQL → DWH (звезда) → MLflow → Prediction → витрина для BI.

## Компоненты
- PostgreSQL: staging, DWH, mart;
- Apache Airflow: оркестрация;
- MLflow: tracking и регистрация модели;
- Python: ETL, REST-парсер, ML;
- scikit-learn / XGBoost: классификация;
- Docker Compose: воспроизводимый запуск;
- SQL: DDL, загрузка и аналитические представления.

## Быстрый запуск

Требуется Docker Desktop и Docker Compose.

```bash
docker compose up -d --build
```

После запуска:
1. Airflow: http://localhost:8080
2. MLflow: http://localhost:5000
3. PostgreSQL: localhost:5433

Логин Airflow: `admin`, пароль: `admin`.

В Airflow запустить DAG `orders_end_to_end`.

Для локального запуска без Airflow:

```bash
python -m pip install -r requirements.txt
python src/generate_sources.py
python src/web_parser.py
python src/load_staging.py
python src/build_dwh.py
python ml/train.py
python ml/predict.py
```

## Результат
После выполнения создаются:
- `staging.orders_raw`;
- `staging.web_products_raw`;
- `dwh.dim_date`;
- `dwh.dim_customer`;
- `dwh.dim_product`;
- `dwh.dim_channel`;
- `dwh.fact_order`;
- `mart.order_predictions`;
- MLflow experiment `order_status_classification`.

## Структура

```text
vkr_order_data_platform/
├── dags/
├── data/
├── docs/
├── ml/
├── sql/
├── src/
├── tests/
├── config/
├── docker-compose.yml
├── Dockerfile.airflow
├── requirements.txt
└── README.md
```

## Материалы для защиты

- `docs/VKR_presentation_final.pptx` — обновлённая презентация на 16 слайдов;
- `docs/VKR_defense_script.docx` — готовый текст выступления и ответы на вопросы комиссии;
- `docs/PROJECT_DESCRIPTION.md` — описание назначения и результата системы;
- `docs/DEMO_CHECKLIST.md` — пошаговый сценарий демонстрации;
- `docs/RESULTS.md` — результаты локальной проверки и перечень обязательных скриншотов;
- `docs/figures/ERD.png` — ERD по фактической SQL-схеме;
- `docs/screenshots/result_status_distribution.png` — распределение статусов;
- `docs/screenshots/result_revenue_by_channel.png` — аналитический результат по каналам;
- `docs/screenshots/result_confusion_matrix.png` — матрица ошибок локальной ML-проверки.

## Проверка проекта

В текущей среде выполнены синтаксическая проверка Python и автоматические тесты: **9 passed, 1 skipped**. Skip относится к импорту Airflow, поскольку Airflow не установлен вне Docker.

Docker-интеграционный прогон в среде разработки не выполнялся: Docker Engine здесь отсутствует. Версии Docker-образов и библиотек проекта намеренно не изменялись.