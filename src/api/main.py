# -*- coding: utf-8 -*-
import logging
import os
from bson import json_util
from bson.objectid import ObjectId
import json
from flask import Flask,request
import caiyun.platform.config as cfg
import caiyun.platform.environ as env
from logging.handlers import TimedRotatingFileHandler
from caiyun.platform.wsgi import api
from pymongo import MongoClient
import sys
application = Flask(__name__)
reload(sys) 
sys.setdefaultencoding('utf8') 
mongo_client = MongoClient("mongodb://localhost:27017/",connect=False)
logdir = env.get("log")
if os.path.exists(logdir):
    path = '%s/err-%s.log' % (logdir, cfg.caiyun_env)
    err_handler = TimedRotatingFileHandler(path, when='d', interval=1)
    err_handler.setLevel(logging.INFO)
    err_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    application.logger.addHandler(err_handler)

route = application.route
application.debug = True
logger = application.logger

@route('/')
def index():
	return "Hello smart match ..."

@route('/<int:qid>/<string:content>/<string:choice>/<string:answer>/<int:score>/<int:ismust>/question')
@api
def add_question(qid,content,choice,answer,score,ismust):
		db = mongo_client.match
		topic = db.topic
		topic.insert({"id":qid,"content":content,"choice":choice,"answer":answer,"score":score,"ismust":ismust})
		return {"status":"ok"}

@route('/<string:uid>/<string:name>/regist')
@api
def regist(uid,name):
		db = mongo_client.match
		student = db.student
		response={"status":"ok"}
		std = student.find({"id":uid})
		for x in std:
			return response
		student.insert({"id":uid,"name":name,"credit":100,"islogin":0})
		return response

@route('/<string:uid>/login')
@api
def login(uid):
		db = mongo_client.match
		student = db.student
		std = student.find({"id":uid})
		for x in std:
			student.update({"id":uid},{"$set":{"islogin":1}})
			return {"status":"ok","result":"1"}
		return {"status":"failed","result":"-1"}

@route('/gen_papers')
@api
def gen_papers():
		db = mongo_client.match
		student = db.student
		testpaper = db.testpaper
		testpaper.remove({})
		stds = student.find()
		for x in stds:
			logger.debug(x["id"])
			gen_std_testpaper(x["id"])
		topic = db.topic
		public_topics = topic.find({"ismust":0})
		i = 1
		for y in public_topics:
			testpaper.insert({"index":i,"content":y["content"],"choice":y["choice"],"answer":y["answer"],"score":y["score"],"ismust":y["ismust"],"uid":"public","name":"public","uchoice":"0","scored":-1})
			i+=1
		return {"status":"ok"}

@route('/<string:uid>/<int:index>/<int:ismust>/get_topic')
@api
def get_testpaper_topic(uid,index,ismust):
		db = mongo_client.match
		testpaper = db.testpaper
		student = db.student
		myscore = 0
		std = student.find({"id":uid})
		for s in std:
			myscore = s["credit"]
		result = []
		response = {"status":"ok"}
		total = 0
		papers = None
		index_percent=0
		if ismust == 0:
			uid = "public"
			total = testpaper.find({"ismust":ismust}).count()
			papers = testpaper.find({"index":index,"ismust":ismust})
			index_percent = (float(index)/float(total))*100
		else:
			total = testpaper.find({"uid":uid,"ismust":ismust}).count()
			papers = testpaper.find({"uid":uid,"index":index,"ismust":ismust})
			index_percent = (float(index)/float(total))*100
		for x in papers:
			paper = {"index_percent":index_percent,"last":(total-index),"index":x["index"],"topic_id":str(x["_id"]),"content":x["content"],"answer":x["answer"],"choice":x["choice"],"uname":x["name"],"uchoice":x["uchoice"],"score":x["score"],"scored":x["scored"]}
			jsondoc = json.dumps(paper,default=json_util.default)
			result.append(paper)
		response["result"] = result
		response["myscore"] = myscore
		return response

@route('/<string:uid>/get_paper')
@api
def get_paper(uid):
		db = mongo_client.match
		testpaper = db.testpaper
		response = {"status":"ok"}
		result=[]
		papers = testpaper.find({"uid":uid})
		for x in papers:
			paper = {"index":x["index"],"topic_id":str(x["_id"]),"content":x["content"],"answer":x["answer"],"choice":x["choice"],"uname":x["name"],"uchoice":x["uchoice"],"score":x["score"],"scored":x["scored"]}
			jsondoc = json.dumps(paper,default=json_util.default)
			result.append(paper)
		response["result"]=result
		return response

@route('/<string:topic_id>/<string:uchoice>/<int:scored>/<string:uid>/answer')
@api
def answer_paper(topic_id,uchoice,scored,uid):
		db = mongo_client.match
		testpaper = db.testpaper
		testpaper.update({"_id":ObjectId(topic_id)},{"$set":{"uchoice":uchoice,"scored":scored}})
		student = db.student
		student.update({"id":uid},{"$inc":{"credit":scored}})
		return {"status":"ok"}

@route('/<string:topic_id>/get_answer_result')
@api
def get_answer_res(topic_id):
		db = mongo_client.match
		testpaper = db.testpaper;
		res = testpaper.find({"_id":ObjectId(topic_id)})
		for x in res:
			return {"status":"ok","topic_id":topic_id,"scored":x["scored"],"uchoice":x["uchoice"]}
		return {"status":"fail"}

@route('/<string:topic_id>/<int:index>/<string:uid>/lock_topic')
@api
def lock_topic(topic_id,index,uid):
		db = mongo_client.match
		student = db.student
		testpaper = db.testpaper
		topic = testpaper.find({"_id":ObjectId(topic_id)})
		istopicstart = db.istopicstart
		istopicstart.update({"ismust":0},{"$set":{"index":index,"isstart":2}})
		lock_man = ""
		for x in topic:
			if x["uid"] == "public" or x["uid"] == uid:
				testpaper.update({"_id":ObjectId(topic_id)},{"$set":{"uid":uid,"name":uid}})
				return {"status":"ok"}
			elif uid == "public":
				testpaper.update({"_id":ObjectId(topic_id)},{"$set":{"uid":"public","name":"public"}})
				return {"status":"ok"}
			std = student.find({"id":x["uid"]})
			for y in std:
				lock_man = y["id"]
		return {"status":"failed","result":lock_man}

@route('/get_stdlist')
@api
def get_stdlist():
		db = mongo_client.match
		student = db.student
		stds = student.find().sort("credit",-1)
		results = []
		for x in stds:
			item = {"id":x["id"],"name":x["name"],"credit":x["credit"]}
			jsondoc = json.dumps(item,ensure_ascii=False)
			results.append(jsondoc)
		return {"status":"ok","result":results}

@route('/<int:ismust>/isstart')
@api
def isstart(ismust):
		db = mongo_client.match
		isstart = db.isstart
		res = isstart.find({"is_must":ismust})
		for x in res:
			if x["isstart"] == 1:
				return {"status":"ok"}
		return {"status":"fail"}

@route('/<int:index>/wait_start')
@api
def wait_start(index):
		db = mongo_client.match
		istopicstart = db.istopicstart
		istopicstart.update({"ismust":0},{"$set":{"index":index,"isstart":0}})
		return {"status":"ok"}

@route('/istopicstart')
@api
def istopicstart():
		db = mongo_client.match
		istopicstart = db.istopicstart
		res = istopicstart.find()
		for x in res:
			return {"index":x["index"],"isstart":x["isstart"]}

def gen_std_testpaper(uid):
		db = mongo_client.match
		student = db.student
		topic = db.topic
		testpaper = db.testpaper
		#gen person paper
		std = student.find({"id":uid})
		i = 1
		for x in std:
			topics = topic.find({"ismust":1})
			for y in topics:
				testpaper.insert({"index":i,"content":y["content"],"choice":y["choice"],"answer":y["answer"],"score":y["score"],"ismust":y["ismust"],"uid":uid,"name":x["name"],"uchoice":"0","scored":-1})
				i+=1
def main():
	application.debug = True
	application.run()

if __name__ == "__main__":
	main()
