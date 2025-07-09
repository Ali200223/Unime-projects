import socket
import threading
import json
import time
from scheduler_core import LoggerVMScheduler, VMRequest, Machine
from datetime import datetime

HOST = '0.0.0.0'  # Listen on all interfaces for real deployment
PORT = 65432

# Initialize scheduler with no machines initially
scheduler = LoggerVMScheduler([])

# Track registered machines to avoid duplicates
registered_machines = set()

# Logs and inboxes
communication_logs = []
message_queues = {}  # receiver_id -> list of messages

def handle_client_connection(conn, addr):
    with conn:
        data = conn.recv(4096)
        if not data:
            return
        try:
            payload = json.loads(data.decode('utf-8'))
            ptype = payload.get("type")

            if ptype == "register":
                machine_id = payload["machine_id"]
                if machine_id not in registered_machines:
                    m = Machine(machine_id, payload["cpu"], payload["mem"])
                    scheduler.machines.append(m)
                    registered_machines.add(machine_id)
                    print(f"[Logger VM] Registered machine: {m}")
                    conn.sendall(b"Machine registered.\n")
                else:
                    conn.sendall(b"Machine already registered.\n")

            elif ptype == "resource":
                vm = VMRequest(
                    vm_id=payload["vm_id"],
                    cpu_req=payload["cpu_req"],
                    mem_req=payload["mem_req"],
                    workload=payload["workload"],
                    arrival_time=int(time.time()),
                    priority=payload["priority"]
                )
                scheduler.receive_request(vm)
                conn.sendall(b"Resource request received.\n")

            elif ptype == "message":
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "sender_id": payload["sender_id"],
                    "receiver_id": payload["receiver_id"],
                    "message": payload["message"]
                }
                communication_logs.append(log_entry)

                receiver_id = payload["receiver_id"]
                if receiver_id not in message_queues:
                    message_queues[receiver_id] = []
                message_queues[receiver_id].append(log_entry)

                print(f"[Logger VM] Queued message for {receiver_id}: {log_entry}")
                conn.sendall(b"Message received and queued.\n")

            elif ptype == "comm_request":
                scheduler.receive_comm_request(
                    payload["sender_id"],
                    payload["receiver_id"],
                    payload["priority"]
                )
                conn.sendall(b"Communication request queued.\n")

            elif ptype == "fetch_messages":
                receiver = payload["receiver_id"]
                msgs = message_queues.get(receiver, [])
                conn.sendall(json.dumps(msgs).encode('utf-8'))
                message_queues[receiver] = []
                print(f"[Logger VM] Delivered {len(msgs)} messages to {receiver}")

            else:
                conn.sendall(b"Unknown request type.\n")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"[Logger VM] {error_msg}")
            conn.sendall(error_msg.encode())

def scheduler_loop():
    while True:
        scheduler.scheduler_tick()
        approved_comms = scheduler.process_comm_requests()
        for req in approved_comms:
            print(f"[Logger VM] Communication approved: {req['sender_id']} → {req['receiver_id']}")
        time.sleep(1)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Logger VM] Server started on {HOST}:{PORT}")
    threading.Thread(target=scheduler_loop, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client_connection, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
