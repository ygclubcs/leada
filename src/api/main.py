# -*- coding: utf-8 -*-
import logging
import os
from bson import json_util
from bson.objectid import ObjectId
import json
from flask import Flask,request
from logging.handlers import TimedRotatingFileHandler
from pymongo import MongoClient
import sys
application = Flask(__name__)
reload(sys) 
sys.setdefaultencoding('utf8') 
mongo_client = MongoClient("mongodb://localhost:27017/",connect=False)

route = application.route
application.debug = True
logger = application.logger

@route('/')
def index():
	return "Hello smart match ..."

def main():
	application.debug = True
	application.run()

if __name__ == "__main__":
	main()
