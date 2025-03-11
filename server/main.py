import json
import os
from flask import Flask
import server 

app = Flask(__name__, template_folder='../web-app', static_folder='../web-app/static')

if __name__ == "__main__":
    server = server.Server(app)
