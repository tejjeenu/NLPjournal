import pymongo
from datetime import datetime,timedelta

myclient = pymongo.MongoClient('mongodb+srv://jeenutej:datta001@cluster0.q4rp2wf.mongodb.net/?retryWrites=true&w=majority')

db = myclient["journaldb"]
entries = db["journalentries"]
goals = db["goalquotes"]
gratefulness = db["gratefulquotes"]
learning = db["learningquotes"]

def add(entrytext,gr,le,go):
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

    quotesjsonstring = ""

    pipeline = [
        {"$sample": {"size": 10}},
        {"$sort": {"Date": pymongo.ASCENDING} }
    ]

    #instead replace entries with all 3 of the quote stuff

    for x in goals.aggregate(pipeline):
        #print("for goals")
        #print(str(x['journalID']) + "|" + str(x['quote']))
        quotesjsonstring = quotesjsonstring + str(x['journalID']) + "|" + str(x['quote']) + ",-"
    
    for x in gratefulness.aggregate(pipeline):
        #print("for gratefulness")
        #print(str(x['journalID']) + "|" + str(x['quote']))
        quotesjsonstring = quotesjsonstring + str(x['journalID']) + "|" + str(x['quote']) + ",-"
    
    for x in learning.aggregate(pipeline):
        #print("for learning")
        #print(str(x['journalID']) + "|" + str(x['quote']))
        quotesjsonstring = quotesjsonstring + str(x['journalID']) + "|" + str(x['quote']) + ",-"
    
    return quotesjsonstring[:-2]
    


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
    print("update succesful")

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
    print("delete successful")

deleteentry(3)











    


    


