# fetch_messages.py (dynamic version)
import socket
import json
import sys

def fetch_messages(receiver_id):
    payload = {
        "type": "fetch_messages",
        "receiver_id": receiver_id
    }
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 65432))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(4096)
            messages = json.loads(response.decode('utf-8'))
            if messages:
                print(f"[{receiver_id}] Received {len(messages)} messages:")
                for msg in messages:
                    print(f"From {msg['sender_id']} @ {msg['timestamp']}: {msg['message']}")
            else:
                print(f"[{receiver_id}] No new messages.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetch_messages.py <vm_id>")
    else:
        fetch_messages(sys.argv[1])
