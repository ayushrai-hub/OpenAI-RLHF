from typing import List
import sys

class VaultEntryManager:
    def __init__(self, cleared_staff: List[str], all_staff: List[str]):
        self.cleared_staff = set(cleared_staff)
        self.all_staff = set(all_staff)
        self.entry_allowed = False

    def allow_entry(self, staff_id: str):
        if staff_id not in self.all_staff:
            raise Exception(f"Unauthorized entry. Staff ID {staff_id} is invalid.")
        if staff_id not in self.cleared_staff:
            raise Exception(f"Unauthorized entry. Staff ID {staff_id} is not cleared for vault access.")
        self.entry_allowed = True

    def close_entry(self):
        self.entry_allowed = False

class SafeAccessController:
    def __init__(self, staff_id: str, entry_manager: VaultEntryManager):
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

    def execute_task(self, task: str):
        if self.entry_granted:
            print(f"Cleared Entry for {self.staff_id}. Executed task: {task}")

def process_vault_access(input_stream, output_stream=sys.stdout):
    input = input_stream.read().splitlines()
    n = int(input[0])
    all_staff = input[1].split()
    g = int(input[2])
    cleared_staff = input[3].split()
    q = int(input[4])
    
    entry_controls = VaultEntryManager(cleared_staff, all_staff)
    output = []

    for i in range(5, 5 + 2 * q, 2):
        staff_id = input[i]
        task = input[i + 1]
        with SafeAccessController(staff_id, entry_controls) as controller:
            if controller.entry_granted:
                output.append(f"Cleared Entry for {staff_id}. Executed task: {task}")

    output_stream.write("\n".join(output))