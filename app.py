from flask import Flask 
app = Flask(__name__)

@app.route("/")
def run_checker():
    # Existing price check logic
    return "Alerts running!"

if __name__ == "__main__":  
    app.run()