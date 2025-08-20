# ideal_completion.py
import sys
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
            return True
            
    def execute_task(self, task):
        if self.entry_granted:
            result = f"Cleared Entry for {self.staff_id}. Executed task: {task}"
            print(result)
            return result

def process_vault_access(input_stream, output_stream=sys.stdout):
    """
    Process vault access requests from an input stream and write results to output stream.
    
    Args:
        input_stream: A file-like object containing the input data
        output_stream: A file-like object to write the output (defaults to sys.stdout)
    
    Input Format:
        Line 1: n (total number of staff)
        Line 2: space-separated staff IDs
        Line 3: g (number of cleared staff)
        Line 4: space-separated cleared staff IDs
        Line 5: q (number of access requests)
        Following lines: staff_id and task pairs for each request
    
    Raises:
        ValueError: If input constraints are violated
    """
    sys.stdout = output_stream
    
    # Input processing with constraint validation
    n = int(input_stream.readline())
    if n < 1:
        raise ValueError("Total staff count must be at least 1")
        
    all_staff = input_stream.readline().strip().split()
    if len(all_staff) != n:
        raise ValueError(f"Expected {n} staff members, got {len(all_staff)}")
        
    g = int(input_stream.readline())
    if g < 1 or g > n:
        raise ValueError("Cleared staff count must be between 1 and total staff count")
        
    cleared_staff = input_stream.readline().strip().split()
    if len(cleared_staff) != g:
        raise ValueError(f"Expected {g} cleared staff members, got {len(cleared_staff)}")
        
    q = int(input_stream.readline())
    if q < 1 or q > 10:
        raise ValueError("Number of requests must be between 1 and 10")
        
    entry_controls = VaultEntryManager(cleared_staff, all_staff) 
    
    for _ in range(q):
        staff_id = input_stream.readline().strip()
        task = input_stream.readline().strip()
        with SafeAccessController(staff_id, entry_controls) as controller:
            controller.execute_task(task)
            
    sys.stdout = sys.__stdout__

if __name__ == "__main__":
    try:
        process_vault_access(sys.stdin)
    except ValueError as e:
        print(f"Input Error: {e}")