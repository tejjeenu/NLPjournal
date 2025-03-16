import flask
from flask import request, jsonify, make_response,render_template
import requests

app = flask.Flask(__name__)
app.config["DEBUG"] = True

import random
import json
import torch
from nltk_utils import bag_of_words, tokenize, NeuralNet, keywordlist
import pymongo
from datetime import datetime,timedelta
myclient = pymongo.MongoClient('mongodb+srv://jeenutej:datta001@cluster0.q4rp2wf.mongodb.net/?retryWrites=true&w=majority')

db = myclient["journaldb"]
entries = db["journalentries"]
goals = db["goalquotes"]
gratefulness = db["gratefulquotes"]
learning = db["learningquotes"]

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "testmodel.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

currententry = ""
currentid = ""

def format(topic):
    topic = str(topic)
    for stopval in '"\n':
        topic = topic.replace(stopval,"")
    
    return topic

def predict(topic):
    prediction = ""
    topic = tokenize(topic)
    X = bag_of_words(topic, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()] #this is the predicted tag for the phrase in my case

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.75:
        prediction = tag
    else:
        prediction = "None"
    
    return prediction

def predictindepth(topic):
    returnval = ""
    phrasepredictions = []
    topic = str(topic)
    phrases = topic.split(",")

    for phrase in phrases:
        if(predict(phrase) != "None"):
            phrasepredictions.append(predict(phrase))
    
    if(len(phrasepredictions) == 0):
        returnval = "None"
    else:
        returnval = phrasepredictions[0]
    
    return returnval
     

def add(entrytext, gr, le, go):
  
    global db
    global entries
    global goals
    global gratefulness
    global learning
    currentid = 0
    idval = 0

    entrytext = str(entrytext)
    gr = list(gr)
    le = list(le)
    go = list(go)

    mydoc = entries.find().sort("_id", -1).limit(1)
    for row in mydoc:
        currentid = row['_id']
    
    idval = int(currentid) + 1
    
    post = {"_id":idval,"entry": entrytext,"Date": datetime.now()}
    entries.insert_one(post)

    for quote in gr:
        post = {"journalID": idval, "quote": quote, "Date": datetime.now()}
        gratefulness.insert_one(post)
    
    for quote in le:
        post = {"journalID": idval, "quote": quote, "Date": datetime.now()}
        learning.insert_one(post)
    
    for quote in go:
        post = {"journalID": idval, "quote": quote, "Date": datetime.now()}
        goals.insert_one(post)
    
    print("insert successful")


def getrandomquotes():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    goq = ""
    leq = ""
    grq = ""
    gosection = ""
    grsection = ""
    lesection = ""

    pipeline = [
        {"$sample": {"size": 10}},
        {"$sort": {"Date": pymongo.ASCENDING} }
    ]

    #instead replace entries with all 3 of the quote stuff

    for x in goals.aggregate(pipeline):
        goq = goq + str(x['journalID']) + "|" + str(x['quote']) + ",-"
        keywords = keywordlist(str(x['quote']),2)
        for k in keywords:
            gosection = gosection + k + ","
        gosection = gosection[:-1] + " "
    
    for x in gratefulness.aggregate(pipeline):
        grq = grq + str(x['journalID']) + "|" + str(x['quote']) + ",-"
        keywords = keywordlist(str(x['quote']),2)
        for k in keywords:
            grsection = grsection + k + ","
        grsection = grsection[:-1] + " "
    
    for x in learning.aggregate(pipeline):
        leq = leq + str(x['journalID']) + "|" + str(x['quote']) + ",-"
        keywords = keywordlist(str(x['quote']),2)
        for k in keywords:
            lesection = lesection + k + ","
        lesection = lesection[:-1] + " "
    
    return goq[:-2],grq[:-2],leq[:-2],gosection[:-1],grsection[:-1],lesection[:-1]

def monthly():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    goq = ""
    leq = ""
    grq = ""
    gosection = ""
    grsection = ""
    lesection = ""

    today = datetime.today()
    days_back = today - timedelta(days=30)

    range = {"Date": {"$lt": today, "$gt": days_back}}

    #instead replace entries with all 3 of the quote stuff
    
    for x in goals.find(range):
        goq = goq + str(x['journalID']) + "|" + str(x['quote']) + ",-"
        keywords = keywordlist(str(x['quote']),2)
        for k in keywords:
            gosection = gosection + k + ","
        gosection = gosection[:-1] + " "

    for x in gratefulness.find(range):
        grq = grq + str(x['journalID']) + "|" + str(x['quote']) + ",-"
        keywords = keywordlist(str(x['quote']),2)
        for k in keywords:
            grsection = grsection + k + ","
        grsection = grsection[:-1] + " "

    for x in learning.find(range):
        leq = leq + str(x['journalID']) + "|" + str(x['quote']) + ",-"
        keywords = keywordlist(str(x['quote']),2)
        for k in keywords:
            lesection = lesection + k + ","
        lesection = lesection[:-1] + " "

    return goq[:-2],grq[:-2],leq[:-2],gosection[:-1],grsection[:-1],lesection[:-1]

def getentrynames():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    entryjsonstring = ""

    for x in entries.find():
        #print(str(x['_id']))
        entryjsonstring = entryjsonstring + str(x['_id']) + ","
    
    return entryjsonstring[:-1]
    

def getjournalentry(id):
    id = int(id)
    global db
    global entries
    global goals
    global gratefulness
    global learning

    query = {"_id": id}
    journalentry = ""

    for x in entries.find(query):
        journalentry = str(x['entry']) #this allows id to be associated when deleting and updating on the page
    
    return journalentry

def updateentry(newentry, id):
    id = int(id)
    global db
    global entries
    global goals
    global gratefulness
    global learning

    query = {"_id": id}
    newvalues = { "$set": { "entry": newentry } }

    entries.update_one(query,newvalues)

def deleteentry(id):
    id = int(id)
    global db
    global entries
    global goals
    global gratefulness
    global learning

    query = {"_id": id}
    quotequery = {"journalID":id}

    entries.delete_one(query)
    goals.delete_many(quotequery)
    gratefulness.delete_many(quotequery)
    learning.delete_many(quotequery)


# A route to add a journal entry
@app.route('/add', methods=['GET','OPTIONS'])
def processandadd():
    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        journalentry = str(request.args.get('entry'))

        topics = []
        gr = []
        le = []
        go = []
        paras = journalentry.split("\n\n")

        for p in paras:
           topics.extend(p.split("."))
    #code is for sentences which are likely to have same context


        for topic in topics:
           if(predict(topic) == "None"):
               if(predictindepth(topic) == "gratefulness"):
                  gr.append(topic)
               if(predictindepth(topic) == "goals"):
                  go.append(topic)
               if(predictindepth(topic) == "learning"):
                  le.append(topic)

           if(predict(topic) == "gratefulness"):
                gr.append(topic)
    
           if(predict(topic) == "goals"):
                go.append(topic)
    
           if(predict(topic) == "learning"):
                le.append(topic)
        
        add(journalentry,gr,le,go)

        outputval = {
            "status":"successful"
        }

        return build_actual_response(jsonify(outputval))

@app.route('/random', methods=['GET','OPTIONS'])
def getrandom():
    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        goq,grq,leq,gosection,grsection,lesection = getrandomquotes()

        outputval = {
            "goal quotes":goq,
            "goal keywords":gosection,
            "learning quotes":leq,
            "learning keywords":lesection,
            "grateful quotes":grq,
            "grateful keywords":grsection
        }
          
        return build_actual_response(jsonify(outputval))
        #I want to return the random responses and append them to a string delimited by a comma

@app.route('/monthly', methods=['GET','OPTIONS'])
def getmonthly():
    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        goq,grq,leq,gosection,grsection,lesection = monthly()

        outputval = {
            "goal quotes":goq,
            "goal keywords":gosection,
            "learning quotes":leq,
            "learning keywords":lesection,
            "grateful quotes":grq,
            "grateful keywords":grsection
        }
        
        return build_actual_response(jsonify(outputval))
        #I want to return the random responses and append them to a string delimited by a comma

@app.route('/entrynames', methods=['GET','OPTIONS'])
def getallnames():
    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        journalentrynames = getentrynames()

        outputval = {
            "names":journalentrynames
        }
        
        return build_actual_response(jsonify(outputval))

@app.route('/entryset', methods=['GET','OPTIONS'])
def setentry():
    global currentid
    global currententry

    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        currentid = str(request.args.get('id'))
        currententry = getjournalentry(currentid)
        
        outputval = {
            "status":"entry set successfully"
        }
        
        return build_actual_response(jsonify(outputval))

@app.route('/entryget', methods=['GET','OPTIONS'])
def getentry():
    global currentid
    global currententry

    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        
        outputval = {
            "entry":currententry
        }
        
        return build_actual_response(jsonify(outputval))

@app.route('/entrydelete', methods=['GET','OPTIONS'])
def delentry():
    global currentid
    global currententry

    if request.method == 'OPTIONS': 
        return build_preflight_response()
    elif request.method == 'GET':
        deleteentry(currentid)

        outputval = {
            "status":"deleted successfully"
        }
        
        return build_actual_response(jsonify(outputval))


def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

app.run(host="0.0.0.0")