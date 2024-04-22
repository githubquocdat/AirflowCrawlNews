import psycopg2
import csv


def create_table(conn,cur):
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS USERS(
                        id_user SERIAL PRIMARY KEY,
                        hoTen varchar(255),
                        email varchar(255) UNIQUE NOT NULL
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS BIEN_TAP_VIEN(
                        id_btv SERIAL PRIMARY KEY,
                        hoTen varchar(255),
                        email varchar(255) UNIQUE
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS NHA_BAO(
                        id_nb SERIAL PRIMARY KEY,
                        hoTen varchar(255),
                        email varchar(255) UNIQUE
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS CHU_DE(
                        id_cd SERIAL PRIMARY KEY,
                        ten varchar(255)
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS CHUYEN_MUC(
                        id_cm SERIAL PRIMARY KEY,
                        ten varchar(255)
                    )""")    
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS BAI_BAO(
                        id_bb INTEGER PRIMARY KEY,
                        id_cd INTEGER REFERENCES CHU_DE(id_cd),
                        id_cm INTEGER REFERENCES CHUYEN_MUC(id_cm),
                        id_nb INTEGER REFERENCES NHA_BAO(id_nb),
                        id_btv INTEGER REFERENCES BIEN_TAP_VIEN(id_btv)
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS NOI_DUNG(
                        id_nd SERIAL PRIMARY KEY,
                        tieuDe varchar(255),
                        thoiGian timestamp NOT NULL,
                        noiDung text,
                        tomTat text,
                        id_bb INTEGER REFERENCES BAI_BAO(id_bb)                                                 
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS TIN_DA_LUU(
                        id_bb INTEGER REFERENCES BAI_BAO(id_bb),
                        id_user INTEGER REFERENCES USERS(id_user),
                        PRIMARY KEY (id_bb, id_user)
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS TIN_DA_XEM(
                        id_bb INTEGER REFERENCES BAI_BAO(id_bb),
                        id_user INTEGER REFERENCES USERS(id_user),
                        PRIMARY KEY (id_bb, id_user)
                    )""")
    cur.execute("""
                    CREATE TABLE IF NOT EXISTS BINH_LUAN(
                        id_bl SERIAL PRIMARY KEY,
                        id_bb INTEGER REFERENCES BAI_BAO(id_bb),
                        id_user INTEGER REFERENCES USERS(id_user),
                        noiDung TEXT NOT NULL,
                        thoiGian TIMESTAMP NOT NULL,
                        luotThich INTEGER DEFAULT 0,
                        id_bl_cha INTEGER REFERENCES BINH_LUAN(id_bl)
                    )""")    
    conn.commit()

def insert_table(conn,cur,filePath,tableName,columns):
    with open(filePath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  
        for row in reader:
            cur.execute(f"INSERT INTO {tableName} ({','.join(columns)}) VALUES ({','.join(['%s'] * len(columns))})", row)
    conn.commit()


if __name__ == "__main__":
    try:
        conn = psycopg2.connect("host = localhost dbname = news user = airflow password = airflow")
        cur = conn.cursor()
        create_table(conn, cur)
        cur.execute("INSERT INTO bien_tap_vien(id_btv,hoten) values(0,'MASK')")
        conn.commit()
        insert_table(conn,cur,r'D:\emdenthoi\scrape\csv\tac_gia_2024-04-09_moi.csv', 'NHA_BAO',['hoTen'])
        insert_table(conn,cur,r'D:\emdenthoi\scrape\csv\chu_de_2024-04-09_moi.csv', 'CHU_DE',['ten'])
        insert_table(conn,cur,r'D:\emdenthoi\scrape\csv\chuyen_muc_2024-04-09_moi.csv', 'CHUYEN_MUC',['ten'])
        insert_table(conn,cur,r'D:\emdenthoi\scrape\csv\bai_bao_2024-04-12_moi.csv', 'BAI_BAO',['id_bb','id_cd','id_cm','id_nb','id_btv'])
        insert_table(conn,cur,r'D:\emdenthoi\scrape\csv\noi_dung_2024-04-12_moi_1.csv', 'NOI_DUNG',['tieuDe','thoiGian','noiDung','tomTat','id_bb'])

        # cur.close()
        # conn.close()
    except Exception as e:
        print(e)