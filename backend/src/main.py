from backend.backend import app
import uvicorn

if __name__ == "main":
    HOST = "127.0.0.1"
    PORT = 8003
    uvicorn.run(app, host= HOST, port= PORT)