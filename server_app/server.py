# from sanic import Sanic
# from sanic.response import json
# import sqlite3
# from databases import Database

import flask
from flask import request, render_template, g, session, redirect, url_for, jsonify
from functools import wraps
import sqlite3
from urllib.parse import urlparse


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
  sql_str = 'insert into savedText(url, hostname, title, selected_text) values (?, ?, ?, ?)' 
  g.db.execute(sql_str, (url, hostname, title, selected_text))
  g.db.commit()
  return jsonify({'success': 'success'})

@app.route('/', methods=["GET"])
def home():
  sql_str = 'select * from savedText'
  cur = g.db.execute(sql_str)
  rv = cur.fetchall()
  di = {}
  for val in rv:
    di[val['hostname']] = []

  for val in rv:
    li = di[val['hostname']]  
    # creating text fragment version (note: works only on chrome)
    url = val['url']
    selected_text = val['selected_text']

    first_sentence = selected_text.split('. ')[0]  # obviously not 'bulletproof'; will adjust as errors come about    
    url = url + '#:~:text=' + first_sentence

    li.append({'id': val['id'], 'title': val['title'], 'url': url, 'selected_text': selected_text})
    di[val['hostname']] = li 

  return render_template('home.html', savedText=di)

@app.route('/delete_snippet/<int:post_id>', methods=["GET"])
def delete_snippet(post_id):
  g.db.execute('delete from savedText where id = ?' , (post_id,) )
  g.db.commit()
  return redirect(url_for('home'))



if __name__ == '__main__':
  app.run()


# export FLASK_APP=app.py
# export FLASK_ENV=development
# flask run
# flask run -h localhost -p 8000

# TODO: 
## design of database; # this will constantly change as we build out more features, etc. 

# CREATE TABLE savedText( id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, hostname TEXT, title TEXT, selected_text TEXT);

# CREATE TABLE url( id INTEGER PRIMARY KEY AUTOINCREMENT, url_id INTEGER, title TEXT, url TEXT);
# CREATE TABLE visitDetail( id INTEGER PRIMARY KEY AUTOINCREMENT, url_id INTEGER, visit_id INTEGER, referrer_visit_id INTEGER, visitTime REAL, transition_type TEXT, FOREIGN KEY(url_id) REFERENCES url(url_id) );
# CREATE TABLE bookmark( id INTEGER PRIMARY KEY AUTOINCREMENT, url_id INTEGER, date_added REAL, FOREIGN KEY(url_id) REFERENCES url(url_id));
# CREATE TABLE history(id INTEGER PRIMARY KEY AUTOINCREMENT, url_id INTEGER, last_visit_time INTEGER, visit_count INTEGER, FOREIGN KEY(url_id) REFERENCES url(url_id));

# {'urlID': '7533', 'url': 'https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function', 'title': 'async function - JavaScript | MDN', 'visitcount':
#  2, 'lastVisitedTime': 1617154081598.154, 'visitDetails': [{'id': '7533', 'referringVisitId': '0', 'transition': 'link', 'visitId': '14179', 'visitTime': 1617154080879.8298}, {'id
# ': '7533', 'referringVisitId': '0', 'transition': 'link', 'visitId': '14180', 'visitTime': 1617154081598.154}, {'id': '7533', 'referringVisitId': '0', 'transition': 'link', 'visit
# Id': '14252', 'visitTime': 1617191025961.333}, {'id': '7533', 'referringVisitId': '0', 'transition': 'link', 'visitId': '14253', 'visitTime': 1617191026295.164}]}    

# def check_url_duplicate(url_id):
#   sql_str = 'select exists(select 1 from url where url_id= ? )'
#   cur = g.db.execute(sql_str, (url_id))
#   rv = cur.fetchall()
#   print(rv)

# def save_url(di):
#   url_id = di['urlID']
#   check_url_duplicate(url_id)
#   # url = di['url']
#   # url_title = di['title']
#   # sql_str = 'insert into url (url_id, url, url_title) values (?, ?, ?)' 
#   # g.db.execute(sql_str, (url_id,url,url_title))
#   # g.db.commit()

# @app.route('/save_history', methods=["POST"])
# def save_history(request):
#   print('Hist', request.json)
#   save_url(request.json)
  
#   # url_id = request.json['urlID']
#   # url = request.json['url']
#   # url_title = request.json['title']
#   # visit_count = request.json['visitcount']
#   # last_visited_time = request.json['lastVisitedTime']
#   # visit_details = request.json['visitDetails']
#   return jsonify({'success': 'success'})


