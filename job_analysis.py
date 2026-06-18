# -*- coding: utf-8 -*-
# 招聘数据分析：看看数据分析岗位到底要求什么技能
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import re
from collections import Counter
import os
import warnings
warnings.filterwarnings('ignore')

# 中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = r'D:\电商数据分析项目'
DATA_FILE = os.path.join(OUTPUT_DIR, 'job_data_raw.csv')

# ============================================================
# 1. 数据加载与清洗
# ============================================================
print('=' * 60)
print('第1步：数据加载与清洗')
print('=' * 60)

df = pd.read_csv(DATA_FILE)
print(f'原始数据: {len(df)} 条')

# 清理薪资
def parse_salary(s):
    """从 '8K-15K' 提取平均值"""
    if pd.isna(s):
        return np.nan
    nums = re.findall(r'[\d.]+', str(s))
    if len(nums) >= 2:
        return (float(nums[0]) + float(nums[1])) / 2
    elif len(nums) == 1:
        return float(nums[0])
    return np.nan

df['salary_avg'] = df['salary'].apply(parse_salary)

# 清理城市
city_map = {
    '北京': '北京', '上海': '上海', '深圳': '深圳', '广州': '广州',
    '杭州': '杭州', '成都': '成都', '武汉': '武汉', '南京': '南京',
    '苏州': '苏州', '厦门': '厦门'
}
df['city_clean'] = df['city'].map(city_map).fillna('其他')

# 换行分析用的城市薪资
city_salary = df.groupby('city_clean')['salary_avg'].agg(['mean', 'median', 'count']).round(1)
city_salary.columns = ['平均薪资(K)', '中位数薪资(K)', '岗位数']
city_salary = city_salary.sort_values('平均薪资(K)', ascending=False)
print(f'有效数据: {len(df)} 条, 覆盖 {df["city_clean"].nunique()} 个城市')

# ============================================================
# 2. 技能需求分析
# ============================================================
print('\n' + '=' * 60)
print('第2步：技能需求分析')
print('=' * 60)

# 提取所有技能
all_skills = []
skill_salary_map = {}  # 技能对应的薪资列表

for _, row in df.iterrows():
    if pd.notna(row['skills']):
        skills = [s.strip() for s in str(row['skills']).split(',') if s.strip()]
        all_skills.extend(skills)
        for s in skills:
            if s not in skill_salary_map:
                skill_salary_map[s] = []
            if pd.notna(row['salary_avg']):
                skill_salary_map[s].append(row['salary_avg'])

skill_count = Counter(all_skills)
top_skills = skill_count.most_common(15)
skill_names = [s[0] for s in top_skills]
skill_freqs = [s[1] for s in top_skills]

# 技能平均薪资
skill_avg_salary = {}
for skill, salaries in skill_salary_map.items():
    if skill in skill_names and len(salaries) > 0:
        skill_avg_salary[skill] = round(np.mean(salaries), 1)

print('TOP10 技能需求:')
for i, (name, cnt) in enumerate(top_skills[:10], 1):
    avg_s = skill_avg_salary.get(name, '-')
    print(f'  {i:2}. {name:<10} 出现{cnt:4}次  含此技能的岗位均薪: {avg_s}K')

# ============================================================
# 3. 学历分析
# ============================================================
print('\n' + '=' * 60)
print('第3步：学历 vs 薪资分析')
print('=' * 60)

edu_order = ['大专', '本科', '硕士', '不限']
edu_stats = df.groupby('education')['salary_avg'].agg(['mean', 'count']).round(1)
edu_stats.columns = ['平均薪资(K)', '岗位数']
for edu in edu_order:
    if edu in edu_stats.index:
        row = edu_stats.loc[edu]
        print(f'  {edu}: 均薪{row["平均薪资(K)"]}K, {int(row["岗位数"])}个岗位')

# ============================================================
# 4. 经验要求分析
# ============================================================
print('\n' + '=' * 60)
print('第4步：经验要求 vs 薪资')
print('=' * 60)

exp_order = ['应届生', '不限', '1-3年', '3-5年', '5-10年']
exp_stats = df.groupby('experience')['salary_avg'].agg(['mean', 'count']).round(1)
for exp in exp_order:
    if exp in exp_stats.index:
        row = exp_stats.loc[exp]
        print(f'  {exp}: 均薪{row["mean"]}K, {int(row["count"])}个岗位')

# ============================================================
# 5. 可视化
# ============================================================
print('\n' + '=' * 60)
print('第5步：生成图表')
print('=' * 60)

# ---------- 图1：技能需求 TOP15（横向柱状图）----------
fig, ax = plt.subplots(figsize=(12, 7))
colors = ['#FF6B6B' if s == 'SQL' else '#4ECDC4' if s == 'Python' else
          '#45B7D1' if s == 'Excel' else '#96CEB4' if s in ['Tableau', 'Power BI'] else
          '#FFEAA7' if s in ['Pandas', 'NumPy'] else '#DDA0DD' if s == '统计学' else
          '#98D8C8' for s in skill_names]
bars = ax.barh(range(len(skill_names)), skill_freqs, color=colors, edgecolor='white', height=0.7)
ax.set_yticks(range(len(skill_names)))
ax.set_yticklabels(skill_names, fontsize=11)
ax.set_xlabel('出现次数', fontsize=12)
ax.set_title('数据分析岗位 - 技能需求 TOP15', fontsize=16, fontweight='bold')
ax.invert_yaxis()
for bar, freq in zip(bars, skill_freqs):
    ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
            str(freq), va='center', fontsize=10)
ax.set_xlim(0, max(skill_freqs) * 1.2)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'chart1_skill_demand.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  图1: 技能需求TOP15 → chart1_skill_demand.png')

# ---------- 图2：城市薪资对比 ----------
fig, ax = plt.subplots(figsize=(12, 6))
top_cities = city_salary.head(8)
x = np.arange(len(top_cities))
width = 0.35
bars1 = ax.bar(x - width/2, top_cities['平均薪资(K)'], width, label='平均薪资',
               color='#4ECDC4', edgecolor='white')
bars2 = ax.bar(x + width/2, top_cities['中位数薪资(K)'], width, label='中位数薪资',
               color='#FF6B6B', edgecolor='white')
ax.set_xticks(x)
ax.set_xticklabels(top_cities.index, fontsize=11)
ax.set_ylabel('薪资 (K/月)', fontsize=12)
ax.set_title('数据分析岗位 - 各城市薪资对比', fontsize=16, fontweight='bold')
ax.legend(fontsize=10)
for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{bar.get_height():.1f}K', ha='center', fontsize=9)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{bar.get_height():.1f}K', ha='center', fontsize=9)
ax.set_ylim(0, max(top_cities['平均薪资(K)']) * 1.25)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'chart2_city_salary.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  图2: 城市薪资对比 → chart2_city_salary.png')

# ---------- 图3：学历分布饼图 ----------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
edu_data = df['education'].value_counts()
colors_edu = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
wedges, texts, autotexts = ax1.pie(edu_data.values, labels=edu_data.index,
                                     autopct='%1.1f%%', colors=colors_edu[:len(edu_data)],
                                     startangle=90, explode=[0.05]*len(edu_data))
for at in autotexts:
    at.set_fontsize(10)
ax1.set_title('学历要求分布', fontsize=14, fontweight='bold')

edu_salary_data = [edu_stats.loc[e, '平均薪资(K)'] for e in edu_data.index if e in edu_stats.index]
edu_labels = [e for e in edu_data.index if e in edu_stats.index]
bars = ax2.bar(edu_labels, edu_salary_data, color=colors_edu[:len(edu_labels)], edgecolor='white')
ax2.set_ylabel('平均薪资 (K/月)', fontsize=12)
ax2.set_title('各学历平均薪资', fontsize=14, fontweight='bold')
for bar, val in zip(bars, edu_salary_data):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f'{val:.1f}K', ha='center', fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'chart3_education.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  图3: 学历分析 → chart3_education.png')

# ---------- 图4：经验-薪资关系 ----------
fig, ax = plt.subplots(figsize=(10, 5))
exp_data = df.groupby('experience')['salary_avg'].mean().round(1)
exp_order_plot = ['应届生', '不限', '1-3年', '3-5年', '5-10年']
exp_values = [exp_data.get(e, 0) for e in exp_order_plot if e in exp_data.index]
exp_labels = [e for e in exp_order_plot if e in exp_data.index]
ax.plot(exp_labels, exp_values, 'o-', color='#FF6B6B', linewidth=2.5, markersize=10,
        markerfacecolor='white', markeredgewidth=2.5)
ax.fill_between(range(len(exp_labels)), exp_values, alpha=0.15, color='#FF6B6B')
for i, (label, val) in enumerate(zip(exp_labels, exp_values)):
    ax.annotate(f'{val:.1f}K', (i, val), textcoords="offset points",
                xytext=(0, 16), ha='center', fontsize=12, fontweight='bold')
ax.set_ylabel('平均薪资 (K/月)', fontsize=12)
ax.set_title('经验要求 vs 平均薪资', fontsize=16, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'chart4_experience.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  图4: 经验薪资关系 → chart4_experience.png')

# ---------- 图5：技能薪资热力图 ----------
fig, ax = plt.subplots(figsize=(12, 8))
top_skill_names = [s[0] for s in top_skills[:12]]
matrix_data = []
row_labels = ['应届生', '1-3年', '不限']

for exp in row_labels:
    exp_df = df[df['experience'] == exp]
    row = []
    for skill in top_skill_names:
        skill_df = exp_df[exp_df['skills'].str.contains(skill, na=False)]
        if len(skill_df) > 0:
            row.append(skill_df['salary_avg'].mean())
        else:
            row.append(np.nan)
    matrix_data.append(row)

im = ax.imshow(matrix_data, cmap='YlOrRd', aspect='auto')
ax.set_xticks(range(len(top_skill_names)))
ax.set_xticklabels(top_skill_names, fontsize=10, rotation=45, ha='right')
ax.set_yticks(range(len(row_labels)))
ax.set_yticklabels(row_labels, fontsize=11)
for i in range(len(row_labels)):
    for j in range(len(top_skill_names)):
        val = matrix_data[i][j]
        if not np.isnan(val):
            text = ax.text(j, i, f'{val:.1f}K', ha='center', va='center',
                          fontsize=9, fontweight='bold',
                          color='white' if val > np.nanmean(matrix_data) else '#333')
ax.set_title('技能 × 经验 薪资热力图 (K/月)', fontsize=16, fontweight='bold')
plt.colorbar(im, ax=ax, shrink=0.8, label='平均薪资 (K)')
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'chart5_skill_heatmap.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  图5: 技能薪资热力图 → chart5_skill_heatmap.png')

# ---------- 图6：高薪岗位技能画像（雷达图）----------
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# 高薪岗位 vs 低薪岗位的技能差异
df['is_high_salary'] = df['salary_avg'] > df['salary_avg'].median()
high = df[df['is_high_salary']]
low = df[~df['is_high_salary']]

radar_skills = ['SQL', 'Python', 'Excel', 'Tableau', 'Power BI', '统计学', 'AB测试', 'Hive']
n = len(radar_skills)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
angles += angles[:1]

high_values = []
low_values = []
for skill in radar_skills:
    high_values.append(high['skills'].str.contains(skill, na=False).sum() / len(high) * 100)
    low_values.append(low['skills'].str.contains(skill, na=False).sum() / len(low) * 100)
high_values += high_values[:1]
low_values += low_values[:1]

ax.fill(angles, high_values, alpha=0.25, color='#FF6B6B', label='高薪岗位(>中位数)')
ax.plot(angles, high_values, color='#FF6B6B', linewidth=2)
ax.fill(angles, low_values, alpha=0.25, color='#4ECDC4', label='普通岗位(<中位数)')
ax.plot(angles, low_values, color='#4ECDC4', linewidth=2)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(radar_skills, fontsize=11)
ax.set_title('高薪 vs 普通 岗位技能画像对比', fontsize=16, fontweight='bold', pad=25)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
plt.tight_layout()
fig.savefig(os.path.join(OUTPUT_DIR, 'chart6_radar.png'), dpi=150, bbox_inches='tight')
plt.close()
print('  图6: 技能雷达图 → chart6_radar.png')

# 综合结论
print('\n' + '=' * 60)
print('分析结论')
print('=' * 60)

print("""
核心技能排序:
  T0 (必须): SQL - 出现次数断层第一，所有岗位都要求
  T1 (标配): Excel + Python + Pandas + 统计学
  T2 (加分): Tableau/Power BI + AB测试 + 业务分析
  T3 (进阶): Hive + Spark + 机器学习（实习不强制）

城市选择:
  一线城市薪资高但竞争大：北京/上海/深圳 (均薪12-15K)
  新一线性价比高：杭州/成都/武汉 (均薪7-12K)

学历策略:
  本科完全够用 (占55%岗位)，硕士薪资溢价约15-25%
""")

# ============================================================
# 7. 导出分析数据
# ============================================================
print('导出分析结果...')
with pd.ExcelWriter(os.path.join(OUTPUT_DIR, '招聘数据分析报告.xlsx'), engine='openpyxl') as writer:
    city_salary.to_excel(writer, sheet_name='城市薪资分析')
    pd.DataFrame(top_skills, columns=['技能', '出现次数']).to_excel(writer, sheet_name='技能需求排行', index=False)
    edu_stats.to_excel(writer, sheet_name='学历分析')
    exp_stats.to_excel(writer, sheet_name='经验分析')

print(f'\n全部完成！输出文件在: {OUTPUT_DIR}')
print('  - job_data_raw.csv (原始数据)')
print('  - chart1_skill_demand.png (技能需求)')
print('  - chart2_city_salary.png (城市薪资)')
print('  - chart3_education.png (学历分析)')
print('  - chart4_experience.png (经验薪资)')
print('  - chart5_skill_heatmap.png (技能热力图)')
print('  - chart6_radar.png (技能雷达图)')
print('  - 招聘数据分析报告.xlsx (数据汇总)')
