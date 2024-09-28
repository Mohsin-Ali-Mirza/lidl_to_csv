from fastapi import FastAPI

#hello

app = FastAPI()


@app.get('/')
def hello_world():
    return "Hello,World"
