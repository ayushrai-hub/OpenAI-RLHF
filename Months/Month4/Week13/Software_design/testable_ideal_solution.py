class VaultEntryManager:
    def __init__(self, cleared_staff, all_staff):
        self.cleared_staff = set(cleared_staff)
        self.all_staff = set(all_staff)
        self.entry_allowed = False

    def allow_entry(self, staff_id):
        if staff_id not in self.all_staff:
            raise Exception(f"Unauthorized entry. Staff ID {staff_id} is invalid.")
        if staff_id not in self.cleared_staff:
            raise Exception(f"Unauthorized entry. Staff ID {staff_id} is not cleared for vault access.")
        self.entry_allowed = True

    def close_entry(self):
        self.entry_allowed = False

class SafeAccessController:
    def __init__(self, staff_id, entry_manager):
        self.staff_id = staff_id
        self.entry_manager = entry_manager
        self.entry_granted = False

    def __enter__(self):
        try:
            self.entry_manager.allow_entry(self.staff_id)
            self.entry_granted = True
        except Exception as e:
            print(e)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.entry_manager.close_entry()
        if not self.entry_granted:
            return True  # Prevent raising exceptions if the entry wasn't allowed

    def execute_task(self, task):
        if self.entry_granted:
            return f"Cleared Entry for {self.staff_id}. Executed task: {task}"

def process_vault_access(input_stream):
    input_data = input_stream.splitlines()
    n = int(input_data[0])
    all_staff = input_data[1].split()
    g = int(input_data[2])
    cleared_staff = input_data[3].split()
    q = int(input_data[4])

    entry_controls = VaultEntryManager(cleared_staff, all_staff)
    result = []

    idx = 5
    for _ in range(q):
        staff_id = input_data[idx]
        task = input_data[idx + 1]
        idx += 2

        with SafeAccessController(staff_id, entry_controls) as controller:
            task_result = controller.execute_task(task)
            if task_result:
                result.append(task_result)
    return result
