from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import logging
import psycopg2

def get_Redshift_connection():
    host = "learnde.cduaw970ssvt.ap-northeast-2.redshift.amazonaws.com"
    user = "cooltime0608"  
    password = "..."  
    port = 5439
    dbname = "dev"
    conn = psycopg2.connect(f"dbname={dbname} user={user} host={host} password={password} port={port}")
    conn.set_session(autocommit=True)
    return conn.cursor()


def extract(url):
    logging.info("Extract started")
    f = requests.get(url)
    logging.info("Extract done")
    return (f.text)


def transform(text):
    logging.info("transform started")
    # ignore the first line - header
    lines = text.split("\n")[1:]
    logging.info("transform done")
    return lines


def load(lines):
    logging.info("load started")
    cur = get_Redshift_connection()
    sql = "BEGIN;DELETE FROM cooltime0608.name_gender;"
    for l in lines:
        if l != '':
            (name, gender) = l.split(",")
            sql += f"INSERT INTO cooltime0608.name_gender VALUES ('{name}', '{gender}');"
    sql += "END;"
    cur.execute(sql)
    logging.info(sql)
    logging.info("load done")
	
	
'''
def load(lines):
    # BEGIN과 END를 사용해서 SQL 결과를 트랜잭션으로 만들어주는 것이 좋음
    # BEGIN;DELETE FROM (본인의스키마).name_gender;INSERT INTO TABLE VALUES ('Junha', 'MALE');....;END;
    cur = get_Redshift_connection()
    with cur:
      cur.execute("DELETE FROM cooltime0608.name_gender")
      for index, r in enumerate(lines):
          if r != '' and index != 0:
              (name, gender) = r.split(",")
              print(name, "-", gender)
              sql = "INSERT INTO cooltime0608.name_gender VALUES ('{n}', '{g}')".format(n=name, g=gender)
              print(sql)
              cur.execute(sql)
'''

def etl():
    link = "https://s3-geospatial.s3-us-west-2.amazonaws.com/name_gender.csv"
    data = extract(link)
    lines = transform(data)
    load(lines)


dag_second_assignment = DAG(
	dag_id = 'second_assignment',
  catchup = False,
	start_date = datetime(2022,5,12), # 날짜가 미래인 경우 실행이 안됨
	schedule_interval = '0 2 * * *')  # 적당히 조절

task = PythonOperator(
	task_id = 'perform_etl',
	python_callable = etl,
	dag = dag_second_assignment)
