import time

class VMRequest:
    def __init__(self, vm_id, cpu_req, mem_req, workload, arrival_time, priority):
        self.vm_id = vm_id
        self.cpu_req = cpu_req
        self.mem_req = mem_req
        self.workload = workload
        self.arrival_time = arrival_time
        self.priority = priority
        self.status = "waiting"
        self.start_time = None
        self.end_time = None

    def __repr__(self):
        return f"VM<{self.vm_id}, P={self.priority}, W={self.workload}, CPU={self.cpu_req}, MEM={self.mem_req}, Arrived={self.arrival_time}>"

class Machine:
    def __init__(self, machine_id, total_cpu, total_mem):
        self.machine_id = machine_id
        self.total_cpu = total_cpu
        self.total_mem = total_mem
        self.available_cpu = total_cpu
        self.available_mem = total_mem
        self.running_vms = []

    def can_allocate(self, vm):
        return self.available_cpu >= vm.cpu_req and self.available_mem >= vm.mem_req

    def allocate(self, vm, current_time):
        self.available_cpu -= vm.cpu_req
        self.available_mem -= vm.mem_req
        vm.status = "running"
        vm.start_time = current_time
        self.running_vms.append(vm)

    def release_finished_vms(self, current_time):
        finished = []
        for vm in self.running_vms[:]:
            if vm.start_time + vm.workload <= current_time:
                vm.status = "finished"
                vm.end_time = current_time
                self.available_cpu += vm.cpu_req
                self.available_mem += vm.mem_req
                self.running_vms.remove(vm)
                finished.append(vm)
        return finished

    def __repr__(self):
        return f"[{self.machine_id}] CPU: {self.available_cpu}/{self.total_cpu}, MEM: {self.available_mem}/{self.total_mem}"

class LoggerVMScheduler:
    def __init__(self, machines):
        self.machines = machines
        self.waiting_queue = []
        self.time = 0
        self.execution_log = []

        # ✅ NEW: Communication request queue
        self.communication_queue = []

    def receive_request(self, vm_request):
        print(f"[Logger VM] Received: {vm_request}")
        self.waiting_queue.append(vm_request)

    def scheduler_tick(self):
        self.time += 1

        # Release VMs that have finished their workload
        for machine in self.machines:
            finished = machine.release_finished_vms(self.time)
            for vm in finished:
                self.execution_log.append(f"Time {self.time}: VM {vm.vm_id} finished on {machine.machine_id}")

        # Sort waiting queue before trying to allocate
        self.sort_waiting_queue()

        for vm in self.waiting_queue[:]:
            for machine in self.machines:
                if machine.can_allocate(vm):
                    machine.allocate(vm, self.time)
                    self.execution_log.append(f"Time {self.time}: VM {vm.vm_id} scheduled on {machine.machine_id}")
                    self.waiting_queue.remove(vm)
                    break

    def sort_waiting_queue(self):
        # Sort by priority (desc), then arrival time (asc), then workload (asc)
        n = len(self.waiting_queue)
        for i in range(n):
            for j in range(0, n - i - 1):
                a, b = self.waiting_queue[j], self.waiting_queue[j + 1]
                if self.should_swap(a, b):
                    self.waiting_queue[j], self.waiting_queue[j + 1] = b, a

    def should_swap(self, a, b):
        if a.priority < b.priority:
            return True
        elif a.priority == b.priority:
            if a.arrival_time > b.arrival_time:
                return True
            elif a.arrival_time == b.arrival_time:
                return a.workload > b.workload
        return False

    # ✅ Handle communication requests
    def receive_comm_request(self, sender_id, receiver_id, priority):
        timestamp = int(time.time())
        self.communication_queue.append({
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "priority": priority,
            "timestamp": timestamp
        })
        print(f"[Scheduler] Received COMM request: {sender_id} → {receiver_id} | P{priority}")

    def process_comm_requests(self, max_per_tick=2):
        self.communication_queue.sort(key=lambda r: (r["priority"], r["timestamp"]))
        approved = []

        for _ in range(min(max_per_tick, len(self.communication_queue))):
            request = self.communication_queue.pop(0)
            print(f"[Scheduler] APPROVED comm: {request['sender_id']} → {request['receiver_id']}")
            approved.append(request)

        return approved
