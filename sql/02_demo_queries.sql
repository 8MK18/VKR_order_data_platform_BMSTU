SELECT COUNT(*) AS orders_count FROM dwh.fact_order;
SELECT order_status, COUNT(*) FROM dwh.fact_order GROUP BY order_status ORDER BY 2 DESC;
SELECT channel, SUM(total_amount) AS revenue FROM mart.v_order_dashboard GROUP BY channel ORDER BY revenue DESC;
SELECT predicted_status, COUNT(*) FROM mart.order_predictions GROUP BY predicted_status;
SELECT * FROM mart.v_order_dashboard ORDER BY full_date DESC LIMIT 20;
