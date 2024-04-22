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

edge_service = Service('msedgedriver.exe')
edge_options = Options()

edge_options.add_argument('--headless')
edge_options.add_argument('--no-sandbox')
TIMEOUT = 35 #secs
driver = webdriver.Edge(service=edge_service, options=edge_options)

def news():
    driver.get("https://vnexpress.net/tin-tuc-24h")
    # raw_data = WebDriverWait(driver, TIMEOUT).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'article.fck_detail strong')))
    raw_data = driver.find_elements(By.CSS_SELECTOR, '#automation_TV0 > div > article > h3 > a')
    for i in raw_data:
        list_news.append(i.get_attribute('href'))
    return list_news

def crawl_tac_gia(cur,conn,list_news):
    cur.execute("""
                SELECT hoten FROM NHA_BAO 
                """)
    record = cur.fetchall()
    tennb=[list(x) for x in record]
    list_au_new=[]
    for link in list_news:
        driver.get(link)
        try:
            detail_news = driver.find_elements(By.CSS_SELECTOR,"#dark_theme > section.section.page-detail.top-detail > div > div.sidebar-1 > article > p > strong")
            author=detail_news[-1].text
        except:
            list_news.remove(link)  
        if author not in tennb and author not in list_au_new:
            list_au_new.append(author)
            cur.execute(f"insert into nha_bao(hoten) values('{author}')")
            conn.commit()
    return list_news

def crawl_bai_bao():
    cur.execute(" select id_nb, hoten from nha_bao")
    record = cur.fetchall()
    nha_bao=[list(x) for x in record]

    cur.execute(" select id_cd, ten from chu_de")
    record = cur.fetchall()
    chu_de=[list(x) for x in record]

    cur.execute(" select id_cm, ten from chuyen_muc")
    record = cur.fetchall()
    chuyen_muc=[list(x) for x in record]
    
    status_bb = 0
    try:
        cc_news=driver.find_elements(By.CSS_SELECTOR,'ul.breadcrumb li a')
        id_news=driver.find_elements(By.CSS_SELECTOR,'li.myvne_save_for_later')
        detail_news = driver.find_elements(By.CSS_SELECTOR,"article.fck_detail strong")

        id_article_bb = id_news[0].get_attribute('data-article-id')
        for i in range(len(nha_bao)):
            if detail_news[-1].text in nha_bao[i][1] :
                id_author=nha_bao[i][0]
        for i in range(len(chu_de)):
            if cc_news[1].get_attribute('title') in chu_de[i][1] :
                id_cd=chu_de[i][0]
        for i in range(len(chuyen_muc)):
            if cc_news[0].get_attribute('title') in chuyen_muc[i][1] :
                id_cm=chuyen_muc[i][0]
        return status_bb, id_article_bb, id_cd, id_cm, id_author
    except:
        status_bb=1
        return status_bb
    
def crawl_noi_dung():
    status_nn = 0
    try:
        id_news=driver.find_elements(By.CSS_SELECTOR,'li.myvne_save_for_later')
        date_news=driver.find_elements(By.CSS_SELECTOR,'span.date ')
        title_news=driver.find_elements(By.CSS_SELECTOR,'h1.title-detail')
        description_news=driver.find_elements(By.CSS_SELECTOR,'p.description')
        detail =''
        detail_news = driver.find_elements(By.CSS_SELECTOR,'div.sidebar-1 article.fck_detail p.Normal')
        for i in detail_news:
            detail = detail + ' ' + " ".join(i.text.split("\n"))

        id_article_nn = id_news[0].get_attribute('data-article-id')
        description = description_news[0].text
        date = date_news[0].text
        title = title_news[0].text
        detail_all = detail
        return status_nn, title, date, detail_all, description, id_article_nn
    except:
        status_nn=1
        return status_nn
def convert_datetime(datetime_str):
    parts = datetime_str.split(",")
    date_str, time_str = parts[1].strip(), parts[2].strip().split(' ')[0]
    datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
    formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime
def crawl_bai_bao_noi_dung(list_news):
    for link in list_news:  
        driver.get(link)
        id_article_nn='' ;date=''; title='' ;description=''; detail_all = ''
        id_cd=''; id_cm=''; id_nb=''; id_article_bb = ''
        try:
            status_bb, id_article_bb, id_cd, id_cm, id_nb = crawl_bai_bao()
        except:
            status_bb = crawl_bai_bao()

        try:
            status_nn, title, date, detail_all, description, id_article_nn = crawl_noi_dung()
            date=convert_datetime(date)
        except:
            status_nn= crawl_noi_dung()

        if status_nn == 0 and status_bb == 0:
            try:
                cur.execute("insert into bai_bao(id_bb, id_cd, id_cm, id_nb, id_btv) values( %s, %s, %s, %s, 0)", (id_article_bb, id_cd, id_cm, id_nb) )
                cur.execute("insert into noi_dung(tieude, thoigian, noidung, tomtat, id_bb) values(%s, %s, %s, %s, %s)", (title, date, detail_all, description, id_article_nn))
                conn.commit()
            except:
                print(f"{link} : bai bao da co.")
        else:
            print(f"{link} khong hop le")

def transform(conn,cur):
    cur.execute("""DELETE FROM noi_dung
                    WHERE id_nd IN
                        (SELECT id_nd
                        FROM 
                            (SELECT id_nd,
                            ROW_NUMBER() OVER( PARTITION BY tieude,thoigian,noidung,tomtat
                            ORDER BY  id_nd ) AS row_num
                            FROM noi_dung ) t
                            WHERE t.row_num > 1 );""")
    cur.execute("""DELETE FROM nha_bao
                    WHERE id_nb IN
                        (SELECT id_nb
                        FROM 
                            (SELECT id_nb,
                            ROW_NUMBER() OVER( PARTITION BY hoten
                            ORDER BY  id_nb ) AS row_num
                            FROM nha_bao ) t
                            WHERE t.row_num > 1 );""")
    conn.commit()
if __name__ == "__main__":
    try:
        conn = psycopg2.connect("host = localhost dbname = news user = airflow password = airflow")
        cur = conn.cursor()
        list_news=[]
        list_news= news()
        list_news = crawl_tac_gia(cur,conn,list_news)
        # crawl_bai_bao_noi_dung(list_news)
        # transform(conn,cur)
    except Exception as e:
        print(e)
    