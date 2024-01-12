import os
from PIL import Image


def refactor():
    for i in range(0, 31):
        img = Image.open(os.path.join("Assets", "Rocket_ico", f"Rocket{str(i)}.png"))
        img.save(os.path.join("Assets", "Warp_ico", f"Warp{str(i)}.png"))


def other():
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


other()