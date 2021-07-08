# Dependencies
from flask import Flask, render_template
import os

# Configuration
app = Flask(__name__)

# Data
people_from_app_py = [
{
    "name": "Thomas",
    "age": 33,
    "location": "New Mexico",
    "favorite_color": "Blue"
},
{
    "name": "Gregory",
    "age": 41,
    "location": "Texas",
    "favorite_color": "Red"
},
{
    "name": "Vincent",
    "age": 27,
    "location": "Ohio",
    "favorite_color": "Green"
},
{
    "name": "Alexander",
    "age": 29,
    "location": "Florida",
    "favorite_color": "Orange"
}
]

# Routes
@app.route("/")
def root():
    return render_template("main.j2", people=people_from_app_py)

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port, debug=True)
# Use 'python app.py' or 'flask run' to run in terminal