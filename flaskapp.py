from flask import Flask, request, jsonify
from waitress import serve
from RecordGPT import root
import threading

app = Flask(__name__)

# In-memory storage for simplicity; consider a database for production use
events = []

@app.route('/save', methods=['POST'])
def save_events():
    data = request.json
    events.extend(data)
    print(f"\n\n The saved events are : {events} \n\n")
    return jsonify({"status": "success"})


@app.route('/retrieve', methods=['GET'])
def retrieve_events():
    return jsonify(events)


def run_flask_app():
    serve(app, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    root.mainloop()
    
    

