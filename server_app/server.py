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

from flask import json


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


def create_main_dict(rv):
  di = {}
  for val in rv:
    di[val['hostname']] = []

  li = []
  for val in rv:
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
 
  final_return_dict = {}
  for dict in li:
    hostname = dict['hostname']
    if hostname in final_return_dict:
      old_li = final_return_dict[hostname]
      old_li.append(dict)
      final_return_dict[hostname] = old_li
    else:
      final_return_dict[hostname] = [dict]

  return final_return_dict


@app.route('/', methods=["GET", "POST"])
def home():
  sql_str = 'select * from savedUrl order by created_date desc'
  cur = g.db.execute(sql_str)
  rv = cur.fetchall()
  
  # TODO: abstract this (the common parts in both categories and others)

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
 
  final_other_bookmarks_dict = {}
  for dict in li:
    hostname = dict['hostname']
    if hostname in final_other_bookmarks_dict:
      old_li = final_other_bookmarks_dict[hostname]
      old_li.append(dict)
      final_other_bookmarks_dict[hostname] = old_li
    else:
      final_other_bookmarks_dict[hostname] = [dict]

  sql_str = "select distinct category from savedCategory order by created_date desc" 
  cur = g.db.execute(sql_str)
  categories_rv = cur.fetchall()

  sql_str = "select distinct category from savedCategory order by created_date desc" 
  cur = g.db.execute(sql_str)
  categories_rv = cur.fetchall()

  final_category_di = {}
  for category_row in categories_rv:
    sql_str = 'select * from savedCategory where category=?'
    cur = g.db.execute(sql_str, (category_row['category'],))
    rows = cur.fetchall()

    di = {}
    li = []    
    for row in rows:
      saved_text_id = row['saved_text_id']
      sql_str = 'select * from savedUrl where saved_text_id=?'
      cur = g.db.execute(sql_str, (saved_text_id,))

      url_rows = cur.fetchall()

      for val in url_rows:
        di[val['hostname']] = []

      for val in url_rows:
        url = val['url']
        sql_str = "select saved_text, created_date from savedText where id=? order by created_date desc" 
        cur = g.db.execute(sql_str, (saved_text_id,))
        saved_text_rv = cur.fetchall()
        if len(saved_text_rv) > 0:
          selected_text = saved_text_rv[0][0]
          created_date = saved_text_rv[0][1]
        else:
          selected_text = ''
          created_date = ''
          
        first_sentence = selected_text.split('. ')[0]  # obviously not 'bulletproof'; will adjust as errors come about    
        url = url + '#:~:text=' + first_sentence

        li.append({'id': val['id'], 'hostname': val['hostname'], 'title': val['title'], 'url': url, 'selected_text': selected_text, 'created_date': created_date})

    final_di = {}
    for dict in li:
      hostname = dict['hostname']
      if hostname in final_di:
        old_li = final_di[hostname]
        old_li.append(dict)
        final_di[hostname] = old_li
      else:
        final_di[hostname] = [dict]

    final_category_di[category_row['category']] = final_di 
    
  return render_template('home.html', savedText=final_other_bookmarks_dict, categories=final_category_di)



@app.route('/delete_snippet/<int:post_id>', methods=["GET"])
def delete_snippet(post_id):
  g.db.execute('delete from savedText where id = ?' , (post_id,) )
  g.db.commit()
  return redirect(url_for('home'))


def check_category_duplicate(saved_text_id):
  sql_str = 'select * from savedCategory where saved_text_id=?'
  cur = g.db.execute(sql_str, (saved_text_id,))
  rows = cur.fetchall()
  if len(rows) > 0:
    return True
  return False

@app.route('/add_category', methods=["POST"])
def add_category():
  checkbox_values = request.json['checkbox_values']
  category_selection = request.json['category_selection_str']
  new_category_value = request.json['new_category_value']
  
  if category_selection != '':
    for saved_text_id in checkbox_values:
      duplicate = check_category_duplicate(saved_text_id)
      if not duplicate:
        sql_str = 'insert into savedCategory(category, saved_text_id, created_date) values (?, ?, ?)' 
        created_date = time.time()
        g.db.execute(sql_str, (category_selection, saved_text_id, created_date))
        g.db.commit()

  else:
    for saved_text_id in checkbox_values:
      duplicate = check_category_duplicate(saved_text_id)
      if not duplicate:
        sql_str = 'insert into savedCategory(category, saved_text_id, created_date) values (?, ?, ?)' 
        created_date = time.time()
        g.db.execute(sql_str, (new_category_value, saved_text_id, created_date))
        g.db.commit()

  return jsonify({'success': True})



if __name__ == '__main__':
  app.run()

# export FLASK_APP=server.py
# export FLASK_ENV=development
# flask run -h localhost -p 8000






