def towers_of_hanoi(n, from_tower, to_tower, aux_tower):
    """
    Solves the Towers of Hanoi problem for n disks.

    Args:
        n (int): Number of disks.
        from_tower (str): Starting tower.
        to_tower (str): Destination tower.
        aux_tower (str): Auxiliary tower.

    Returns:
        None
    """
    if n == 1:
        # Base case: move one disk from the from_tower to the to_tower
        print(f"Move disk 1 from {from_tower} to {to_tower}")
        return

    # Move n - 1 disks from the from_tower to the aux_tower
    towers_of_hanoi(n - 1, from_tower, aux_tower, to_tower)

    # Move the nth disk from the from_tower to the to_tower
    print(f"Move disk {n} from {from_tower} to {to_tower}")

    # Move n - 1 disks from the aux_tower to the to_tower
    towers_of_hanoi(n - 1, aux_tower, to_tower, from_tower)


def main():
    # Number of disks
    n = 4

    # Tower names
    from_tower = "A"
    to_tower = "C"
    aux_tower = "B"

    print(f"Solving Towers of Hanoi problem for {n} disks...")
    towers_of_hanoi(n, from_tower, to_tower, aux_tower)


if __name__ == "__main__":
    main()