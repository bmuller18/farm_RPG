from flask import Flask, request, jsonify
from cropsystem.crops import wheat
app = Flask(__name__)



if __name__ == '__main__':
    app.run(debug=True)