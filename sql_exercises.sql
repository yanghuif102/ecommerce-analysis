USE ecommerce_db;

-- ============================================================
-- 一、GROUP BY 练习（分组聚合）
-- ============================================================

-- 题1：每个城市的订单数和总GMV，按GMV降序排列
SELECT delivery_city AS 城市, COUNT(*) AS 订单数,
       ROUND(SUM(actual_amount), 0) AS GMV
FROM orders WHERE order_status = '已完成'
GROUP BY delivery_city ORDER BY GMV DESC LIMIT 5;

-- 题2：每个类目的平均商品价格
SELECT c.category_name AS 类目,
       ROUND(AVG(p.price), 0) AS 均价,
       MAX(p.price) AS 最高价,
       MIN(p.price) AS 最低价
FROM products p JOIN categories c ON p.category_id = c.category_id
GROUP BY c.category_name;

-- 题3：男女用户的消费对比
SELECT u.gender AS 性别,
       COUNT(DISTINCT o.order_id) AS 订单数,
       ROUND(SUM(o.actual_amount), 0) AS 总消费,
       ROUND(AVG(o.actual_amount), 0) AS 客单价
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.order_status = '已完成'
GROUP BY u.gender;

-- ============================================================
-- 二、JOIN 练习（表关联）
-- ============================================================

-- 题4：查每个订单的用户名和城市（两表 JOIN）
SELECT o.order_id, u.username, u.city, o.actual_amount
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.actual_amount > 500
ORDER BY o.actual_amount DESC LIMIT 10;

-- 题5：查退款订单的详情（三表 JOIN）
SELECT r.refund_id, u.username, p.product_name,
       r.refund_reason, r.refund_amount
FROM refunds r
JOIN users u ON r.user_id = u.user_id
JOIN orders o ON r.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
LIMIT 10;

-- ============================================================
-- 三、子查询练习
-- ============================================================

-- 题6：查出消费金额超过平均值的用户
SELECT u.username, SUM(o.actual_amount) AS 总消费
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.order_status = '已完成'
GROUP BY u.user_id, u.username
HAVING SUM(o.actual_amount) > (
    SELECT AVG(actual_amount) FROM orders WHERE order_status = '已完成'
)
ORDER BY 总消费 DESC LIMIT 10;

-- 题7：查出买过最贵商品的用户
SELECT DISTINCT u.username, u.city
FROM users u
JOIN orders o ON u.user_id = o.user_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE oi.product_id = (
    SELECT product_id FROM products ORDER BY price DESC LIMIT 1
);

-- ============================================================
-- 四、CASE WHEN 练习（条件分类）
-- ============================================================

-- 题8：按订单金额分档
SELECT
    CASE
        WHEN actual_amount < 100 THEN '小额(<100)'
        WHEN actual_amount < 300 THEN '中额(100-300)'
        WHEN actual_amount < 500 THEN '大额(300-500)'
        ELSE '超大额(>500)'
    END AS 金额档位,
    COUNT(*) AS 订单数,
    ROUND(SUM(actual_amount), 0) AS GMV
FROM orders WHERE order_status = '已完成'
GROUP BY 金额档位 ORDER BY MIN(actual_amount);

-- ============================================================
-- 五、综合练习
-- ============================================================

-- 题9：每个城市的高消费用户数（消费>1000元的用户）
SELECT u.city, COUNT(DISTINCT u.user_id) AS 高消费用户数
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status = '已完成'
GROUP BY u.city
HAVING SUM(o.actual_amount) > 0
ORDER BY 高消费用户数 DESC LIMIT 5;

-- 题10：商品复购率（被买超过1次的商品比例）
SELECT
    ROUND(COUNT(DISTINCT CASE WHEN 购买次数 > 1 THEN product_id END) * 100.0
          / COUNT(DISTINCT product_id), 1) AS 复购率
FROM (
    SELECT product_id, COUNT(*) AS 购买次数
    FROM order_items GROUP BY product_id
) t;
