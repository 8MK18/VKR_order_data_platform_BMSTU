# Результаты и материалы для защиты

## Данные
- 2 000 синтетических заказов в `data/raw/orders.csv`.
- 50 товаров в `data/web/products.json`.
- Целевая переменная: `order_status`.
- Классы: `completed`, `cancelled`, `delayed`.

## Локальная воспроизводимая проверка ML
Проверка модели на исходных данных без PostgreSQL/MLflow выполнена отдельно, чтобы проверить саму ML-логику в среде анализа.

- train: 1 600 строк;
- test: 400 строк;
- Accuracy: 0.8925;
- F1 weighted: 0.8631.

Эти числа получены в среде проверки проекта и могут отличаться от результата запуска Docker-стенда при другой версии scikit-learn. Для защиты следует показывать метрики из вашего фактического запуска Docker/MLflow.

## Что обязательно сфотографировать после запуска Docker
1. Airflow: успешный DAG `orders_end_to_end`.
2. Airflow: Graph/Tree View с зелёными задачами.
3. MLflow: experiment `order_status_classification` и run с Accuracy/F1.
4. PostgreSQL: `SELECT COUNT(*) FROM dwh.fact_order;`.
5. PostgreSQL: `SELECT * FROM mart.v_order_dashboard LIMIT 10;`.
6. PostgreSQL: `SELECT * FROM mart.order_predictions LIMIT 10;`.
7. При возможности — DWH таблицы и ERD.

## Важно
Скриншоты, подтверждающие успешный Docker-запуск, не подменяются синтетическими изображениями. В презентации для них предусмотрены отдельные поля-заглушки.
