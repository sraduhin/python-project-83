import datetime
import logging
import os
import psycopg2

from dotenv import load_dotenv
from validators import url

from flask import Flask, render_template, request, flash, get_flashed_messages, redirect, url_for

logging.basicConfig(encoding='utf-8', level=logging.DEBUG)

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
    return render_template('urls/urls.html', urls=urls)


@app.post('/')
def get_url():
    data = request.form.to_dict()
    url = data['url']
    logging.debug(f"requested url: {url}")

    success = validate(data['url'])
    if success:
        insert_string = f"""INSERT INTO urls (name, created_at)
                            VALUES ('{url}',
                            '{datetime.datetime.now()}'
                        );"""
        query_string = f"""SELECT id FROM urls WHERE name = '{url}'"""
        cur = conn.cursor()
        cur.execute(insert_string)
        conn.commit()
        cur.execute(query_string)
        id = cur.fetchone()[0]
        cur.close()
        flash('Страница успешно добавлена', 'alert alert-info')
        logging.debug(f"success status: {url}")
        return redirect(url_for('show_url', id=id))
        
    flash('Некорректный URL', 'alert alert-danger')
    logging.debug(f"incorrect url: {url}")
    return redirect(url_for('main'))

@app.route('/urls/<int:id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    query_string = f"SELECT * FROM urls WHERE id = {id};"
    cur = conn.cursor()
    cur.execute(query_string)
    url = cur.fetchone()
    cur.close()
    return render_template('urls/url.html', url=url, messages=messages)


if __name__ == '__main__':
    app.run()