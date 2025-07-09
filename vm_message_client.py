import socket
import json

def send_message(sender_id, receiver_id, message):
    payload = {
        "type": "message",
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "message": message
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('127.0.0.1', 65432))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024)
            print(f"[{sender_id} → {receiver_id}] Response: {response.decode().strip()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_message("vm1", "vm2", "Hello from VM1!")
