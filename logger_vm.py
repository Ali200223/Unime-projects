import socket
import threading
import json
import time
from scheduler_core import LoggerVMScheduler, VMRequest, Machine
from datetime import datetime

HOST = '127.0.0.1'  # Use 0.0.0.0 on real VM
PORT = 65432

# Initialize scheduler with 3 machines
scheduler = LoggerVMScheduler([
    Machine("M1", 8, 32),
    Machine("M2", 6, 24),
    Machine("M3", 10, 40)
])

# NEW: Store communication logs
communication_logs = []

# Unified client handler
def handle_client_connection(conn, addr):
    with conn:
        data = conn.recv(2048)
        if not data:
            return
        try:
            payload = json.loads(data.decode('utf-8'))
            if payload.get("type") == "resource":
                # Handle resource request
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

            elif payload.get("type") == "message":
                # Handle communication message
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "sender_id": payload["sender_id"],
                    "receiver_id": payload["receiver_id"],
                    "message": payload["message"]
                }
                communication_logs.append(log_entry)
                print(f"[Logger VM] Logged message: {log_entry}")
                conn.sendall(b"Message logged.\n")
            elif payload.get("type") == "comm_request":
                sender = payload["sender_id"]
                receiver = payload["receiver_id"]
                priority = payload["priority"]
                scheduler.receive_comm_request(sender, receiver, priority)
                conn.sendall(b"Communication request queued.\n")


            else:
                conn.sendall(b"Unknown request type.\n")

        except Exception as e:
            conn.sendall(f"Error: {str(e)}".encode())

# Run scheduler periodically
def scheduler_loop():
    while True:
        scheduler.scheduler_tick()

        approved_comms = scheduler.process_comm_requests()
        for req in approved_comms:
            print(f"[Logger VM] Communication approved: {req['sender_id']} → {req['receiver_id']}")

        time.sleep(1)

# Start the TCP server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[Logger VM] Scheduler server started on {HOST}:{PORT}")
    
    # Start scheduler thread
    threading.Thread(target=scheduler_loop, daemon=True).start()

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client_connection, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
