# -*- coding: utf-8 -*-
"""
Pandas 实战教程 —— 用你自己的电商数据学
运行每一段，亲眼看到结果
"""
import pymysql
import pandas as pd

# 连接你的 MySQL
conn = pymysql.connect(host='localhost', port=3306, user='root', password='1234',
                       database='ecommerce_db', charset='utf8mb4')

# ================================================================
# 第1课：读数据 —— pd.read_sql()
# ================================================================
print("=" * 50)
print("第1课：从数据库读取数据")
print("=" * 50)

# 这相当于 SQL 的 SELECT * FROM orders
orders = pd.read_sql("SELECT * FROM orders", conn)
users = pd.read_sql("SELECT * FROM users", conn)
behavior = pd.read_sql("SELECT * FROM user_behavior LIMIT 10000", conn)

# 最常用的3个函数
print("前5行:", orders.head())      # 看一眼数据长什么样
print("\n所有列名:", orders.columns.tolist())
print("\n表结构:", orders.dtypes)    # 每列是什么类型
print("\n行列数:", orders.shape)     # (行数, 列数)

# ================================================================
# 第2课：筛选 —— 相当于 WHERE
# ================================================================
print("\n" + "=" * 50)
print("第2课：数据筛选")
print("=" * 50)

# 筛选已完成的订单
completed = orders[orders['order_status'] == '已完成']
print("已完成订单:", len(completed), "笔")

# 筛选金额大于500的订单
high_value = orders[orders['actual_amount'] > 500]
print("高价值订单(>500):", len(high_value), "笔")

# 多条件筛选（城市=北京 且 金额>300）
beijing_big = orders[(orders['delivery_city'] == '北京') & (orders['actual_amount'] > 300)]
print("北京大额订单:", len(beijing_big), "笔")

# ================================================================
# 第3课：分组聚合 —— 相当于 GROUP BY
# ================================================================
print("\n" + "=" * 50)
print("第3课：分组聚合")
print("=" * 50)

# 每个城市的订单数和GMV
city_stats = orders.groupby('delivery_city').agg(
    订单数=('order_id', 'count'),
    总GMV=('actual_amount', 'sum'),
    客单价=('actual_amount', 'mean')
).sort_values('总GMV', ascending=False)
print("城市销售TOP5:")
print(city_stats.head())

# 每种状态的订单数
status_cnt = orders['order_status'].value_counts()
print("\n订单状态分布:")
print(status_cnt)

# ================================================================
# 第4课：合并表 —— 相当于 JOIN
# ================================================================
print("\n" + "=" * 50)
print("第4课：表合并（JOIN）")
print("=" * 50)

# 订单关联用户信息
order_user = orders.merge(users[['user_id', 'gender', 'city', 'user_level']], on='user_id')
print("合并后:", order_user.shape[1], "列")

# 按性别看消费
gender_stats = order_user.groupby('gender').agg(
    订单数=('order_id', 'count'),
    总消费=('actual_amount', 'sum'),
    客单价=('actual_amount', 'mean')
)
print(gender_stats)

# ================================================================
# 第5课：计算新列 —— 相当于 SELECT ... AS
# ================================================================
print("\n" + "=" * 50)
print("第5课：计算新列")
print("=" * 50)

# 给订单加一列"月份"
orders['月份'] = pd.to_datetime(orders['order_time']).dt.month

# 按月份看GMV
monthly_gmv = orders.groupby('月份')['actual_amount'].sum().sort_index()
print("每月GMV:")
print(monthly_gmv)

# 加一列"折扣率"
orders['折扣率'] = (orders['discount_amount'] / orders['order_amount'] * 100).round(2)
print("\n平均折扣率:", orders['折扣率'].mean().round(2), "%")

# ================================================================
# 第6课：统计分析 —— describe()
# ================================================================
print("\n" + "=" * 50)
print("第6课：统计描述")
print("=" * 50)

# 一行看所有数值列
print(orders[['order_amount', 'discount_amount', 'actual_amount']].describe())

# 分位数
print("\nGMV中位数:", orders['actual_amount'].median())
print("GMV标准差:", orders['actual_amount'].std().round(2))

# 相关性（金额和折扣的关系）
print("\n金额和折扣的相关系数:", orders['order_amount'].corr(orders['discount_amount']).round(4))

# ================================================================
# 第7课：导出结果
# ================================================================
print("\n" + "=" * 50)
print("第7课：导出")
print("=" * 50)

# 导出分析结果到 CSV（Excel 能打开）
city_stats.to_csv(r'D:\电商数据分析项目\城市销售分析.csv', encoding='utf-8-sig')
print("已导出: 城市销售分析.csv")

# 导出到 Excel（多个 sheet）
with pd.ExcelWriter(r'D:\电商数据分析项目\Pandas分析结果.xlsx', engine='openpyxl') as writer:
    city_stats.to_excel(writer, sheet_name='城市分析')
    gender_stats.to_excel(writer, sheet_name='性别分析')

print("已导出: Pandas分析结果.xlsx")
print("\nPandas 实战教程完成！")

conn.close()
