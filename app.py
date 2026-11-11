import os
import httpx #this is used to create client. It creates an asynchronous HTTP client to make requests to the Ollama API.
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Ollama API")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

class PromptRequest(BaseModel):
    prompt: str
    model: str = DEFAULT_MODEL

@app.get("/")
def home():
    return {
        "message": "Ollama API is running",
        "endpoints": {
            "health": "/health",
            "models": "/models",
            "generate": "/generate"
        }
    }

#the purpose of this endpoint is to verify if our FastAPI endpoint is able to communicate with Ollama server or not
#the purpose of this endpoint is to check the health of the Ollama API and return the list of available models. 
# It will return a status of "healthy" if the API is reachable and a list of models, 
# or "unhealthy" with an error message if there is an issue.
@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient() as Client: #it creates an asynchronous HTTP client using httpx library.
            response = await Client.get(f"{OLLAMA_BASE_URL}/api/tags") #this is used to check endpoint whether it is giving
            #response or not. It sends a Get request to Olammas /api/tags to retrieve the list of available models.
          
        return {
            "status": "healthy",
            "models": response.json()["models"]
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

#this endpoint is used to retrieve the list of available models from the Ollama API.      
@app.get("/models")
async def models():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
    return response.json()

#here PromptRequest is a class that we created upwards using BaseModel from pydantic library which means our request
#needs to have a prompt and a model.
#this is a text generation endpoint that accepts a prompt from the user and model as input, it sends to the Ollama 
#server for inferencing purpose and returns the generated response to you from the Ollama API.
@app.post("/generate")
async def generate(request: PromptRequest):
    payload = {
        "model": request.model,
        "prompt": request.prompt,
        "stream": False
    }
#stream is false as we need the complete response at once rather than streaming it in chunks.
    async with httpx.AsyncClient(timeout=120) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json = payload
        )
        
    return response.json()


