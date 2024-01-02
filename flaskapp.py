from flask import Flask, request, jsonify
from flask_cors import CORS
from waitress import serve
from Recorder_IDE import root 
import threading

app = Flask(__name__)
CORS(app)

# In-memory storage for simplicity; consider a database for production use
events = []

@app.route('/save', methods=['POST'])
def save_events():
    print("Sending request to retrieve data to be saved ...")
    data = request.json
    print(f"\nThe recieved data is : {data}\n")
    events.extend(data)
    print(f"\n\n The saved events are : {events} \n\n")
    return jsonify({"status": "success"})


@app.route('/retrieve', methods=['GET'])
def retrieve_events():
    return jsonify(events)


def run_flask_app():
    print("The flask application has been successfully started!")
    serve(app, host='0.0.0.0', port=9000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    root.mainloop()
    
    

