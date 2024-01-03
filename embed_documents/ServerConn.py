import requests
import json


def conn(recorded_event):
    if not recorded_event:
        print("No events to send")
    else:
        try:
            response = requests.post(
                'http://localhost:9005/save',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(recorded_event)
            )
            if response.status_code == 200:
                print('Event data sent successfully')
            else:
                print('Failed to send event data: Status code', response.status_code)

        except requests.exceptions.RequestException as e:
            print('Error sending request:', e)