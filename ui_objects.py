#   \ui_objects.py

import main

#   Button class, used in the pause menu, handles by id_clicked method in main()
#   and click cooldowns are handled by handle_objects()
class Button:

    def __init__(self, x, y, width, height, colour, text, text_colour):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.text = text
        self.text_colour = text_colour
        self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
        self.cool = 0
        self.click_cooldown = 0.1 * main.FPS

    def is_clicked(self, *buttons):
        if self.cool <= 0:
            mouse_pressed = main.pygame.mouse.get_pressed()
            pressed = False
            for b in buttons:
                if mouse_pressed[b]:
                    pressed = True
                    break

            if pressed:
                x, y = main.pygame.mouse.get_pos()
                if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                    self.cool = self.click_cooldown
                    return True


class IntButton:

    def __init__(self, x, y, width, height, colour, text, text_colour):

        self.jumpDown = self.JumpDown(x, y, height, colour, text_colour)
        self.down = self.Down(x, y, height, colour, text_colour)
        self.body = self.Body(x, y, width, height, colour, text, text_colour)
        self.up = self.Up(x, y, width, height, colour, text_colour)
        self.jumpUp = self.JumpUp(x, y, width, height, colour, text_colour)

    class JumpDown:

        def __init__(self, x, y, height, colour, text_colour):
            self.x = x
            self.y = y
            self.width = height
            self.height = height
            self.colour = colour
            self.text = "↡"
            self.text_colour = text_colour
            self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * main.FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = main.pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = main.pygame.mouse.get_pos()
                    if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                        self.cool = self.click_cooldown
                        return True

    class Down:

        def __init__(self, x, y, height, colour, text_colour):
            self.x = x + height + 10
            self.y = y
            self.width = height
            self.height = height
            self.colour = colour
            self.text = "↓"
            self.text_colour = text_colour
            self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * main.FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = main.pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = main.pygame.mouse.get_pos()
                    if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                        self.cool = self.click_cooldown
                        return True

    class Body:

        def __init__(self, x, y, width, height, colour, text, text_colour):
            self.x = x + (height * 2) + (10 * 2)  # left + 2 boxes, + 2 10 pixel gaps
            self.y = y
            self.width = width - (((height * 2) + (10 * 2)) * 2)
            self.height = height
            self.colour = colour
            self.text = text
            self.text_colour = text_colour
            self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * main.FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = main.pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = main.pygame.mouse.get_pos()
                    if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                        self.cool = self.click_cooldown
                        return True

    class Up:

        def __init__(self, x, y, width, height, colour, text_colour):
            self.x = x + (height * 2) + (10 * 3) + (width - (((height * 2) + (10 * 2)) * 2))
            self.y = y
            self.width = height
            self.height = height
            self.colour = colour
            self.text = "↑"
            self.text_colour = text_colour
            self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * main.FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = main.pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = main.pygame.mouse.get_pos()
                    if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                        self.cool = self.click_cooldown
                        return True

    class JumpUp:

        def __init__(self, x, y, width, height, colour, text_colour):
            self.x = x + (height * 3) + (10 * 4) + (width - (((height * 2) + (10 * 2)) * 2))
            self.y = y
            self.width = height
            self.height = height
            self.colour = colour
            self.text = "↟"
            self.text_colour = text_colour
            self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * main.FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = main.pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = main.pygame.mouse.get_pos()
                    if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                        self.cool = self.click_cooldown
                        return True


class Reticule:

    def __init__(self):
        with open(main.os.path.join("Settings", "Reticule.txt")) as f:
            for i, x in enumerate(f):
                line = x.strip()
                if i == 0:
                    self.colour = tuple(line)
                elif i == 1:
                    self.width = int(line)
                elif i == 2:
                    self.height = int(line)
                elif i == 3:
                    self.dot = int(line)
                elif i == 4:
                    self.gap = int(line)
                elif i == 5:
                    self.thickness = int(line)

#   \ui_objects.py