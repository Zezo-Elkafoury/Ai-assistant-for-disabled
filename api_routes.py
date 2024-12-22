from fastapi import FastAPI
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# LLM Router (Main that talk to you)

"""
    Input: user query
    Output : Json format 
    {
        Message: e.g(okay , I will do this)
        routing : {
                Here's an api request e.g(choosing a command from pinecone)
                or nothing if it were a question , like continue chatting
            }
        } 
"""
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
import json


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash-exp',
    system_instruction=system_prompt)

chat = model.start_chat(history=[])

@app.get("/router/")
async def router(prompt:str):
    response = chat.send_message(prompt)
    return {response.text}

# LLM Choose the right command
"""
    Converting user's query into embedings using Gemini | return the embed text
    Search in pinecone | return top 5 matches
    LLM Choosing the command | return a command from pinecone or -1 if nothing
"""
# LLM for Generating & Running the code
"""
    inp: Query : output code that do this task
    Instal depedncencies : input: code , output : installing (success| fail)
    Run a certain python file :inp: filename , output: Success| fail

"""

# Store Generated code in Pinecone
"""
    inp: filename : generate the metadata for the instance e.g(description, command,etc..)
    Converting the description into vectors
    storing them in pinecone
"""
# LLM for answering questions 
