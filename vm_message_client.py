import socket
import json
import time

LOGGER_HOST = '127.0.0.1'
LOGGER_PORT = 65432

def send_payload(payload):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((LOGGER_HOST, LOGGER_PORT))
            s.sendall(json.dumps(payload).encode('utf-8'))
            response = s.recv(1024)
            print(f"[{payload.get('vm_id', payload.get('machine_id'))}] Response: {response.decode().strip()}")
    except Exception as e:
        print(f"Error: {e}")

def auto_start_vm(vm_id, machine_id, cpu, mem, cpu_req, mem_req, workload, priority):
    # Step 1: Register machine
    register_payload = {
        "type": "register",
        "machine_id": machine_id,
        "cpu": cpu,
        "mem": mem
    }
    send_payload(register_payload)

    time.sleep(0.5)  # Short delay to ensure registration is processed

    # Step 2: Send resource request for VM
    resource_payload = {
        "type": "resource",
        "vm_id": vm_id,
        "cpu_req": cpu_req,
        "mem_req": mem_req,
        "workload": workload,
        "priority": priority
    }
    send_payload(resource_payload)

if __name__ == "__main__":
    # Example: start VM1 on Machine M1
    auto_start_vm(
        vm_id="vm1",
        machine_id="M1",
        cpu=8,
        mem=32,
        cpu_req=2,
        mem_req=8,
        workload=5,
        priority=1
    )
