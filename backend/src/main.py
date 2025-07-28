from backend.backend import app
import uvicorn
from config.constants import HOST, PORT

if __name__ == "__main__":
    uvicorn.run(app, host= HOST, port= PORT)