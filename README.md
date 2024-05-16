
# PDF-Insight(Gen-1)

PDF Insight: RAG-Based Gen-AI Application

## Demo

https://github.com/nis12ram/PDF-Insight/assets/145199311/2e652e52-df50-41f6-b302-43d5907df81b


## Tech Stack

**Client:** HTML, CSS, JS

**Server:** Flask

**Database:** Mongo-db, astra-db


## Features

- **Adding PDFs seamlessly**: Effortlessly incorporate PDF files into sessions.
- **Smooth session switching**: Easily transition between sessions with minimal hassle.
- **Streamlined for faster inference**: Designed for optimal performance, ensuring swift response times and minimal latency during inference.



### Environment Variables

- **`LANGCHAIN_API_KEY`**: Required for integrating with Langsmith (optional).

- **`LANGCHAIN_PROJECT`**: Specifies the name of the Langsmith project (optional).
  - Example: `LANGCHAIN_PROJECT="MY_PROJECT_NAME"`

- **`GROQ_API_KEY`**: Required for interacting with the Groq inference engine.

- **`ASTRA_DB_APPLICATION_TOKEN`**: Token used to connect with Astra DB.

- **`ASTRA_DB_ID`**: Identifier for connecting with Astra Vector DB.

- **`MONGO_CONNECTION_STRING`**: Connection string for MongoDB cluster.
  - Example: `MONGO_CONNECTION_STRING = "mongodb+srv://{username}:{password}@<cluster_name>.<value>.mongodb.net"`

- **`MONGO_CLUSTER_USERNAME`**: Username for accessing the MongoDB cluster.

- **`MONGO_CLUSTER_PASSWORD`**: Password for accessing the MongoDB cluster.

- **`APP_SECRET_KEY`**: Secret key for the Flask application.






 
  


## Run Locally

Clone the project

```bash
  git clone https://github.com/nis12ram/PDF-Insight.git
```

Create python virual environment

```bash
  python -m venv <path>/venv
```

Install requirements & Add .env file

```bash
  pip install -r requirements.txt
```

Change static path

`approach2flaskServer.py`
```bash
app.config['STATIC_FOLDER'] = <path_to_your_static_folder>
```
run 

`approach2flaskServer.py`
```bash
python approach2flaskServer.py
```

## RAG Architecture

![llmarch](https://github.com/nis12ram/PDF-Insight/assets/145199311/b0bf6412-cc98-4b15-a6a8-1dfae6ce09b3)

## APP Architecture

![systemArch](https://github.com/nis12ram/PDF-Insight/assets/145199311/9c4945a5-6c79-4ec4-97d1-aa2aabda9f20)



## Acknowledgements

 - [Krish Naik Langchain Series](https://youtu.be/KmQOlg5YfU0?si=rqIx6z1hURf47dWV)
 - [Alejandro MUlti Pdf Rag ](https://youtu.be/dXxQ0LR-3Hg?si=PjOJa3jSh77AXpbb)
 - [Sigma Web Dev Series](https://youtube.com/playlist?list=PLu0W_9lII9agq5TrH9XLIKQvv0iaF2X3w&si=XcFN0cZ2jyBfVvRK)

