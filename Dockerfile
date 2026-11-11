FROM python:3.12-slim
#this docker file will be used in the build of our docker image for our FastAPI application.
WORKDIR /app

# Install dependencies first (cached layer)
#copy requirements.txt from root (.) and install dependencies to leverage Docker's caching mechanism. 
#This way, if the requirements.txt file hasn't changed, Docker will use the cached layer and skip re-installing dependencies,
# which speeds up the build process.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app.py to the root of our docker container or image. Copy app source
COPY app.py .

EXPOSE 8000

#uvicorn is the server that will run our FastAPI application. It listens on all network interfaces.
#0.0.0.0 is used to make the application accessible from outside the container and lets allow to use by anyone, 
#and port 8000 is the default port for FastAPI applications.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
