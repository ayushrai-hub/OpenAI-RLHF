# ideal_completion.py

import turtle as tg

def setup_screen():
    screen = tg.Screen()
    screen.setup(width=800, height=600)
    screen.bgcolor('blue')
    return screen

def setup_turtle():
    turtle = tg.Turtle()
    turtle.speed(0)
    turtle.width(1)
    turtle.penup()
    turtle.goto(0, 0)
    turtle.pendown()
    return turtle

def calculate_positions():
    positions = []
    x, y = 0, 0
    a, b = 0, 1
    screen_width = 800  # Assuming the same screen setup as the setup_screen function
    for spot in range(1, 17):
        c = a + b
        a = b
        b = c

        if x + c > screen_width // 2 - c:
            x = -screen_width // 2
            y -= c  # Move down

        positions.append((x, y, c))
        x += c  # Move right by the size of the square
    return positions

def draw_fibonacci_shapes():
    screen = setup_screen()
    turtle = setup_turtle()
    colors = ['yellow', 'green', 'purple', 'white', 'black', 'orange', 'cyan']
    line_color = 'red'
    
    positions = calculate_positions()
    for x, y, c in positions:
        turtle.penup()
        turtle.goto(x, y)
        turtle.pendown()
        draw_square(turtle, c, line_color, colors[positions.index((x, y, c)) % len(colors)])
    
    screen.mainloop()

def draw_square(turtle, size, line_color, fill_color):
    turtle.color(line_color, fill_color)
    turtle.begin_fill()
    for _ in range(4):
        turtle.forward(size)
        turtle.right(90)
    turtle.end_fill()