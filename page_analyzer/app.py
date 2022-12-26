import logging
import os

from dotenv import load_dotenv

from flask import (Flask, render_template, request, flash,
                   get_flashed_messages, redirect, url_for)

from page_analyzer import models
from page_analyzer.utils import get_html_data, parse_and_validate

logging.basicConfig(level=logging.DEBUG)

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')


app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/')
def main():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls')
def get_urls():
    urls = models.get_all_urls()
    return render_template('urls/urls.html', urls=urls)


@app.post('/urls')
def add_url():
    data = request.form.to_dict()
    url, success = parse_and_validate(data)
    logging.info(f"requested url: {url}")

    if not success:
        flash('Некорректный URL', 'alert alert-danger')
        logging.debug(f"incorrect url: {url}")
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'index.html', messages=messages, url=url), 422

    page_id = models.get_id(url)
    if page_id:
        flash('Страница уже существует', 'alert alert-info')
        logging.info(f"Page already exist: {url}")
    else:
        models.add_url(url)
        page_id = models.get_id(url)
        flash('Страница успешно добавлена', 'alert alert-info')
        logging.info(f"Success status: {url}")
    return redirect(url_for('show_url', id=page_id))


@app.route('/urls/<int:id>')
def show_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = models.get_url(id)
    if not url:
        logging.error(f"Unknown page id: {id}")
        return render_template('page404.html'), 404
    checks = models.get_checks(id)
    return render_template(
        'urls/url.html', url=url, checks=checks, messages=messages
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url = models.get_url(id, 'name')[0]
    html_data = get_html_data(url)
    if html_data:
        html_data['url_id'] = str(id)
        models.add_check(html_data.keys(), html_data.values())
        flash('Страница успешно проверена', 'alert alert-info')
        return redirect(url_for('show_url', id=id))
    logging.error(f"request error: {url}")
    flash('Произошла ошибка при проверке', 'alert alert-danger')
    return redirect(url_for('show_url', id=id))


@app.errorhandler(404)
def not_found(error):
    logging.error(f'Error: {error}')
    return render_template('page404.html')
