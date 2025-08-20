#ideal_completion.py

class VaultEntryManager:
    def __init__(self, cleared_staff, all_staff):
        if not all_staff:
            raise ValueError("Total staff count must be at least 1")
        if not cleared_staff:
            raise ValueError("Cleared staff count must be at least 1")
        if len(cleared_staff) > len(all_staff):
            raise ValueError("Cleared staff count cannot exceed total staff count")
            
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
            return True  # Prevent raising exceptions if entry wasn't allowed
            
    def execute_task(self, task):
        if self.entry_granted:
            print(f"Cleared Entry for {self.staff_id}. Executed task: {task}")

def process_vault_access():
    # Input processing with constraint validation
    n = int(input())
    if n < 1:
        raise ValueError("Total staff count must be at least 1")
        
    all_staff = input().split()
    if len(all_staff) != n:
        raise ValueError(f"Expected {n} staff members, got {len(all_staff)}")
        
    g = int(input())
    if g < 1 or g > n:
        raise ValueError("Cleared staff count must be between 1 and total staff count")
        
    cleared_staff = input().split()
    if len(cleared_staff) != g:
        raise ValueError(f"Expected {g} cleared staff members, got {len(cleared_staff)}")
        
    q = int(input())
    if q < 1 or q > 10:
        raise ValueError("Number of requests must be between 1 and 10")
        
    entry_controls = VaultEntryManager(cleared_staff, all_staff)
    
    for _ in range(q):
        staff_id = input()
        task = input()
        with SafeAccessController(staff_id, entry_controls) as controller:
            controller.execute_task(task)

# Usage
if __name__ == "__main__":
    try:
        process_vault_access()
    except ValueError as e:
        print(f"Input Error: {e}")