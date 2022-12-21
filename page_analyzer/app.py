import datetime
import logging
import os
import psycopg2
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from validators import url
from urllib.parse import urlparse

from flask import (Flask, render_template, request, flash,
                   get_flashed_messages, redirect, url_for)

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
SECRET_KEY = os.getenv('SECRET_KEY')
conn = psycopg2.connect(DATABASE_URL)
validate = url


app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
def main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls')
def get_urls():
    query_string = "SELECT * FROM urls;"
    cur = conn.cursor()
    cur.execute(query_string)
    urls = cur.fetchall()
    cur.close()
    conn.commit()
    return render_template('urls/urls.html', urls=urls)


@app.post('/')
def get_url():
    data = request.form.to_dict()
    url = data['url']
    url = urlparse(url)
    url = url.scheme + '://' + url.netloc
    logging.info(f"requested url: {url}")

    success = validate(data['url'])
    if not success:
        flash('Некорректный URL', 'alert alert-danger')
        logging.debug(f"incorrect url: {url}")
        return redirect(url_for('main'))

    query_string = f"""SELECT id FROM urls WHERE name = '{url}'"""
    cur = conn.cursor()
    cur.execute(query_string)
    result = cur.fetchone()
    conn.commit()
    if result:
        flash('Страница уже существует', 'alert alert-info')
        logging.info(f"Page already exist: {url}")
        id = result[0]
    else:
        insert_string = f"""INSERT INTO urls (name, created_at)
                            VALUES ('{url}',
                            '{datetime.datetime.now()}'
                        );"""
        cur.execute(insert_string)
        conn.commit()
        cur.execute(query_string)
        id = cur.fetchone()[0]
        cur.close()
        conn.commit()
        flash('Страница успешно добавлена', 'alert alert-info')
        logging.info(f"Success status: {url}")
    return redirect(url_for('show_url', id=id))


@app.route('/urls/<int:id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    cur = conn.cursor()
    query_string = f"SELECT * FROM urls WHERE id = {id};"
    cur.execute(query_string)
    url = cur.fetchone()
    conn.commit()
    if not url:
        logging.error(f"Unknown page id: {id}")
        return render_template('page404.html'), 404
    query_string = f"SELECT * FROM url_checks WHERE url_id = {id};"
    cur.execute(query_string)
    checks = cur.fetchall()
    cur.close()
    conn.commit()
    return render_template(
        'urls/url.html', url=url, checks=checks, messages=messages
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    cur = conn.cursor()
    query_string = f"SELECT name FROM urls WHERE id = {id};"
    cur.execute(query_string)
    url = cur.fetchone()[0]
    conn.commit()
    try:
        r = requests.get(url)
        r.raise_for_status()
    except (requests.RequestException):
        logging.error(f"request error: {url}")
        flash('Произошла ошибка при проверке', 'alert alert-danger')
        return redirect(url_for('show_url', id=id))
    code = r.status_code
    soup = BeautifulSoup(r.text, 'html.parser')
    db_values = {
        'url_id': str(id),
        'status_code': str(code),
        'created_at': f"'{datetime.datetime.now()}'",
    }
    if soup.h1 and soup.h1.get_text():
        db_values['h1'] = f"'{soup.h1.get_text()}'"
    if soup.title and soup.title.get_text():
        db_values['title'] = f"'{soup.title.get_text()}'"
    if soup.meta:
        content = soup.meta.attrs
        if content.get('name') == 'description' and content.get('content'):
            db_values['description'] = f"'{content.get('content')}'"
    insert_string = f"""INSERT INTO url_checks
                        ({', '.join(db_values.keys())})
                        VALUES
                        ({', '.join(db_values.values())});"""
    cur.execute(insert_string)
    cur.close()
    conn.commit()
    flash('Страница успешно проверена', 'alert alert-info')
    return redirect(url_for('show_url', id=id))


@app.errorhandler(404)
def not_found(error):
    logging.error(f'Error: {error}')
    return render_template('page404.html'), 404
