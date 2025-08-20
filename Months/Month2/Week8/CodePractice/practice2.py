def towers_of_hanoi(n, from_tower, to_tower, aux_tower):
    """
    Solve the Towers of Hanoi problem for n disks.

    Args:
        n (int): Number of disks.
        from_tower (str): Name of the tower where disks are initially stacked.
        to_tower (str): Name of the tower where disks need to be moved.
        aux_tower (str): Name of the auxiliary tower.

    Returns:
        None
    """
    if n == 1:
        # Base case: If there's only one disk, move it directly.
        print(f"Move disk 1 from tower {from_tower} to tower {to_tower}")
        return

    # Recursive case: Move n - 1 disks to the auxiliary tower.
    towers_of_hanoi(n - 1, from_tower, aux_tower, to_tower)

    # Move the nth disk to the destination tower.
    print(f"Move disk {n} from tower {from_tower} to tower {to_tower}")

    # Move the n - 1 disks from the auxiliary tower to the destination tower.
    towers_of_hanoi(n - 1, aux_tower, to_tower, from_tower)


# Define the number of disks and tower names.
n = 4
from_tower = 'A'
to_tower = 'C'
aux_tower = 'B'

# Solve the Towers of Hanoi problem.
print("Towers of Hanoi Solution:")
towers_of_hanoi(n, from_tower, to_tower, aux_tower)