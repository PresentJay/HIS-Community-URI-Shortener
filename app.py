from base62 import base62_encode
from datetime import datetime
from flask import Flask, redirect, request
from flask_sqlalchemy import SQLAlchemy
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ['DB_USER'],
    os.environ['DB_PASSWORD'],
    os.environ['DB_HOST'],
    os.environ['DB_PORT'],
    os.environ['DB_NAME']
)
db = SQLAlchemy(app)


class URL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(512), index=True, unique=True)
    shortened_url = db.Column(db.String(6), index=True, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

db.create_all()

@app.route('/shorten', methods=['POST'])
def shorten_url():
    original_url = request.form['url']
    url = URL.query.filter_by(original_url=original_url).first()
    if url:
        return url.shortened_url
    else:
        id = URL.query.count()
        shortened_url = base62_encode(id)
        url = URL(original_url=original_url, shortened_url=shortened_url)
        db.session.add(url)
        db.session.commit()
        return shortened_url

@app.route('/<short_url>')
def redirect_url(short_url):
    url = URL.query.filter_by(shortened_url=short_url).first()
    if url:
        url.updated_at = datetime.utcnow()
        db.session.commit()
        return redirect(url.original_url)
    else:
        return 'URL not found', 404


if __name__ == '__main__':
    app.run()
