# !usr/bin/env python3
# encoding:utf-8
"""
@project = bosszhipin
@file = Bosszhipin
@author = 'Easton Liu'
@creat_time = 2018/10/16 19:51
@explain:

"""
import requests
import pymongo
import random
import re
import time
import json
from bs4 import BeautifulSoup


DB="bosszp"
headers = {
        'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.96 Safari/537.36',
    }
def get_urls(root_url,db):
    print(root_url)
    urls = []
    d_url=[]
    res = requests.get(root_url,headers=headers)
    print(res)
    soup = BeautifulSoup(res,'lxml')
    jobs = soup.find_all(class_="job-primary")
    for job in jobs:
        url = job.div.h3.a.attrs['href']
        full_url = 'https://www.zhipin.com'+url
        urls.append(full_url)
    for url in urls:
        if not db.item.find({'url':url}):
            d_url.append(url)
    return d_url
def htmlparser(db,url):
    rec = requests.get(url, headers=headers)
    soup = BeautifulSoup(rec,'lxml')
    jbo_info = soup.find(class_='info-primary')
    public_time = (re.search('(\d+-\d+-\d+)',jbo_info.find(class_='time').text)).group(1)
    jbo_title = jbo_info.find(class_='name').h1.text
    salary = (jbo_info.find(class_='badge').text).strip()
    match_str = re.search('城市\：([\u4E00-\u9FA5]+)经验\：(\d+-\d+[\u4E00-\u9FA5]|\d?[\u4E00-\u9FA5]+)学历\：([\u4E00-\u9FA5]+)',jbo_info.p.text)
    jbo_addr,job_year,holder = match_str.group(1),match_str.group(2),match_str.group(3)
    company_info = soup.find(class_='info-company')
    company_name = company_info.find(class_='name').text
    match_str1 = re.search('([\u4E00-\u9FA5]*|[A-Z]*[\u4E00-\u9FA5]*)(\d+|\d+-\d+)人([\u4E00-\u9FA5]+)',company_info.p.text)
    is_public,company_peoples,company_type = match_str1.group(1),match_str1.group(2),match_str1.group(3).strip('以上')
    jobsec = (soup.find(class_='job-sec').div.text).strip()
    item = {'company_name':company_name,
            'jbo_title':jbo_title,
            'salary':salary,
            'holder':holder,
            'job_year':job_year,
            'address':jbo_addr,
            'public_time':public_time,
            'is_public':is_public,
            'company_peoples':company_peoples,
            'company_type':company_type,
            'jobsec':jobsec,
            'url':url
    }
    db.item.insert(item)



if __name__=='__main__':
    client = pymongo.MongoClient()
    db = client[DB]
    db.item.remove({})
    for i in range(12):
        urls= get_urls(r'https://www.zhipin.com/c101280600/h_101280600/?query=%E8%BD%AF%E4%BB%B6%E6%B5%8B%E8%AF%95&page={}'.format(i+1),db)
        for url in urls:
            htmlparser(db,url)
            time.sleep(10)
