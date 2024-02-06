import requests
import json


def conn(recorded_events):
    if not recorded_events:
        print("No events to send")
    else:
        try:
            response = requests.post(
                'http://localhost:9005/save',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(recorded_events)
            )
    
            if response.status_code == 200:
                print('Event data sent successfully')
            else:
                print('Failed to send event data: Status code', response.status_code)
    
        except requests.exceptions.RequestException as e:
            print('Error sending request:', e)   



def delete_last_event():
    try:
        response = requests.post('http://localhost:9005/delete-last')

        if response.status_code == 200:
            print('Last event deleted successfully')
            deleted_event = response.json().get('deleted_event')
            if deleted_event:
                print('Deleted event:', deleted_event)
                return deleted_event  # Return the deleted event
            else:
                print('No event was deleted.')
                return None
        else:
            print('Failed to delete last event: Status code', response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print('Error sending request:', e)
        return None
    


def reset_event_queue():
    try:
        response = requests.post('http://localhost:9005/reset')

        if response.status_code == 200:
            print('The event queue has been reset successfully for a new activity recording session.')
        else:
            print('Failed to delete last event: Status code', response.status_code)
            return None

    except requests.exceptions.RequestException as e:
        print('Error sending request:', e)
        return None

