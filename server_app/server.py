# from sanic import Sanic
# from sanic.response import json
# import sqlite3
# from databases import Database

import flask
from flask import request, render_template, g, session, redirect, url_for, jsonify
from functools import wraps
import sqlite3
from urllib.parse import urlparse
import time


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["DATABASE"] = '/Users/rahul/Desktop/primary/nlp_projects/project_a/main.db'
# SECRET_KEY = open("secret_key.txt", 'r').read()
# app.secret_key = SECRET_KEY


def connect_db():
  sqlite_db = sqlite3.connect(app.config["DATABASE"])
  sqlite_db.row_factory = sqlite3.Row # to return dicts rather than tuples
  return sqlite_db

@app.before_request
def before_request():
  g.db = connect_db()
  
@app.teardown_request
def teardown_request(exception):
  db = getattr(g, 'db', None)
  if db is not None:
    db.close()

def format_posts(posts):
  rv = []
  for post in posts:
    title, date = post['title'], post['created']
    formatted_date = date.split(' ')[0]
    rv.append({'id': post['id'], 'title': title, 'created': formatted_date, 'body': post['body']})
  return rv


@app.route('/save_text', methods=["POST"])
def save_text():
  print('Data', request.json)
  url = request.json['tabURL']
  hostname = urlparse(url).netloc  # save because we will use hostname as titles with the saved text underneath;
  title = request.json['tabTitle']
  selected_text = request.json['selectedText']
  created_date = time.time()
  sql_str = 'insert into savedText(url, hostname, title, selected_text, created_date) values (?, ?, ?, ?, ?)' 
  g.db.execute(sql_str, (url, hostname, title, selected_text, created_date))
  g.db.commit()
  return jsonify({'success': 'success'})


@app.route('/', methods=["GET", "POST"])
def home():
  sql_str = 'select * from savedUrl order by created_date desc'
  cur = g.db.execute(sql_str)
  rv = cur.fetchall()
  
  di = {}
  for val in rv:
    di[val['hostname']] = []

  li = []
  for val in rv:
    # li = di[val['hostname']]  
    # creating text fragment version (note: works only on chrome)
    url = val['url']

    saved_text_id = val['saved_text_id']
    sql_str = "select saved_text, created_date from savedText where id=? order by created_date desc" 
    cur = g.db.execute(sql_str, (saved_text_id,))
    rv = cur.fetchall()
    if len(rv) > 0:
      selected_text = rv[0][0]
      created_date = rv[0][1]
    else:
      selected_text = ''
      created_date = ''
      
    first_sentence = selected_text.split('. ')[0]  # obviously not 'bulletproof'; will adjust as errors come about    
    url = url + '#:~:text=' + first_sentence

    li.append({'id': val['id'], 'hostname': val['hostname'], 'title': val['title'], 'url': url, 'selected_text': selected_text, 'created_date': created_date})
 
  # li = sorted(li, key=lambda k: k['created_date'], reverse=True)
  final_di = {}
  for dict in li:
    hostname = dict['hostname']
    if hostname in final_di:
      old_li = final_di[hostname]
      old_li.append(dict)
      final_di[hostname] = old_li
    else:
      final_di[hostname] = [dict]

  return render_template('home.html', savedText=final_di)

@app.route('/delete_snippet/<int:post_id>', methods=["GET"])
def delete_snippet(post_id):
  g.db.execute('delete from savedText where id = ?' , (post_id,) )
  g.db.commit()
  return redirect(url_for('home'))




if __name__ == '__main__':
  app.run()

# export FLASK_APP=server.py
# export FLASK_ENV=development
# flask run -h localhost -p 8000


# TODO:
  # Add a category form 
    # create new category or choose from existing to add this snippet into
  # def create_category






