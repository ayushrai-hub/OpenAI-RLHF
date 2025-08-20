import turtle as tg

def calculate_positions():
    positions = []
    
    # Initial Fibonacci numbers
    a: int = 1
    b: int = 1

    # Start at the center of the screen (0,0)
    x, y = 0, 0
    direction: int = 0  # Start by moving right
    angle: int = 90     # Every step turns 90 degrees

    # Calculate positions of the squares in a Fibonacci spiral
    for spot in range(20):  # Increase range as needed
        c: int = a + b
        a, b = b, c
        
        # Store position and size of the square
        positions.append((x, y, c))
        
        # Update position in a spiral pattern
        if direction == 0:  # Right
            x += c
        elif direction == 90:  # Up
            y += c
        elif direction == 180:  # Left
            x -= c
        elif direction == 270:  # Down
            y -= c
        
        direction = (direction + angle) % 360  # Rotate 90 degrees
    
    return positions

def draw_fibonacci_shapes():
    # Setup the screen and turtle
    s: tg.Screen = tg.Screen()
    s.setup(width=800, height=800)
    s.bgcolor('blue')
    
    t: tg.Turtle = tg.Turtle()
    t.speed(0)
    t.width(1)
    
    colors: list = ['yellow', 'green', 'purple', 'white', 'black', 'orange', 'cyan']
    linecolor: str = 'red'
    
    # Fetch positions from the calculation
    positions = calculate_positions()

    # Draw shapes based on the calculated positions
    for spot, (x, y, c) in enumerate(positions):
        # Configure color
        t.color(linecolor, colors[spot % len(colors)])
        
        # Move to the starting position of the square
        t.penup()
        t.goto(x, y)
        t.pendown()

        # Draw square according to Fibonacci number
        t.begin_fill()
        for _ in range(4):
            t.forward(c)
            t.right(90)
        t.end_fill()

    s.mainloop()
