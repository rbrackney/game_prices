# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 10:55:30 2015

@author: ryan
"""
from flask import render_template, request
from app import app
import os
import pymysql as mdb
import a_Model


pw_path =  '/home/ryan/credentials/'
with open(os.path.join(pw_path, 'mysql_pw.txt')) as f:
    pw = f.read().strip('\n')
        
#db = mdb.connect(user="root", host="localhost", passwd=pw, db="world", charset='utf8')
db = mdb.connect(user="root", host="localhost", passwd=pw, db="gamepricepred", charset='utf8')
@app.route('/')
@app.route('/index')
def index():    
   user = { 'nickname': 'Miguel' } # fake user, not sure about this
   return render_template("ssgenie.html",
       title = 'Home',
       user = user)


@app.route('/db')
def cities_page():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name FROM City LIMIT 15;")
        query_results = cur.fetchall()
    cities = ""
    for result in query_results:
        cities += result[0]
        cities += "<br>"
    return cities
    
@app.route("/db_fancy")
def cities_page_fancy():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")
        query_results = cur.fetchall()
    cities = []
    for result in query_results:
        cities.append(dict(name=result[0], country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities)
    
@app.route('/input')
def cities_input():
  return render_template("input.html")

@app.route('/ssinput')
def ss_input():
  return render_template("ssinput.html")
  

@app.route('/output')
def cities_output():
  #pull 'ID' from input field and store it
  city = request.args.get('ID')

  with db:
    cur = db.cursor()
    #just select the city from the world_innodb that the user inputs
    cur.execute("SELECT Name, CountryCode,  Population FROM City WHERE Name='%s';" % city)
    query_results = cur.fetchall()

  cities = []
  for result in query_results:
    cities.append(dict(name=result[0], country=result[1], population=result[2]))
  the_result = ''
  #return render_template("output.html", cities = cities, the_result = the_result)
  
  #call a function from a_Model package. note we are only pulling one result in the query
  pop_input = cities[0]['population']   
  the_result = a_Model.ModelIt(city, pop_input)
  return render_template("output.html", cities = cities, the_result = the_result)
  
@app.route('/ssoutput')
def ss_output():
    game_id =  request.args.get('ID')
    
    with db:
        cur = db.cursor()
        #add try/except statements
        cur.execute("SELECT SteamDBTimestamp FROM Games WHERE Appid = %d;" % int(game_id))
        query_results = cur.fetchall()
        
    game_info = str(query_results[0]) #just return the first option
    return render_template("ssoutput.html", game_info = game_info)
    