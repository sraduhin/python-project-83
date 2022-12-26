import datetime
import psycopg2

from config import DATABASE_URL

conn = psycopg2.connect(DATABASE_URL)


def get_id(url):
    query_string = f"SELECT id FROM urls WHERE name = '{url}'"
    cur = conn.cursor()
    cur.execute(query_string)
    result = cur.fetchone()
    conn.commit()
    if result:
        return result[0]


def get_url(id, *args):
    args = '*' if not args else ', '.join(args)
    query_string = f"SELECT {args} FROM urls WHERE id = {id};"
    cur = conn.cursor()
    cur.execute(query_string)
    url = cur.fetchone()
    conn.commit()
    return url


def get_all_urls(*args):
    args = '*' if not args else ', '.join(args)
    query_string = f"SELECT {args} FROM urls;"
    cur = conn.cursor()
    cur.execute(query_string)
    url = cur.fetchall()
    conn.commit()
    return url


def get_checks(page_id):
    query_string = f"SELECT * FROM url_checks WHERE url_id = {page_id};"
    cur = conn.cursor()
    cur.execute(query_string)
    checks = cur.fetchall()
    cur.close()
    conn.commit()
    return checks


def add_url(url):
    cur = conn.cursor()
    insert_string = f"""INSERT INTO urls (name, created_at)
                            VALUES ('{url}',
                            '{datetime.datetime.now()}'
                        );"""
    cur.execute(insert_string)
    cur.close()
    conn.commit()


def add_check(columns, values):
    cur = conn.cursor()
    insert_string = f"""INSERT INTO url_checks
                        ({', '.join(columns)})
                        VALUES
                        ({', '.join(values)});"""
    cur.execute(insert_string)
    cur.close()
    conn.commit()
