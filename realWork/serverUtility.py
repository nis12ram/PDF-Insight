# imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain.chains import ConversationalRetrievalChain, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.vectorstores.cassandra import Cassandra
import cassio
from langchain_groq import ChatGroq
from langchain_community.llms import Ollama
from langchain.memory import ConversationBufferMemory, ConversationEntityMemory
from langchain_core.prompts import PromptTemplate, SystemMessagePromptTemplate, ChatPromptTemplate
from pypdf import PdfReader
import os
from dotenv import load_dotenv
from datetime import datetime
import secrets
load_dotenv()

ASTRA_DB_APPLICATION_TOKEN = os.environ['ASTRA_DB_APPLICATION_TOKEN']
ASTRA_DB_ID = os.environ['ASTRA_DB_ID']
cassio.init(token=ASTRA_DB_APPLICATION_TOKEN, database_id=ASTRA_DB_ID)

# functions


def suitableId(userId):
    return f'id{userId}'


def getCurrentDate():
    currentDate = datetime.now()

    # Format the datetime object as per your requirement
    formattedDate = str(str(currentDate).split(' ')[0])
    return formattedDate


def daysDifference(date1_str, date2_str):
    # Convert date strings to datetime objects
    date1 = datetime.strptime(date1_str, '%Y-%m-%d')
    date2 = datetime.strptime(date2_str, '%Y-%m-%d')

    # Calculate the difference between the two dates
    difference = abs((date2 - date1).days)

    return difference


def generateSessionId(length=32):

    # Use secrets.token_bytes for cryptographically secure random bytes
    randomBytes = secrets.token_bytes(length // 2)
    # Convert bytes to hex string for easier use as session ID
    sessionId = randomBytes.hex()
    return sessionId


def getTextChunks(pdfFiles, getId=True, alreadyHaveId=None):
    if (getId == True):
        sessionId = generateSessionId()
    elif (getId == False):
        sessionId = alreadyHaveId

    textSplitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200)
    docsChunks = []
    for pdfFile in pdfFiles:
        fileName = pdfFile.filename
        pdfReader = PdfReader(pdfFile)
        pages = ""
        for page in pdfReader.pages:
            # text_chunks += page.extract_text()
            pages += page.extract_text()
        singlePdfDocs = [
            Document(page_content=pages, metadata={
                'sessionId': sessionId, 'fileName': fileName})
        ]
        singlePdfDocsChunks = textSplitter.split_documents(
            singlePdfDocs)
        docsChunks.extend(singlePdfDocsChunks)
    return docsChunks, sessionId


def getVectorStore(docsChunks):
    embeddingFunction = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2")

    # vectorStore = Lancedb.from_documents(docsChunks, embeddingFunction)
    # vectorStore.save_local("vectorDb")
    vectorStore = FAISS.from_documents(docsChunks, embeddingFunction)

    vectorStore.save_local("vectorDb")

    return vectorStore


def getAstraVectorStore(docsChunks, collectionName, add=True):

    embeddingFunction = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2")
    astraVectorStore = Cassandra(embedding=embeddingFunction,
                                 table_name=collectionName,
                                 session=None,
                                 keyspace=None)
    if (add == True):
        astraVectorStore.add_documents(documents=docsChunks)

    return astraVectorStore



def uploadToVectorStore(docsChunks):
    embeddingFunction = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2")

    # vectorStore = Lancedb.from_documents(docsChunks, embeddingFunction)
    # vectorStore.save_local("vectorDb")
    vectorStore = FAISS.from_documents(docsChunks, embeddingFunction)

    vectorStore.save_local("vectorDb")
    print('Feature vector stored in Faiss vectordb')


def loadVectorStore(dbPath):
    embeddingFunction = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2")

    vectorStore = FAISS.load_local(
        dbPath, embeddingFunction, allow_dangerous_deserialization=True)
    return vectorStore


# base on create_retrieval_chain
def getAstraRetrievalChain(vectorStore, userSessionId):
    print('i am indide the astra retrievla chain')
    print(f'the new user session id {userSessionId}')

    groqApiKey = os.environ['GROQ_API_KEY']
    prompt = ChatPromptTemplate.from_template("""
    Answer the following question base only on the provided context.
    Think step by step before providing a detailed answer.
    i will tip you $1000 if the user finds the answer helpful.
    if you don't know the answer politely say i don't know.
    <context>
    {context}
    </context>
    Question: {input}""")

    llm = ChatGroq(groq_api_key=groqApiKey, model_name="llama3-8b-8192")
    documentChain = create_stuff_documents_chain(llm, prompt)
    retrievalChain = create_retrieval_chain(retriever=vectorStore.as_retriever(
        search_kwargs={'filter': {'sessionId': userSessionId}, 'k': 3}), combine_docs_chain=documentChain)

    return retrievalChain


# based on ConversationalRetrievalChain
def getAstraConversationChain(vectorStore, userSessionId):
    print('i am indide the astra conbversation chain')
    print(f'the new user session id {userSessionId}')
    groqApiKey = os.environ['GROQ_API_KEY']
    # llm = ChatGroq(groq_api_key=groq_api_key, model_name="gemma-7b-it")
    llm = ChatGroq(groq_api_key=groqApiKey, model_name="llama3-8b-8192")
    # llm = Ollama(model="gemma:2b")

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    # memory = ConversationEntityMemory(llm=llm, chat_history_key="chat_history",
    #                                   return_messages=True)
    customCondenseQuestionTemplate = """Given the following conversation and a follow-up message, rephrase the follow-up message to a stand-alone question or instruction that represents the user's intent, add all context needed if necessary to generate a complete and unambiguous question or instruction. Only modify the original question if the chat history provides important context or relevance to it. Maintain the same language as the follow-up input message.

Chat History:
{chat_history}

Follow Up Input: {question}
Standalone question or instruction:
"""

    conversationChain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorStore.as_retriever(
            search_kwargs={'filter': {'sessionId': userSessionId}, 'k': 3}),
        memory=memory,
        verbose=True,
        condense_question_prompt=PromptTemplate.from_template(
            customCondenseQuestionTemplate)

    )

    try:
        conversationChain.combine_docs_chain.llm_chain.prompt.template = """You are a Helpfull and Intelligent Assistant ,who only have the knowledege of context nothing else. 
        Analyze the context thoroughly and then try to answer the question solely based on the understanding that you gain from the context,otherwise politely say that i do not know.
        If the question seems totally unrelated to the current context, then you should gently remind me to keep the discussion focused.

{context}

Question: {question}
Helpful Answer:"""

    except Exception as e:
        if str(e) == '"ChatPromptTemplate" object has no field "template"':
            print("Error: ChatPromptTemplate has no 'template' field. Using fallback.")
            qaTemplate = SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=[
                'context'], template="You are a Helpfull and Intelligent Assistant ,who only have the knowledege of context nothing else.Analyze the context thoroughly and then try to answer the question solely based on the understanding that you gain from the context,otherwise politely say that i do not know.If the question seems totally unrelated to the current context, then you should gently remind me to keep the discussion focused....\n----------------\n{context}"))
            conversationChain.combine_docs_chain.llm_chain.prompt.messages[0] = qaTemplate
        else:
            print(f"Unexpected error: {e}")  # Handle other exceptions

    return conversationChain
