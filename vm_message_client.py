import socket
import json
import time

LOGGER_HOST = '192.168.56.20'
LOGGER_PORT = 65432

def send_payload(payload):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((LOGGER_HOST, LOGGER_PORT))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(4096)
            print(f"[{payload.get('vm_id', payload.get('machine_id'))}] Response: {response.decode().strip()}")
            return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def auto_start_vm(vm_id, machine_id, cpu, mem, cpu_req, mem_req, workload, priority):
    # Step 1: Register machine
    register_payload = {
        "type": "register",
        "machine_id": machine_id,
        "cpu": cpu,
        "mem": mem
    }
    send_payload(register_payload)
    time.sleep(0.5)  # Allow time for registration

    # Step 2: Send VM resource request
    resource_payload = {
        "type": "resource",
        "vm_id": vm_id,
        "cpu_req": cpu_req,
        "mem_req": mem_req,
        "workload": workload,
        "priority": priority
    }
    send_payload(resource_payload)

    # Step 3: Optional - Send message to another VM
    send = input("Do you want to send a message to another VM? (yes/no): ").strip().lower()
    if send == "yes":
        receiver_id = input("Enter receiver VM ID: ").strip()
        message = input("Enter message: ").strip()
        message_payload = {
            "type": "message",
            "sender_id": vm_id,
            "receiver_id": receiver_id,
            "message": message
        }
        send_payload(message_payload)

    # Step 4: Optional - Fetch any messages for this VM
    fetch = input(f"Do you want to fetch messages for VM {vm_id}? (yes/no): ").strip().lower()
    if fetch == "yes":
        fetch_payload = {
            "type": "fetch_messages",
            "receiver_id": vm_id
        }
        response = send_payload(fetch_payload)
        try:
            messages = json.loads(response.decode('utf-8'))
            if messages:
                print(f"\n[VM {vm_id}] Received {len(messages)} messages:")
                for msg in messages:
                    print(f"From {msg['sender_id']} @ {msg['timestamp']}:\n  {msg['message']}")
            else:
                print(f"[VM {vm_id}] No new messages.")
        except:
            print("[VM] Could not parse message response.")

if __name__ == "__main__":
    # Customize these values per real machine
    auto_start_vm(
        vm_id="vm1",
        machine_id="M1",
        cpu=4,
        mem=4,
        cpu_req=2,
        mem_req=8,
        workload=4,
        priority=1
    )
