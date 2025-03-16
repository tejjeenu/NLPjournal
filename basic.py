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
    
    print("insert succesful")


def querydata():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    for row in entries.find():
        print(row)

def getrandomquotes():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    pipeline = [
        {"$sample": {"size": 10}},
        {"$sort": {"Date": pymongo.ASCENDING} }
    ]

    #instead replace entries with all 3 of the quote stuff

    for x in goals.aggregate(pipeline):
        print("for goals")
        print(str(x['journalID']) + "|" + str(x['quote']))
    
    for x in gratefulness.aggregate(pipeline):
        print("for gratefulness")
        print(str(x['journalID']) + "|" + str(x['quote']))
    
    for x in learning.aggregate(pipeline):
        print("for learning")
        print(str(x['journalID']) + "|" + str(x['quote']))

def monthly():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    today = datetime.today()
    days_back = today - timedelta(days=30)

    range = {"Date": {"$lt": today, "$gt": days_back}}

    #instead replace entries with all 3 of the quote stuff
    
    for x in goals.find(range):
        print("for goals")
        print(str(x['journalID']) + "|" + str(x['quote']))
    
    for x in gratefulness.find(range):
        print("for gratefulness")
        print(str(x['journalID']) + "|" + str(x['quote']))
    
    for x in learning.find(range):
        print("for learning")
        print(str(x['journalID']) + "|" + str(x['quote']))

def getentrynames():
    global db
    global entries
    global goals
    global gratefulness
    global learning

    for x in entries.find():
        print(str(x['_id']))
    

def getjournalentry(id):
    id = int(id)
    global db
    global entries
    global goals
    global gratefulness
    global learning

    query = {"_id": id}

    for x in entries.find(query):
        print(str(x['_id']) + "|" + str(x['entry'])) #this allows id to be associated when deleting and updating on the page

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
    entries.delete_one(query)


journalentry = input("Please could you give an example Journal entry to Break down and analyse: ")

topics = []
gr = []
le = []
go = []
pointer = 0
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

#print("Your gratefulness quotes are " + str(gr))
#print(" ")
#print("Your goals quotes are " + str(go))
#print(" ")
#print("Your learning quotes are " + str(le))
#print(" ")
#print("All your topics are" + str(topics))

print(keywordlist(journalentry))





