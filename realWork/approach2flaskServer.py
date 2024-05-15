from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from urllib.parse import quote_plus
from datetime import datetime
import os
from dotenv import load_dotenv
from serverUtility import *
load_dotenv()


app = Flask(__name__)

# setting up mongo db datsbase

username = quote_plus(str(os.environ['MONGO_CLUSTER_USERNAME']))
pasword = quote_plus(str(os.environ['MONGO_CLUSTER_PASWORD']))
mongoURI = os.environ['MONGO_CONNECTION_STRING']
# creating the database name as pdf by joining it with connection string
app.config["MONGO_URI"] = mongoURI.format(
    username=username, pasword=pasword) + "/pdf"
db = PyMongo(app).db


# setting up secret key
app.secret_key = os.environ['APP_SECRET_KEY']


# langsmith Tracking (Important for getting insights of gen-ai application)
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")


# setting up global variable for flask app
class Chain:
    def __init__(self):
        self.vectorStore = None
        self.retrievalChain = None
        self.status = None
        self.sessionId = 'Default'
        self.userId = 'Default'
        self.userChatHistory = []


chain = Chain()
app.config['chain'] = chain
app.config['STATIC_URL'] = '/static'  # URL prefix for static files
app.config['STATIC_FOLDER'] = 'D:\\test_locally_notebooks\\PDF-Insight\\realWork\\static'


@ app.route('/', methods=['GET'])
def uiFile():
    return redirect(url_for('starterUi'))


@ app.route('/starterUi', methods=['GET'])
def starterUi():
    return render_template('starter.html')
    # return render_template('starter.html')


@ app.route('/authUi', methods=['GET'])
def authUi():
    return render_template('auth.html')


@ app.route('/uploadUi', methods=['GET'])
def uploadUi():
    return render_template('upload.html')


@ app.route('/sessionDataUi', methods=['GET'])
def sessionDataUi():
    return render_template('sessionData.html')


@ app.route('/chatUi', methods=['GET'])
def chatUi():
    return render_template('chat.html')


@ app.route('/reDirect/<endPoint>', methods=['GET'])
def reDirect(endPoint):
    return redirect(url_for(endPoint))


@ app.route('/signIn', methods=['POST'])
def signIn():
    if request.method == 'POST':
        try:
            euserId = request.form['euserId']
            print(f'euserId is {euserId}')

            userId = suitableId(userId=euserId)
            print(f'userId is {userId}')
            document = db.get_collection(
                "user info").find_one({'userId': userId})
            print(f'these is the document {document}')
            if (document == None):
                return jsonify({'sucess': 0, 'message': 'Incorrect userId'})
            else:
                chain.userId = userId
                return jsonify({'sucess': 1, 'message': 'correct userId'})
        except:
            return jsonify({'sucess': 0, 'message': 'Incorrect userId'})


@ app.route('/signUp', methods=['POST'])
def signUp():
    if request.method == 'POST':
        try:
            userName = request.form['userName']
            nuserId = request.form['nuserId']
            userId = suitableId(userId=nuserId)
            chain.userId = userId
            db.get_collection("user info").insert_one(
                {'userName': userName, 'userId': userId})
            return jsonify({'sucess': 1, 'message': 'userId created'})
        except:
            return jsonify({'sucess': 0, 'message': 'error occured'})


@app.route('/status', methods=['POST'])
def status():

    status = request.form['status']
    chain.status = status
    return jsonify({'message': 'status saved'})

    # files upload handling


@ app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        try:
            userId = app.config['chain'].userId
            sessionId = app.config['chain'].sessionId
            status = app.config['chain'].status
            print(f'userId in the upload is {userId}')

            pdfFiles = request.files.getlist('pdfFiles')
            print(f'pdfFiles: {pdfFiles}')
            if (status == 'n'):
                docsChunks, sessionId = getTextChunks(pdfFiles=pdfFiles)
            if (status == 'e'):
                docsChunks, sessionId = getTextChunks(pdfFiles=pdfFiles, getId=False,
                                                      alreadyHaveId=sessionId)
            # vectorStore = getVectorStore(docsChunks=docsChunks)
            vectorStore = getAstraVectorStore(
                docsChunks=docsChunks, collectionName=userId, add=True)

            # conversationChain = getConversationChain(vectorStore=vectorStore)
            retrievalChain = getAstraRetrievalChain(
                vectorStore=vectorStore, userSessionId=sessionId)
            chain.vectorStore = vectorStore
            chain.retrievalChain = retrievalChain
            chain.sessionId = sessionId

            return jsonify({'sucess': 1, 'status': status})
        except Exception as e:
            print(e)
            return jsonify({'sucess': 0})

# store session data to mongo db


@ app.route('/sessionData', methods=['POST'])
def sessionData():
    if (request.method == 'POST'):
        print(request.form['sessionName'])
        print(request.form['sessionDesc'])
        userId = app.config['chain'].userId
        sessionName = request.form['sessionName']
        sessionDesc = request.form['sessionDesc']
        sessionId = app.config['chain'].sessionId
        sessionDate = getCurrentDate()
        print(f'sessionDate {sessionDate}')
        print(
            f'difference check is {daysDifference("2024-05-06","2024-04-06")}')

        db.get_collection(userId).insert_one({
            'sessionName': sessionName,
            'sessionDesc': sessionDesc,
            'sessionId': sessionId,
            'sessionDate': sessionDate

        })

        return jsonify({'sucess': 1})


@app.route('/userAllSessions', methods=['POST'])
def userAllSessions():
    if (request.method == 'POST'):
        try:
            userId = app.config['chain'].userId

            currentDate = getCurrentDate()
            currentSessionId = app.config['chain'].sessionId
            currentSessionDocument = db.get_collection(
                userId).find_one({"sessionId": currentSessionId})
            if (currentSessionDocument == None):
                current = []
            else:
                currentSessionDocument = dict(currentSessionDocument)
                # print(f'these is you are searching {currentSessionDocument}')
                current = [{'sessionName': currentSessionDocument['sessionName'],
                            'sessionDesc': currentSessionDocument['sessionDesc'],
                            'sessionId': currentSessionId}]
            # print(current)
            today, lastWeek, others = [], [], []

            sessionsList = list(db.get_collection(userId).find())
            # print(f'full session list ')
            # print(sessionsList)
            sortToday, sortWeek = {}, {}
            for i in range(len(sessionsList)):
                session = dict(sessionsList[i])
                sessionDate = session['sessionDate']
                days = int(daysDifference(str(currentDate), str(sessionDate)))
                # print(f'days difference is {days}')
                if (days < 1):
                    today.append({'sessionName': session['sessionName'],
                                  'sessionDesc': session['sessionDesc'],
                                  'sessionId': session['sessionId']})
                elif (days >= 1 and days <= 7):
                    lastWeek.append({'sessionName': session['sessionName'],
                                    'sessionDesc': session['sessionDesc'],
                                     'sessionId': session['sessionId']})
                else:
                    others.append({'sessionName': session['sessionName'],
                                   'sessionDesc': session['sessionDesc'],
                                   'sessionId': session['sessionId']})
            # [0] index latest session [-1] index oldest seesion of time
            today.reverse(), lastWeek.reverse(), others.reverse()
            print(f'today: {today}')
            print(f'lastWeek: {lastWeek}')
            print(f'others: {others}')
            return jsonify({'current': current, 'today': today, 'lastWeek': lastWeek, 'others': others})
        except:
            return jsonify({'current': [], 'today': [], 'lastWeek': [], 'others': []})


@app.route('/loadVStore', methods=['POST'])
def loadVStore():
    if (request.method == 'POST'):
        # print('we have entered in test endpoint')
        userId = app.config['chain'].userId
        vectorStore = app.config['chain'].vectorStore
        if (vectorStore == None):
            vectorStore = getAstraVectorStore(
                docsChunks='', collectionName=userId, add=False)
            chain.vectorStore = vectorStore
        # print(f'we are getting these in test :{vectorStore}')
        return jsonify({'message': 'executed'})


@app.route('/sessionChatHistory', methods=['POST'])
def sessionChatHistory():
    if (request.method == 'POST'):
        try:
            userId = app.config['chain'].userId

            sessionId = request.form['sessionId']
            document = dict(db.get_collection(
                userId).find_one({'sessionId': sessionId}))
            print(f'changed sessionId {sessionId}')

            # modifing chain and session id based on user preference
            vectorStore = app.config['chain'].vectorStore
            # if (vectorStore == None):
            #     vectorStore = getAstraVectorStore(
            #         docsChunks='', collectionName=userId, add=False)

            retrievalChain = getAstraRetrievalChain(
                vectorStore=vectorStore, userSessionId=sessionId)
            chain.retrievalChain = retrievalChain
            chain.sessionId = sessionId
            chain.userChatHistory = document['userChatHistory']
            return jsonify({'userChatHistory': document['userChatHistory']})
        except Exception as e:
            print(f'Error in sessionChatHistory endpoint: {e}')
            return jsonify({'userChatHistory': [{'userQuery': 'no chatHistory retrieved', 'answer': 'no chatHistory retrieved'}]})


@ app.route('/process', methods=["POST"])
def process():
    try:
        if request.method == 'POST':
            userQuery = request.form['userQuery']
            print(f'userQuery value is {userQuery}')
            # print(f'conversationChain is {conversationChain}')
            retrievalChain = app.config['chain'].retrievalChain
            # print(f'retrievalChain in process: {retrievalChain}')
            if (retrievalChain != None):
                # for retrieval  chain
                response = retrievalChain.invoke({'input': userQuery})

                # for converstaion chain
                # response = retrievalChain.invoke({'question': userQuery})

                print(f'i am in retrieval response :{response}')
                chain.userChatHistory.append(
                    {'userQuery': userQuery, 'answer': response['answer']})
                return jsonify({"answer": response['answer']})

            else:
                return jsonify({"answer": 'Internal Error'})
    except Exception as e:
        print(f'Error in process endpoint: {e}')
        return jsonify({"answer": 'Internal Error'})


@ app.route('/userChatData', methods=['POST'])
def userChatData():
    try:
        userId = app.config['chain'].userId

        print('we are inside chatData')
        sessionId = app.config['chain'].sessionId
        userChatHistory = app.config['chain'].userChatHistory
        print(f'session id inside chat id {sessionId}')
        print(f'userChatHistroy {userChatHistory}')
        # ro = db.get_collection('sitaram').find_one_and_update({"_id": sessionId},
        #                                                       {"$set": {"newfield": "abc"}})
        if (len(userChatHistory) > 0.):
            ro = db.get_collection(userId).update_one({"sessionId": sessionId},
                                                      {"$set": {"userChatHistory": userChatHistory}})
            print(f'something that we got {ro}')
            return jsonify({'sucess': 1})
        else:
            return jsonify({'sucess': 0})

    except Exception as e:
        print(f'Error in userChatData endpoint: {e}')
        return jsonify({'sucess': 0})


if __name__ == "__main__":
    # app.run(host='localhost', port=5001, debug=False)
    from waitress import serve
    port = '3001'
    host = '192.168.43.30'
    # host = 'localhost'
    print(f'Server running at http://{host}:{port}')
    serve(app, port=port, host=host)
