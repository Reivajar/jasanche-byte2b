"""`main` is the top level module for your Flask application."""

# Data Exploration Byte Version 1
# 
# Copyright 1/2016 Jennifer Mankoff
#
# Licensed under GPL v3 (http://www.gnu.org/licenses/gpl.html)
#

# Imports
import os
import jinja2
import webapp2
import logging
import json
import urllib

# this is used for constructing URLs to google's APIS
from googleapiclient.discovery import build

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# This API key is provided by google as described in the tutorial
API_KEY = 'AIzaSyCuKKwcT5mUYZP_Q-heqCPjvdWyacRuX00'


# This uses discovery to create an object that can talk to the 
# fusion tables API using the developer key
service = build('fusiontables', 'v1', developerKey=API_KEY)

# This is the table id for the fusion table
TABLE_ID = '1QVga82_gzEViomBJui9q4A5SFj9EXDfdEMjSZDsD'

# This is the default columns for the query
query_cols = []

# Import the Flask Framework
from flask import Flask, request
app = Flask(__name__)

def get_all_data(query):
    response = service.query().sql(sql=query).execute()
    logging.info(response['columns'])
    logging.info(response['rows'])
    return response

# make a query given a set of columns to retrieve
def make_query(cols, limit):
    string_cols = ""
    if cols == []:
        cols = ['*']
    for col in cols:
        string_cols = string_cols + ", " + col
    string_cols = string_cols[2:len(string_cols)]

    query = "SELECT " + string_cols + " FROM " + TABLE_ID

    query = query + " LIMIT " + str(limit)

    #logging.info(query)
    # query = "SELECT * FROM " + TABLE_ID + " WHERE  AnimalType = 'DOG' LIMIT 2"

    return query
    
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.

@app.route('/')
def index():
    template = JINJA_ENVIRONMENT.get_template('templates/index.html')
    request = service.column().list(tableId=TABLE_ID)
    allheaders = get_all_data(make_query([], 10))
    logging.info('allheaders')
    return template.render(allheaders=allheaders['columns'], headers=allheaders['columns'], content=allheaders['rows'])

@app.route('/_update_table', methods=['POST']) 
def update_table():
    logging.info(request.get_json())
    cols = request.json['cols']
    logging.info(cols)
    result = get_all_data(make_query(cols, 100))
    logging.info(result)
    return json.dumps({'content' : result['rows'], 'headers' : result['columns']})

@app.route('/about')
def about():
    template = JINJA_ENVIRONMENT.get_template('templates/about.html')
    return template.render()

@app.route('/quality')
def quality():
    template = JINJA_ENVIRONMENT.get_template('templates/quality.html')
    return template.render()

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404

@app.errorhandler(500)
def application_error(e):
    """Return a custom 500 error."""
    return 'Sorry, unexpected error: {}'.format(e), 500
