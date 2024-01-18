import os
import json
import math
from PIL import Image


def refactor():
    for i in range(0, 31):
        img = Image.open(os.path.join("Assets", "Rocket_ico", f"Rocket{str(i)}.png"))
        img.save(os.path.join("Assets", "Warp_ico", f"Warp{str(i)}.png"))


def crop():
    for i in range(1, 31):
        img = Image.open(os.path.join("Assets", "Glaive_ico", f"Glaive30.png"))
        width, height = img.size
        img = img.convert("RGBA")
        for y in range(height - i):
            for x in range(width):
                img.putpixel((x, y), (0, 0, 0, 0))
        img.save(os.path.join("Assets", "Glaive_ico", f"Glaive{str(i)}.png"))


def flip_test():
    import pygame
    import sys

    # Initialize Pygame
    pygame.init()

    # Set up display
    width, height = 400, 300
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Flip Example")

    # Load an image
    image = pygame.image.load("Assets/Rocket_ico/Rocket30.png")

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Flip the image horizontally and vertically
        flipped_image_horizontal = pygame.transform.flip(image, True, False)
        flipped_image_vertical = pygame.transform.flip(image, False, True)

        # Draw the original and flipped images on the screen
        screen.fill((255, 255, 255))
        screen.blit(image, (50, 50))
        screen.blit(flipped_image_horizontal, (200, 50))
        screen.blit(flipped_image_vertical, (200, 150))

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()
    sys.exit()


def write_json():
    data = {
        "colour": (0, 255, 0),
        "width": 20,
        "height": 20,
        "dot": 0,
        "gap": 0,
        "thickness": 1,
    }

    with open(os.path.join("Settings", "reticule.json"), "w") as file:
        json.dump(data, file, indent=4)


def get_json():
    with open(os.path.join("Settings", "reticule.json"), 'r') as file:
        data = json.load(file)

    print(data)


def check_on_line(start_x, start_y, end_x, end_y, point_x, point_y):
    # Calculate the slope
    if start_x != end_x:
        m = (end_y - start_y) / (end_x - start_x)
    else:
        # The line is vertical, so the slope is undefined
        m = float('inf')

    print(m)

    # Calculate the y-intercept
    b = start_y - m * start_x

    # Check if the point lies on the line
    if point_y == m * point_x + b:
        return True
    else:
        return False


def shortest_distance(start_x, start_y, end_x, end_y, point_x, point_y):
    # Calculate the length of the line segment
    line_length = math.dist((start_x, start_y), (end_x, end_y))

    # If the line has zero length, return the distance between the point and the start point
    if line_length == 0:
        return math.dist((start_x, start_y), (point_x, point_y))

    # Calculate the normalized direction vector of the line
    direction_x = (end_x - start_x) / line_length
    direction_y = (end_y - start_y) / line_length

    # Calculate the vector between the start point and the given point
    vector_x = point_x - start_x
    vector_y = point_y - start_y

    # Calculate the dot product of the vector and the direction vector
    dot_product = vector_x * direction_x + vector_y * direction_y

    # Check if the closest point is beyond the start point of the line
    if dot_product < 0:
        closest_point_x = start_x
        closest_point_y = start_y
    # Check if the closest point is beyond the end point of the line
    elif dot_product > line_length:
        closest_point_x = end_x
        closest_point_y = end_y
    else:
        # Calculate the closest point on the line to the given point
        closest_point_x = start_x + dot_product * direction_x
        closest_point_y = start_y + dot_product * direction_y

    # Calculate the distance between the closest point and the given point
    distance = math.dist((closest_point_x, closest_point_y), (point_x, point_y))

    return distance


def calculate_angle(x1, y1, x2, y2):
    # Calculate the angle in radians
    angle_radians = math.atan2(y2 - y1, x2 - x1)

    # Convert the angle to degrees
    angle_degrees = math.degrees(angle_radians)

    # Ensure the angle is between 0 and 180 degrees
    angle_degrees = (angle_degrees + 360) % 360

    # If the angle is greater than 90 degrees, subtract it from 180
    return angle_degrees
