# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 10:55:30 2015

@author: ryan
"""
from flask import render_template, request, make_response
from app import app
import os
import pymysql as mdb
import a_Model
import numpy as np

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
  the_result = a_Model.modelit(city, pop_input)
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
    
    
    #imgurl = "http://127.0.0.1:5000/10/priceplot.png" 
    
    appid= game_id
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = np.array([1,2,3,4,5,6,7,8,9,10])
    graph_response = a_Model.graph_prices(x,y,'stuff')
    return render_template("ssoutput.html", game_info = game_info, appid = appid)

@app.route('/fig/<cropzonekey>')
def fig(cropzonekey):
    fig = draw_polygons(cropzonekey)
    img = StringIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')


@app.route

@app.route("/priceplot.png")
def priceplot():
    '''modified from example at https://gist.github.com/wilsaj/862153'''
    x = np.array([1,2,3,4,5,6,7,8,9,10])
    y = np.array([1,2,3,4,5,6,7,8,9,10])
    response = a_Model.graph_prices(x,y,'stuff')
    return response

@app.route("/<appid>/priceplot.png")
def priceplot2(appid):
    
    with db:
        cur = db.cursor()
        cur.execute("SELECT plot_x FROM Games WHERE Appid = %d;" % int(appid))
        query_results = cur.fetchall()
        p_x = str(query_results[0])
        cur.execute("SELECT plot_y FROM Games WHERE Appid = %d;" % int(appid))
        query_results = cur.fetchall()
        p_y = str(query_results[0])
        print 'reached here'
        x = np.array(eval(eval(p_x[1:-2])))
        y = np.array(eval(eval(p_y[1:-2])))
        print 'and reached here'
        print type(x)
    #x = np.array([1,2,3,4,5,6,7,8,9,10])
    #y = np.array([1,2,3,4,5,6,7,8,9,10])
    response = a_Model.graph_prices(x,y,appid)
    return response