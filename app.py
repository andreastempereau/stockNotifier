from flask import Flask
import main

app = Flask(__name__)

@app.route("/")
def run_app():
    main.run() # Execute your main stock checker logic
    return "App run successfully!"
    
if __name__ == "__main__":
   app.run()