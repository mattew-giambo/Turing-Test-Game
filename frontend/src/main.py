import uvicorn
from frontend.frontend import app
from config.constants import HOST, PORT

if __name__ =="__main__":
    uvicorn.run(app, host= HOST, port= PORT)