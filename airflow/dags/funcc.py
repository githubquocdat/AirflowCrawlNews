from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import pandas as pd
import os
import psycopg2
from datetime import datetime

def news(ti):
    edge_service = Service('msedgedriver.exe')
    edge_options = Options()

    edge_options.add_argument('--headless')
    edge_options.add_argument('--no-sandbox')
    driver = webdriver.Edge(service=edge_service, options=edge_options)
    list_news = []
    TIMEOUT = 30
    driver.get("https://vnexpress.net/tin-tuc-24h")
    raw_data = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#automation_TV0 > div > article > div > a')))
    for i in raw_data:
        list_news.append(i.get_attribute('href'))
    ti.xcom_push(key='my_link', value=list_news)

def news_news(ti):
    ti.xcom_pull(key='my_link', task_ids='link')