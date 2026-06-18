# -*- coding: utf-8 -*-
import requests
import json
import time
import random
import re
import os
import csv
from datetime import datetime

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

OUTPUT_DIR = r'D:\电商数据分析项目'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'job_data_raw.csv')

# ============================================================
# 方案1: Boss直聘搜索页爬取
# ============================================================
def crawl_boss(keyword='数据分析', pages=5):
    """爬取Boss直聘"""
    jobs = []
    session = requests.Session()
    session.headers.update(HEADERS)

    for page in range(1, pages + 1):
        url = f'https://www.zhipin.com/wapi/zpgeek/search/joblist.json'
        params = {
            'query': keyword,
            'page': page,
            'pageSize': 30,
            'city': '100010000',  # 全国
            'experience': '108',   # 应届生/实习
        }
        try:
            resp = session.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('zpData'):
                    for item in data['zpData'].get('jobList', []):
                        jobs.append({
                            'title': item.get('jobName', ''),
                            'company': item.get('brandName', ''),
                            'city': item.get('cityName', ''),
                            'salary': item.get('salaryDesc', ''),
                            'experience': item.get('jobExperience', ''),
                            'education': item.get('jobDegree', ''),
                            'skills': ','.join(item.get('skills', [])),
                            'source': 'Boss直聘'
                        })
                    print(f'  Boss直聘第{page}页: 获取{len(data["zpData"].get("jobList",[]))}条')
                else:
                    print(f'  Boss直聘第{page}页: 数据格式异常 - {str(data)[:100]}')
            else:
                print(f'  Boss直聘第{page}页: HTTP {resp.status_code}')
        except Exception as e:
            print(f'  Boss直聘第{page}页: 错误 - {e}')

        time.sleep(random.uniform(3, 6))

    return jobs


# ============================================================
# 方案2: 拉勾网搜索
# ============================================================
def crawl_lagou(keyword='数据分析', pages=3):
    """爬取拉勾网"""
    jobs = []
    session = requests.Session()
    session.headers.update(HEADERS)

    # 先获取cookie
    try:
        session.get('https://www.lagou.com/', timeout=10)
    except:
        pass

    for page in range(1, pages + 1):
        url = 'https://www.lagou.com/jobs/v2/positionAjax.json'
        params = {
            'needAddtionalResult': 'false',
            'first': 'true',
            'pn': str(page),
            'kd': keyword,
        }
        form_data = {
            'first': 'true',
            'pn': str(page),
            'kd': keyword,
        }
        try:
            referer = f'https://www.lagou.com/jobs/list_{keyword}?px=default&city=全国'
            session.headers['Referer'] = referer
            resp = session.post(url, data=form_data, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('content') and data['content'].get('positionResult'):
                    result = data['content']['positionResult']['result']
                    for item in result:
                        jobs.append({
                            'title': item.get('positionName', ''),
                            'company': item.get('companyFullName', ''),
                            'city': item.get('city', ''),
                            'salary': item.get('salary', ''),
                            'experience': item.get('workYear', ''),
                            'education': item.get('education', ''),
                            'skills': ','.join(item.get('skillLables', [])),
                            'source': '拉勾'
                        })
                    print(f'  拉勾第{page}页: 获取{len(result)}条')
                else:
                    print(f'  拉勾第{page}页: 需登录或无数据')
            else:
                print(f'  拉勾第{page}页: HTTP {resp.status_code}')
        except Exception as e:
            print(f'  拉勾第{page}页: 错误 - {e}')

        time.sleep(random.uniform(3, 5))

    return jobs


# ============================================================
# 方案3: 生成仿真实数据 (爬虫失效时的后备方案)
# ============================================================
def generate_realistic_data(n=300):
    """基于真实市场行情生成仿真数据"""
    print('\n  爬虫获取数据较少，补充仿真数据...')

    import numpy as np

    np.random.seed(42)

    cities_pool = (
        ['北京'] * 25 + ['上海'] * 22 + ['深圳'] * 18 + ['广州'] * 12 +
        ['杭州'] * 8 + ['成都'] * 5 + ['武汉'] * 3 + ['南京'] * 3 +
        ['苏州'] * 2 + ['厦门'] * 2
    )

    salary_map = {
        '北京': (8, 25), '上海': (7, 24), '深圳': (7, 22), '广州': (5, 18),
        '杭州': (6, 20), '成都': (4, 14), '武汉': (3, 12), '南京': (5, 16),
        '苏州': (4, 15), '厦门': (3, 12)
    }

    titles = (
        ['数据分析师'] * 30 + ['数据分析实习生'] * 25 + ['BI数据分析师'] * 10 +
        ['商业数据分析'] * 8 + ['数据运营'] * 8 + ['电商数据分析'] * 6 +
        ['数据分析专员'] * 5 + ['BI工程师'] * 3 + ['数据产品经理'] * 3 +
        ['大数据分析师'] * 2
    )

    education_pool = ['本科'] * 55 + ['大专'] * 25 + ['硕士'] * 15 + ['不限'] * 5

    skills_pool = [
        'SQL', 'Python', 'Excel', 'Tableau', 'Power BI',
        'Pandas', 'NumPy', 'Matplotlib', 'SPSS', 'R语言',
        'Hive', 'Spark', 'Flink', '统计学', 'AB测试',
        '数据仓库', 'ETL', '数据可视化', '机器学习', '业务分析'
    ]

    all_skills_combo = {
        '基础组': ['SQL', 'Excel', 'Python', 'Pandas', '统计学'],
        '进阶组': ['SQL', 'Python', 'Tableau', 'Power BI', 'AB测试', 'Hive'],
        '全栈组': ['SQL', 'Python', 'Spark', 'Hive', '机器学习', 'ETL', '数据仓库'],
        '业务组': ['SQL', 'Excel', '业务分析', 'AB测试', 'Tableau'],
    }

    data = []
    for _ in range(n):
        city = np.random.choice(cities_pool).item()
        min_s, max_s = salary_map.get(city, (4, 15))
        salary_low = round(np.random.uniform(min_s, max_s - 3), 1)
        salary_high = round(salary_low + np.random.uniform(3, 10), 1)

        # 70% 概率用基础技能组
        combo_key = np.random.choice(['基础组', '基础组', '基础组', '进阶组', '业务组'])
        skill_count = np.random.randint(3, 8)
        skills = list(np.random.choice(all_skills_combo[combo_key],
                                        size=min(skill_count, len(all_skills_combo[combo_key])),
                                        replace=False))

        data.append({
            'title': np.random.choice(titles).item(),
            'company': f"{np.random.choice(['字节跳动', '阿里', '腾讯', '美团', '京东', '网易', '快手', '小红书', '得物', '拼多多', 'SHEIN', '某跨境电商', '某科技', '某金融', '某教育'])}{np.random.choice(['科技', '信息技术', '网络', '数据', ''])}有限公司" if np.random.random() < 0.3 else f"{np.random.choice(['华', '明', '锐', '创', '汇', '星', '智', '远', '云', '博'])}{np.random.choice(['为', '源', '思', '达', '通', '联', '科', '数', '析', '睿'])}{np.random.choice(['科技', '数据', '信息', '咨询', ''])}有限公司",
            'city': city,
            'salary': f'{salary_low}K-{salary_high}K',
            'salary_avg_k': round((salary_low + salary_high) / 2, 1),
            'experience': np.random.choice(['应届生', '1-3年', '1-3年', '不限', '3-5年']),
            'education': np.random.choice(education_pool).item(),
            'skills': ','.join(skills),
            'source': '仿真数据(基于真实行情)'
        })

    return data


# ============================================================
# 主流程
# ============================================================
def main():
    print('=' * 60)
    print('招聘数据分析岗位 - 数据采集')
    print(f'采集时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    print('=' * 60)

    all_jobs = []

    # 尝试1: Boss直聘
    print('\n[1/2] 尝试爬取 Boss直聘...')
    boss_jobs = crawl_boss('数据分析', pages=3)
    all_jobs.extend(boss_jobs)
    print(f'  Boss直聘合计: {len(boss_jobs)} 条')

    # 尝试2: 拉勾
    print('\n[2/2] 尝试爬取 拉勾...')
    lagou_jobs = crawl_lagou('数据分析', pages=2)
    all_jobs.extend(lagou_jobs)
    print(f'  拉勾合计: {len(lagou_jobs)} 条')

    # 如果爬虫数据不够，补充仿真数据
    crawed = len(all_jobs)
    if crawed < 100:
        simulated = generate_realistic_data(300 - crawed)
        all_jobs.extend(simulated)

    # 保存
    print(f'\n共采集 {len(all_jobs)} 条数据')

    keys = ['title', 'company', 'city', 'salary', 'experience', 'education', 'skills', 'source']
    with open(OUTPUT_FILE, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys + ['salary_avg_k'], extrasaction='ignore')
        writer.writeheader()
        for job in all_jobs:
            writer.writerow({k: job.get(k, '') for k in keys + ['salary_avg_k']})

    print(f'已保存: {OUTPUT_FILE}')
    print(f'\n数据来源分布:')
    from collections import Counter
    sources = Counter(j.get('source', '未知') for j in all_jobs)
    for s, c in sources.items():
        print(f'  {s}: {c} 条')


if __name__ == '__main__':
    main()
