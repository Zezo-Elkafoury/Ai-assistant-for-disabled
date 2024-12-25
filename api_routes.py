from fastapi import FastAPI, HTTPException, BackgroundTasks
import google.generativeai as genai
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from pinecone import Pinecone
import pyttsx3
import threading
from time import sleep
import speech_recognition as sr

load_dotenv()

app = FastAPI()

# Load environment variables
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "isef-project"

# Configure GenAI
genai.configure(api_key=GOOGLE_API_KEY)

# Configure Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
pinecone_index = pc.Index(PINECONE_INDEX_NAME)

# Set up TTS Engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
for voice in engine.getProperty('voices'):
    if "female" in voice.name.lower():
        engine.setProperty('voice', voice.id)
        break

# Models
class UserQuery(BaseModel):
    query: str

class EmbeddingRequest(BaseModel):
    text: str

class PineconeQuery(BaseModel):
    vector: list
    top_k: int = 5

class PineconeStoreRequest(BaseModel):
    id: str
    vector: list
    metadata: dict = {}

# Routes

system_prompt = """

Respond to user queries in JSON format. Include a message and routing information, selecting one of three specific actions based on the query: 

1. **General Task**  
2. **Explain a Website**  
3. **Explain a Screen**
4. **NULL/Other**

### **Input:**  
A user query (e.g., request, command, or question).

### **Output:**  
A JSON response structured as:  

```json
{
    "Message": "A response to the user query, e.g., 'Okay, I’ll handle this' or 'Here’s the explanation'.",
    "Routing": {
        "Action": "Choose one of: 'General Task', 'Explain a Website', or 'Explain a Screen'.",
        "Details": "Additional context or null if not needed."
    }
}
```

### **Examples:**  

1. **General Task:**  
   ```json
   {
       "Message": "Sure, I’ll handle that for you.",
       "Routing": {
           "Action": "General Task",
           "Details": "Execute the user’s requested task."
       }
   }
   ```

2. **Explain a Website:**  
   ```json
   {
       "Message": "Here’s an explanation of the website.",
       "Routing": {
           "Action": "Explain a Website",
           "Details": "Provide a detailed explanation of the website’s purpose, functionality, or design."
       }
   }
   ```

3. **Explain a Screen:**  
   ```json
   {
       "Message": "Let me explain this screen.",
       "Routing": {
           "Action": "Explain a Screen",
           "Details": "Provide details about the specific screen, its elements, or functionality."
       }
   }
   ```
"""

@app.post("/router/")
async def router(query: UserQuery):
    """Route a user query and return response in JSON format."""
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        system_instruction=system_prompt
    )
    chat = model.start_chat(history=[])
    response = chat.send_message(query.query)
    return response.text


@app.post("/generate-embedding/")
async def generate_embedding(request: EmbeddingRequest):
    """Generate embeddings for the given text."""
    try:
        embedding = genai.embed_content(
            model="models/text-embedding-004", content=request.text
        )
        return {"embedding": embedding["embedding"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pinecone/search/")
async def pinecone_search(request: PineconeQuery):
    """Search in Pinecone index using the provided vector."""
    try:
        results = pinecone_index.query(
            vector=request.vector, top_k=request.top_k, include_metadata=True
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/pinecone/store/")
async def pinecone_store(request: PineconeStoreRequest):
    """Store a vector in Pinecone."""
    try:
        pinecone_index.upsert(vectors=[{
            "id": request.id,
            "values": request.vector,
            "metadata": request.metadata
        }])
        return {"message": "Vector stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/speech-to-text/")
async def speech_to_text(background_tasks: BackgroundTasks):
    """Toggle speech recognition and return transcribed text."""
    recognizer = sr.Recognizer()

    def listen():
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source)
        return recognizer.recognize_google(audio)

    try:
        text = background_tasks.add_task(listen)
        return {"transcription": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Speech recognition failed")


@app.post("/text-to-speech/")
async def text_to_speech(text: str):
    """Convert given text to speech."""
    try:
        engine.say(text)
        engine.runAndWait()
        return {"message": "Speech played successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-code/")
async def generate_code(query: UserQuery):
    """Generate Python code for the given query."""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction="""
            Generate Python code for the task specified...
            """,
        )
        chat = model.start_chat(history=[])
        response = chat.send_message(query.query)
        return {"code": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


