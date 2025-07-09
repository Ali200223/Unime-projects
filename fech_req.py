import socket
import json

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
    fetch_messages("vm2")
