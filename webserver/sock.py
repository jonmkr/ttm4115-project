from websockets.sync.client import connect
import json
from queue import Queue

input_queue = Queue()
output_queue = Queue()

with connect("ws://localhost:5000/ws") as ws:
    payload = {'type': 1, 'id': 3, 'name': 'Elgeseter', 'max_capacity': 10, 'availability': 6}

    ws.send(json.dumps(payload))

    while True:
        try:
            input_queue.put(json.loads(ws.recv(timeout=1)))
        except TimeoutError:
            pass
        
        if not output_queue.empty():
            ws.send(json.dumps(output_queue.get()))
