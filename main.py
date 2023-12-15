import pygame
import math
import os
import random
from screeninfo import get_monitors

pygame.font.init()

DISPLAY = False

#   Pygame constants

FPS = 120

FONT1 = pygame.font.SysFont("Arial", 60)
FONT2 = pygame.font.SysFont("Arial", 40)
FONT3 = pygame.font.SysFont("Arial", 20)

primary_monitor = get_monitors()[0]

WIDTH = 2560    # primary_monitor.width
HEIGHT = 1440   # primary_monitor.height

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

COLOURS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "dark_grey": (50, 50, 50),
    "light_grey": (180, 180, 180),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 125, 0),
    "purple": (160, 70, 160)
}


#   Rocket class, used as an object that comes from the player and follows the mouse into enemies, which it then
#   damages. All rockets are managed by handle_rockets function.
class Rocket:

    def __init__(self, x, y, ang):
        self.x, self.y = x, y
        self.width = 50
        self.height = 102
        self.explosion_radius = 300
        self.rect = pygame.Rect(self.x - (self.width // 2), self.y, self.width, self.height)
        self.angle = ang
        self.vel = 1000 / FPS
        self.imgs = [
            pygame.transform.scale(pygame.image.load(os.path.join("Assets", "rocket1.png")), (self.width, self.height)),
            pygame.transform.scale(pygame.image.load(os.path.join("Assets", "rocket2.png")), (self.width, self.height)),
        ]
        self.img_ind = 0
        self.flame_imgs = []
        self.explode_imgs = []
        self.uptime = 0
        self.light_t = 1 * FPS
        self.smooth_turn = False
        self.exploding = False
        self.explode_max_time = 0.5 * FPS
        self.explode_time = self.explode_max_time
        self.proximity = 40
        self.proximity_time_max = 0.5 * FPS
        self.proximity_time = self.proximity_time_max
        self.health = 30

    def check_radius(self, target):
        distance = math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
        if distance <= self.explosion_radius:
            return True
        else:
            return False

    #   Explode method calculates the affected radius of the rocket's explosion in order to find the affected entities.
    def explode(self, player, enemies):
        self.exploding = True
        dmg_lst = []
        if self.check_radius(player):
            dmg_lst.append(player)

        for enemy in enemies:
            if self.check_radius(enemies[enemy]):
                dmg_lst.append(enemies[enemy])

        return dmg_lst

    def take_damage(self, dmg, player, enemies):
        self.health -= dmg
        if self.health <= 0:
            self.health = 0
            return self.explode(player, enemies)
        else:
            return []


#   Bullet class, used by players and enemies. Travel along the vector of their owners facing direction at the time
#   of their creation. Simply deal damage when hitting an opposing entity. All bullets are managed by
#   handle_bullets function.
class Bullet:

    def __init__(self, owner, bullets):
        self.tag = owner.tag
        self.id = "B{}".format(len(bullets) + 1)
        self.owner = owner
        self.width = 10
        self.height = 40
        self.damage = 10
        self.x, self.y = owner.x, owner.y
        self.img = pygame.transform.scale(owner.bullet_img,
                                          (self.width, self.height))
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.rect = self.img.get_rect(center=(owner.x, owner.y))
        self.angle = owner.angle
        self.vel = 3000 / FPS


class HealthPack:

    def __init__(self, health, time, x, y):
        self.x, self.y = x, y
        self.health = health
        self.time = time * FPS
        self.width, self.height = 40, 40
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.img = pygame.transform.scale(
            pygame.image.load(os.path.join("Assets", "Health pack.png")),
            (self.width, self.height))
        self.timeout = 0


#   Enemy class, low-health enemies that attack and can be attacked by the player. More will appear over time,
#   all of them are controlled by handle_enemies function.
class Enemy:

    def __init__(self, x, y, health, armour, speed, aggression):
        self.team_code = 2
        self.max_health = health
        self.health = self.max_health
        self.max_armour = armour
        self.armour = self.max_armour
        self.armour_mit = 0.4
        self.width = 100
        self.height = 100
        if armour == 0:
            self.img = pygame.transform.scale(
                pygame.image.load(os.path.join("Assets", "Enemy1.png")),  # "IMG_7363.png"  "Enemy1.png" "Th.png"
                (self.width, self.height))
        else:
            self.img = pygame.transform.scale(
                pygame.image.load(os.path.join("Assets", "Enemy2.png")),  # "IMG_7363.png"  "Enemy2.png" "Th.png"
                (self.width, self.height))
        self.angle = 0
        self.x = x
        self.y = y
        self.vel = speed / FPS
        self.x_vel = 0
        self.y_vel = 0
        self.dir = 1
        self.move_time = 0
        self.bullet_img = pygame.image.load(
            os.path.join("Assets", "Bullets", "Bullet_red.png"))
        self.aggression = aggression
        self.cooldown = ((0.8 * FPS) + (random.randint(0, 4) * FPS)) / self.aggression
        self.tag = "1"

    def get_vel(self, edge=0):
        div = random.random()
        self.x_vel = self.vel * div
        self.y_vel = self.vel - self.x_vel

        if edge == 0:
            self.dir = random.choice((1, 2, 3, 4))
        elif edge == 1:
            self.dir = random.choice((3, 4))
        elif edge == 2:
            self.dir = random.choice((1, 4))
        elif edge == 3:
            self.dir = random.choice((1, 2))
        elif edge == 4:
            self.dir = random.choice((2, 3))

    def shoot(self, bullets):
        self.cooldown = ((0.8 * FPS) + (random.randint(0, 2) * FPS)) / self.aggression
        return Bullet(self, bullets)

    def take_damage(self, dam):
        if self.armour > 0:
            self.armour -= dam
            dam *= self.armour_mit
            if self.armour <= 0:
                self.armour = 0

        self.health -= dam
        if self.health < 0:
            self.health = 0


#   Player class, controlled entirely by the user, managed by handle_player function. Is capable of shooting, dashing,
#   launching rockets and moving. Has limited health that will cause the games end upon reaching 0.
class Player:

    def __init__(self):
        self.team_code = 1
        self.width = 100
        self.height = 100
        self.y = (HEIGHT // 3) * 2
        self.x = (WIDTH // 2)
        self.vel = 350 / FPS
        self.img = pygame.transform.scale(
            pygame.image.load(os.path.join("Assets", "ArrowHead1.png")),
            # "Rizzvan.png""ArrowHead1.png""Brookiolyn.png"
            (self.width, self.height))
        self.angle = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)    #(200, 200)
        self.dash_distance = WIDTH / 3
        self.cooldown = 5 * FPS
        self.active_cooldown = self.cooldown
        self.cooldown_f = -1
        self.ico_i = -1
        self.r_ico_i = -1
        self.r_cooldown = 10 * FPS
        self.r_cooldown_f = -1
        self.r_active_cooldown = self.r_cooldown
        self.slash_ico_i = -1
        self.slash_cooldown = 5 * FPS
        self.slash_cooldown_f = -1
        self.slash_active_cooldown = self.slash_cooldown
        self.bullet_img = pygame.transform.scale(
            pygame.image.load(
                os.path.join("Assets", "Bullets", "Bullet_green.png")),
            (5, 20))
        self.max_shoot_delay = 0.2 * FPS
        self.shoot_time = self.max_shoot_delay
        self.max_health = 50000  # 100
        self.health = self.max_health
        self.tag = "0"
        self.overheat = 0
        self.max_overheat = 150
        self.overheat_cooldown = 0
        self.shoot_cool = 0.8 * FPS
        self.overheat_cool = 2.4 * FPS
        self.cooldown_rate = 30 / FPS
        self.kills = 0

    def dash(self, x, y):  # dash in the direction of the mouse
        a = abs(self.x - x)
        b = abs(self.y - y)

        c = math.sqrt(pow(a, 2) + pow(b, 2))

        mult = self.dash_distance / c

        if self.x < x:
            self.x += a * mult
            if self.y < y:
                self.y += b * mult
            else:
                self.y -= b * mult
        else:
            self.x -= a * mult
            if self.y < y:
                self.y += b * mult
            else:
                self.y -= b * mult

        if self.x <= 0:
            self.x = 1
        elif self.x >= WIDTH:
            self.x = WIDTH - 1
        if self.y <= 0:
            self.y = 1
        elif self.y >= HEIGHT:
            self.y = HEIGHT - 1

    def shoot(self, bullets):
        self.shoot_time = self.max_shoot_delay
        self.overheat += 5
        self.overheat_cooldown = self.shoot_cool
        if self.overheat > self.max_overheat:
            self.overheat = self.max_overheat
            self.overheat_cooldown = self.overheat_cool
        return Bullet(self, bullets)

    def shoot_rocket(self):
        return Rocket(self.x, self.y, self.angle)

    def take_damage(self, dam):
        self.health -= dam
        if self.health < 0:
            self.health = 0

    def heal(self, dam):
        self.health += dam
        if self.health > self.max_health:
            self.health = self.max_health

    def slash(self):
        return Slash(self)


class Slash:
    class SlashPrint:
        def __init__(self, rect, angle):
            self.rect = rect
            self.angle = angle

    #   slash animation cuts, printing 10 copies of Slash.png each turned 12 degrees form the previous,
    #   giving a total arc of 120 degrees
    def __init__(self, player):
        self.slash_prints = []
        self.x = player.x
        self.y = player.y
        self.width = 36
        self.height = 44
        self.vel = 5 / FPS
        self.arc = 120
        self.cast_time = 30 * FPS
        self.turn_per_frame = self.arc / self.cast_time
        self.display_angle = 0
        self.turn = 12
        self.initial_offset = math.radians(60)
        self.radius = 180
        self.angle = -player.angle + self.initial_offset
        self.length = math.pi * 40
        self.img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Slash.png")),
                                          (self.width, self.height))
        self.rotated_img = self.img
        self.rect = self.img.get_rect(center=(player.x, player.y))
        #   self.y += 40


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
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.cool = 0
        self.click_cooldown = 0.1 * FPS

    def is_clicked(self, *buttons):
        if self.cool <= 0:
            mouse_pressed = pygame.mouse.get_pressed()
            pressed = False
            for b in buttons:
                if mouse_pressed[b]:
                    pressed = True
                    break

            if pressed:
                x, y = pygame.mouse.get_pos()
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
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = pygame.mouse.get_pos()
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
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = pygame.mouse.get_pos()
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
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = pygame.mouse.get_pos()
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
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = pygame.mouse.get_pos()
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
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.cool = 0
            self.click_cooldown = 0.1 * FPS

        def is_clicked(self, *buttons):
            if self.cool <= 0:
                mouse_pressed = pygame.mouse.get_pressed()
                pressed = False
                for b in buttons:
                    if mouse_pressed[b]:
                        pressed = True
                        break

                if pressed:
                    x, y = pygame.mouse.get_pos()
                    if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                        self.cool = self.click_cooldown
                        return True


class Reticule:

    def __init__(self):
        with open(os.path.join("Settings", "Reticule.txt")) as f:
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


#   Called once per frame, goes through all enemies, turns them to face the player, mov es them in a random direction,
#   move, and shoot at the player. This function also checks if any of the enemies have a health of 0, and then kills
#   them if this is the case.
def handle_enemies(enemies, player, bullets, health_packs):
    kill_lst = []
    for enemy in enemies:

        #   Face player

        enemies[enemy].angle = (
                                       360 - math.atan2(player.y - enemies[enemy].y,
                                                        player.x - enemies[enemy].x) * 180 / math.pi) - 90
        rot_image = pygame.transform.rotate(enemies[enemy].img,
                                            enemies[enemy].angle)
        enemies[enemy].rect = rot_image.get_rect(center=(enemies[enemy].x,
                                                         enemies[enemy].y))

        #   Get direction
        if enemies[enemy].x_vel == 0 and enemies[enemy].y_vel == 0:
            enemies[enemy].get_vel()
        elif enemies[enemy].move_time % (2 * FPS) == 0:
            if random.randint(1, 3) != 1:
                enemies[enemy].get_vel()

        #   Move

        if enemies[enemy].dir < 3:
            if enemies[enemy].x + enemies[enemy].x_vel + enemies[enemy].width // 2 < WIDTH:
                enemies[enemy].x += enemies[enemy].x_vel
            else:
                enemies[enemy].get_vel(1)
            if enemies[enemy].dir == 1:
                if enemies[enemy].y + enemies[enemy].y_vel + enemies[enemy].height // 2 < HEIGHT:
                    enemies[enemy].y += enemies[enemy].y_vel
                else:
                    enemies[enemy].get_vel(4)
            else:
                if enemies[enemy].y - enemies[enemy].y_vel - enemies[enemy].height // 2 > 0:
                    enemies[enemy].y -= enemies[enemy].y_vel
                else:
                    enemies[enemy].get_vel(2)
        else:
            if enemies[enemy].x - enemies[enemy].x_vel - enemies[enemy].width // 2 > 0:
                enemies[enemy].x -= enemies[enemy].x_vel
            else:
                enemies[enemy].get_vel(3)
            if enemies[enemy].dir == 4:
                if enemies[enemy].y + enemies[enemy].y_vel + enemies[enemy].height // 2 < HEIGHT:
                    enemies[enemy].y += enemies[enemy].y_vel
                else:
                    enemies[enemy].get_vel(4)
            else:
                if enemies[enemy].y - enemies[enemy].y_vel - enemies[enemy].height // 2 > 0:
                    enemies[enemy].y -= enemies[enemy].y_vel
                else:
                    enemies[enemy].get_vel(2)

        #   shoot

        if enemies[enemy].cooldown > 0:
            enemies[enemy].cooldown -= 1
        else:
            bullets.append(enemies[enemy].shoot(bullets))

        if enemies[enemy].health == 0:
            kill_lst.append(enemy)

        #   tick

        enemies[enemy].move_time += 1

    #   check health

    for enemy in kill_lst:
        if random.randint(1, 7) == 1:
            health_packs.append(HealthPack(30, 10, enemies[enemy].x, enemies[enemy].y))
        del enemies[enemy]
        player.kills += 1


#   Called once per frame, this function is primarily used to handle all inputs from the user. This function uses the
#   xy coordinates of the mouse, faces the player towards it, reads key inputs to move, and mouse button to shoot,
#   dash and launch rockets. The function then checks if the player's health is 0, and ends the game if this is the case
def handle_player(player, keys_pressed, mouse_pressed, bullets, rockets, health_packs, slashes):
    x, y = pygame.mouse.get_pos()

    #   move

    if keys_pressed[pygame.K_a] and player.x - player.vel > 0:
        player.x -= player.vel
    if keys_pressed[pygame.K_d] and player.x + player.vel + player.width < WIDTH:
        player.x += player.vel
    if keys_pressed[pygame.K_w] and player.y - player.vel > 0:
        player.y -= player.vel
    if keys_pressed[pygame.K_s] and player.y + player.vel + player.height < HEIGHT:
        player.y += player.vel

    #   turn

    player.angle = (360 - math.atan2(y - player.y, x - player.x) * 180 / math.pi) - 90
    rot_image = pygame.transform.rotate(player.img, player.angle)
    player.rect = rot_image.get_rect(center=(player.x, player.y))

    #   dash

    if player.active_cooldown < player.cooldown:
        player.active_cooldown += 1
    elif mouse_pressed[2]:
        player.dash(x, y)
        player.active_cooldown = 0
        player.cooldown_f = 0
        player.ico_i = 0

    #   shoot

    if player.overheat_cooldown > 0:
        player.overheat_cooldown -= 1
    elif player.overheat_cooldown == 0 and player.overheat > 0:
        player.overheat -= player.cooldown_rate

    if player.shoot_time > 0:
        player.shoot_time -= 1
    elif mouse_pressed[0] and player.overheat < player.max_overheat:
        bullets.append(player.shoot(bullets))

    #   shoot rocket

    if player.r_active_cooldown < player.r_cooldown:
        player.r_active_cooldown += 1
    elif keys_pressed[pygame.K_e]:
        rockets.append(player.shoot_rocket())
        player.r_active_cooldown = 0
        player.r_cooldown_f = 0
        player.r_ico_i = 0

    #   slash

    if player.slash_active_cooldown < player.slash_cooldown:
        player.slash_active_cooldown += 1
    elif keys_pressed[pygame.K_q]:
        slashes.append(player.slash())
        player.slash_active_cooldown = 0
        player.slash_cooldown_f = 0
        player.slash_ico_i = 0

    #   check health pack

    for pack in health_packs:
        if pack.timeout == pack.time:
            health_packs.remove(pack)
        else:
            pack.timeout += 1
        if pack.x <= player.x <= pack.x + pack.width or pack.x <= player.x + player.width <= pack.x + pack.width and \
                pack.y <= player.y <= pack.y + pack.height or pack.y <= player.y + player.width <= pack.y + pack.width:
            if player.health < player.max_health:
                player.heal(pack.health)
                health_packs.remove(pack)

    #   check health

    if player.health == 0:
        end_game("You died...       L")
        return True

    return False


#   Called once per frame, this function goes through all bullets currently active and moves them, then checks if it
#   hits an entity of the opposing team, if this is the case, the bullet deals damage, and is removed. There is one
#   final check to ensure the bullet does not go out of bounds.
def handle_bullets(bullets, player, enemies):
    for bullet in bullets:

        #   move

        bullet.x += bullet.vel * math.sin(
            math.radians(abs(bullet.angle - 450) - 90))
        bullet.y -= bullet.vel * math.cos(
            math.radians(abs(bullet.angle - 450) - 90))

        bullet.rect.center = (int(bullet.x), int(bullet.y))

        #   check for hit

        if bullet.tag == "1":
            distance = math.sqrt((bullet.x - player.x) ** 2 + (bullet.y - player.y) ** 2)
            #   if player.x + player.width > bullet.x > player.x and \
            #   player.y + player.height > bullet.y > player.y:
            if distance <= player.width:
                player.take_damage(bullet.damage)
                bullets.remove(bullet)
        elif bullet.tag == "0":
            for enemy in enemies:
                distance = math.sqrt((bullet.x - enemies[enemy].x) ** 2 + (bullet.y - enemies[enemy].y) ** 2)
                #   if enemies[enemy].x + enemies[enemy].width > bullet.x > enemies[enemy].x and \
                #   enemies[enemy].y + enemies[enemy].height > bullet.y > enemies[enemy].y:
                if distance <= enemies[enemy].width:
                    enemies[enemy].take_damage(bullet.damage)
                    bullets.remove(bullet)
                    player.heal(3)
                    break

        #   check if out of bounds

        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT and bullet in bullets:
            bullets.remove(bullet)


def handle_slashes(slashes, player):
    for slash in slashes:
        slash.angle += slash.vel
        slash.x = player.x + slash.radius * math.cos(slash.angle)
        slash.y = player.y + slash.radius * math.sin(slash.angle)

        rotation_angle = -math.degrees(slash.angle) + 180
        slash.rotated_img = pygame.transform.rotate(slash.img, rotation_angle)
        slash.rect = slash.rotated_img.get_rect(center=(slash.x, slash.y))


def handle_rockets(rockets, player, enemies, bullets):
    x, y = pygame.mouse.get_pos()
    dmg_lst = []
    for rocket in rockets:
        if not rocket.exploding:
            if rocket.light_t > 0:
                rocket.light_t -= 1
            else:
                if rocket.img_ind == 0:
                    rocket.img_ind = 1
                else:
                    rocket.img_ind = 0
                rocket.light_t = 1 * FPS

            if rocket.smooth_turn:
                old_angle = rocket.angle

                new_angle = (
                                    360 - math.atan2(y - rocket.y, x - rocket.x) * 180 / math.pi) - 90
                rot_image = pygame.transform.rotate(rocket.imgs[rocket.img_ind], rocket.angle)
                rocket.rect = rot_image.get_rect(center=(rocket.x, rocket.y))

                reverse_old = old_angle - 180
                if reverse_old < 90:
                    reverse_old += 360

                if new_angle > old_angle:
                    rocket.angle = old_angle + ((new_angle - old_angle) / (FPS * 2))
                elif old_angle > new_angle:
                    rocket.angle = new_angle + ((old_angle - new_angle) / (FPS * 2))
                else:
                    rocket.angle = old_angle
            else:
                rocket.angle = (
                                       360 - math.atan2(y - rocket.y, x - rocket.x) * 180 / math.pi) - 90
            rot_image = pygame.transform.rotate(rocket.imgs[rocket.img_ind], rocket.angle)
            rocket.rect = rot_image.get_rect(center=(rocket.x, rocket.y))

            rocket.x += rocket.vel * math.sin(
                math.radians(abs(rocket.angle - 450) - 90))
            rocket.y -= rocket.vel * math.cos(
                math.radians(abs(rocket.angle - 450) - 90))

            for bullet in bullets:
                distance = math.sqrt((bullet.x - rocket.x) ** 2 + (bullet.y - rocket.y) ** 2)
                if distance < ((rocket.width + rocket.height) / 2):
                    dmg_lst = rocket.take_damage(bullet.damage, player, enemies)
                    bullets.remove(bullet)

            for enemy in enemies:
                distance = math.sqrt((enemies[enemy].x - rocket.x) ** 2 + (enemies[enemy].y - rocket.y) ** 2)
                if distance <= enemies[enemy].width:
                    dmg_lst = rocket.explode(player, enemies)

            distance = math.sqrt((x - rocket.x) ** 2 + (y - rocket.y) ** 2)
            if distance < rocket.proximity:
                if rocket.proximity_time > 0:
                    rocket.proximity_time -= 1
                else:
                    dmg_lst = rocket.explode(player, enemies)
            elif rocket.proximity_time < rocket.proximity_time_max:
                rocket.proximity_time += 1

            player.r_active_cooldown += (len(dmg_lst) * (player.r_cooldown / 5))
            for entity in dmg_lst:
                entity.take_damage(60)
        else:
            if rocket.explode_time <= 0:
                rockets.remove(rocket)
            else:
                rocket.explode_time -= 1


def display(player, enemies, dashes, bullets, r_icos, slash_icos, rockets, slashes, attribute_bar_ico, progress_bar_ico,
            health_packs,
            reticule, phase, runtime, ui):
    WIN.fill(COLOURS["black"])

    #   Show health packs

    for pack in health_packs:
        WIN.blit(pack.img, pack.rect)

    #   Show bullets

    for bullet in bullets:
        WIN.blit(
            pygame.transform.rotate(bullet.owner.bullet_img, bullet.angle),
            bullet.rect)

    #   Show player

    WIN.blit(pygame.transform.rotate(player.img, player.angle), player.rect)

    #   Show enemies

    for enemy in enemies:
        WIN.blit(
            pygame.transform.rotate(enemies[enemy].img, enemies[enemy].angle), enemies[enemy].rect)

    #   Show slashes

    for slash in slashes:
        for slash_print in slash.slash_prints:
            WIN.blit(pygame.transform.rotate(slash.img, slash_print.angle), slash_print.rect)
        WIN.blit(slash.rotated_img, pygame.Rect(
            slash.x - (slash.width / 2), slash.y - (slash.height / 2), slash.width, slash.height))

    #   Show rockets

    for rocket in rockets:
        if rocket.exploding:
            pygame.draw.circle(WIN, COLOURS["orange"], (rocket.x, rocket.y), rocket.explosion_radius)
        else:
            WIN.blit(pygame.transform.rotate(rocket.imgs[rocket.img_ind], rocket.angle),
                     rocket.rect)

    #   Show UI

    if ui:
        display_ui(player, enemies, dashes, r_icos, slash_icos, attribute_bar_ico, progress_bar_ico, reticule, phase,
                   runtime)

    pygame.display.update()


def display_ui(player, enemies, dashes, r_icos, slash_icos, attribute_bar_ico, progress_bar_ico, reticule, phase,
               runtime):
    for enemy in enemies:
        pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(
            (enemies[enemy].x - (enemies[enemy].width / 2)),
            (enemies[enemy].y - (enemies[enemy].height / 2)) - 10,
            ((enemies[enemy].health / enemies[enemy].max_health) * enemies[enemy].width),
            3
        ))

        if enemies[enemy].max_armour != 0:
            pygame.draw.rect(WIN, COLOURS["light_grey"], pygame.Rect(
                (enemies[enemy].x - (enemies[enemy].width / 2)),
                (enemies[enemy].y - (enemies[enemy].height / 2)) - 13,
                ((enemies[enemy].armour / enemies[enemy].max_armour) * enemies[enemy].width),
                3
            ))

    #   display cooldowns

    WIN.blit(dashes[0], (10, 10))
    WIN.blit(r_icos[0], (10, 50))
    WIN.blit(slash_icos[0], (10, 90))

    if player.ico_i < 0:
        player.ico_i = 30
    if player.cooldown_f < 0:
        player.cooldown_f = player.cooldown
    if player.active_cooldown > player.cooldown_f.__round__(3):
        player.ico_i += 1
        player.cooldown_f += player.cooldown / 30

    if player.r_ico_i < 0:
        player.r_ico_i = 30
    if player.r_cooldown_f < 0:
        player.r_cooldown_f = player.r_cooldown
    if player.r_active_cooldown > player.r_cooldown_f.__round__(3):
        player.r_ico_i += 1
        player.r_cooldown_f += player.r_cooldown / 30

    if player.slash_ico_i < 0:
        player.slash_ico_i = 30
    if player.slash_cooldown_f < 0:
        player.slash_cooldown_f = player.slash_cooldown
    if player.slash_active_cooldown > player.slash_cooldown_f.__round__(3):
        player.slash_ico_i += 1
        player.slash_cooldown_f += player.slash_cooldown / 30

    WIN.blit(dashes[player.ico_i], (10, 10))
    WIN.blit(r_icos[player.r_ico_i], (10, 50))
    WIN.blit(slash_icos[player.slash_ico_i], (10, 90))

    phase_text = FONT3.render("PHASE: {}".format(phase), True, COLOURS["white"])
    WIN.blit(phase_text, (((WIDTH / 2) - (phase_text.get_width() / 2)), (0 + phase_text.get_height())))
    kill_text = FONT3.render("KILLS: {}".format(player.kills), True, COLOURS["white"])
    WIN.blit(kill_text, (((WIDTH / 2) - (kill_text.get_width() / 2)), (20 + kill_text.get_height())))

    pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(15, HEIGHT - 8, (player.health / player.max_health) * 200, 1))
    if (player.health / player.max_health) * 200 > 193:
        pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(22, HEIGHT - 9, 193, 3))
    elif (player.health / player.max_health) * 200 > 7:
        pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(22, HEIGHT - 9, (player.health / player.max_health) * 200, 3))
    WIN.blit(attribute_bar_ico, (10, HEIGHT - 10))

    bar_colour = COLOURS["green"]
    if player.overheat >= player.max_overheat:
        bar_colour = COLOURS["red"]
    elif player.max_overheat * 0.8 <= player.overheat < player.max_overheat:
        bar_colour = COLOURS["yellow"]

    pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 15, HEIGHT - 8,
                                                  (player.overheat / player.max_overheat) * 200, 1))
    if (player.overheat / player.max_overheat) * 200 > 193:
        pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 22, HEIGHT - 9, 193, 3))
    elif (player.overheat / player.max_overheat) * 200 > 7:
        pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 22, HEIGHT - 9,
                                                      (player.overheat / player.max_overheat) * 200, 3))
    WIN.blit(attribute_bar_ico, (WIDTH - 210 - 10, HEIGHT - 10))

    #   Phase bar

    if phase == "1":
        phase_colour = COLOURS["green"]
    elif phase == "2":
        phase_colour = COLOURS["yellow"]
    elif phase == "3":
        phase_colour = COLOURS["orange"]
    elif phase == "4":
        phase_colour = COLOURS["red"]
    elif phase == "5":
        phase_colour = COLOURS["purple"]
    else:
        phase_colour = COLOURS["white"]

    pygame.draw.rect(WIN, phase_colour, pygame.Rect((WIDTH / 2 - (420 / 2)) + 8, 14, (runtime / 150) * 408, 1))
    if (runtime / 150) * 408 >= 8:
        if (runtime / 150) * 408 >= 400:
            pygame.draw.rect(WIN, phase_colour, pygame.Rect((WIDTH / 2 - (420 / 2)) + 15, 12, 392, 5))
        else:
            pygame.draw.rect(WIN, phase_colour,
                             pygame.Rect((WIDTH / 2 - (420 / 2)) + 15, 12, ((runtime / 150) * 408) - 7, 5))

    WIN.blit(progress_bar_ico, (WIDTH / 2 - (420 / 2), 10))

    #   Reticule

    x, y = pygame.mouse.get_pos()
    pygame.draw.rect(WIN, COLOURS["green"], pygame.Rect(
        x - (reticule.width / 2) - (reticule.gap / 2), y, reticule.width / 2, reticule.thickness
    ))
    pygame.draw.rect(WIN, COLOURS["green"], pygame.Rect(
        x + (reticule.gap / 2), y, reticule.width / 2, reticule.thickness
    ))
    pygame.draw.rect(WIN, COLOURS["green"], pygame.Rect(
        x, y - (reticule.height / 2) - (reticule.gap / 2), reticule.thickness, reticule.height / 2
    ))
    pygame.draw.rect(WIN, COLOURS["green"], pygame.Rect(
        x, y + (reticule.gap / 2), reticule.thickness, reticule.height / 2
    ))
    pygame.draw.circle(WIN, COLOURS["green"], (x, y), reticule.dot)


def pause_display(play_button, restart_button, settings_button, exit_button):
    WIN.fill(COLOURS["black"])

    pygame.draw.rect(WIN, play_button.colour, play_button.rect)
    play_text = FONT2.render(play_button.text, True, play_button.text_colour)
    WIN.blit(play_text, (play_button.x + ((play_button.width - play_text.get_width()) / 2),
                         (play_button.y + ((play_button.height - play_text.get_height()) / 2))))

    pygame.draw.rect(WIN, restart_button.colour, restart_button.rect)
    restart_text = FONT2.render(restart_button.text, True, restart_button.text_colour)
    WIN.blit(restart_text, (restart_button.x + ((restart_button.width - restart_text.get_width()) / 2),
                            (restart_button.y + ((restart_button.height - restart_text.get_height()) / 2))))

    pygame.draw.rect(WIN, settings_button.colour, settings_button.rect)
    settings_text = FONT2.render(settings_button.text, True, settings_button.text_colour)
    WIN.blit(settings_text, (settings_button.x + ((settings_button.width - settings_text.get_width()) / 2),
                             (settings_button.y + ((settings_button.height - settings_text.get_height()) / 2))))

    pygame.draw.rect(WIN, exit_button.colour, exit_button.rect)
    exit_text = FONT2.render(exit_button.text, True, exit_button.text_colour)
    WIN.blit(exit_text, (exit_button.x + ((exit_button.width - exit_text.get_width()) / 2),
                         (exit_button.y + ((exit_button.height - exit_text.get_height()) / 2))))

    pygame.display.update()


def settings_display(reticule_button, back_button):
    WIN.fill(COLOURS["white"])

    pygame.draw.rect(WIN, reticule_button.colour, reticule_button.rect)
    reticule_text = FONT2.render(reticule_button.text, True, reticule_button.text_colour)
    WIN.blit(reticule_text, (reticule_button.x + ((reticule_button.width - reticule_text.get_width()) / 2),
                             (reticule_button.y + ((reticule_button.height - reticule_text.get_height()) / 2))))

    pygame.draw.rect(WIN, back_button.colour, back_button.rect)
    back_text = FONT2.render(back_button.text, True, back_button.text_colour)
    WIN.blit(back_text, (back_button.x + ((back_button.width - back_text.get_width()) / 2),
                         (back_button.y + ((back_button.height - back_text.get_height()) / 2))))


def reticule_display(width_button, height_button, dot_button, gap_button, thickness_button, back_button):
    pass


def handle_cool(*buttons):
    for c_object in buttons:
        if c_object.cool > 0:
            c_object.cool -= 1
            if c_object.cool < 0:
                c_object.cool = 0


def handle_cool_i(*buttons):
    for c_object in buttons:
        if c_object.jumpDown.cool > 0:
            c_object.jumpDown.cool -= 1
            if c_object.jumpDown.cool < 0:
                c_object.jumpDown.cool = 0

        if c_object.down.cool > 0:
            c_object.down.cool -= 1
            if c_object.down.cool < 0:
                c_object.down.cool = 0

        if c_object.body.cool > 0:
            c_object.body.cool -= 1
            if c_object.body.cool < 0:
                c_object.body.cool = 0

        if c_object.up.cool > 0:
            c_object.up.cool -= 1
            if c_object.up.cool < 0:
                c_object.up.cool = 0

        if c_object.jumpUp.cool > 0:
            c_object.jumpUp.cool -= 1
            if c_object.jumpUp.cool < 0:
                c_object.jumpUp.cool = 0


def end_game(end_message):
    pygame.draw.rect(WIN, COLOURS["dark_grey"], pygame.Rect(0, (HEIGHT // 2) - 100, WIDTH, 200))
    end_text = FONT1.render(end_message, True, COLOURS["red"])
    WIN.blit(end_text, (WIDTH / 2 - end_text.get_width() // 2, HEIGHT // 2 - end_text.get_height() // 2))
    pygame.display.update()
    pygame.time.wait(3000)


def reset():
    # returns: pause, player, enemies, enemy_spawn_cooldown, esc_time, num, [bullets, rockets, health_packs, slashes],
    # [runtime, ticks, phase]

    return False, Player(), {}, False, 0, 1, [[], [], [], []], [0, 0, 1]


def main():
    pause = True
    settings = False
    reticule_bool = False
    ui = True

    player = Player()

    enemies = {}

    enemy_spawn_cooldown = False
    esc_time = 0
    spawn_rules = {
        "delay": 3,
        "max": 10,
    }

    runtime = 0
    phase = "1"

    num = 1

    bullets = []
    rockets = []
    health_packs = []
    slashes = []

    play_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60, COLOURS["green"],
                         "PLAY", COLOURS["white"])
    restart_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 10, WIDTH // 4, 60, COLOURS["dark_grey"],
                            "RESTART", COLOURS["white"])
    settings_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60,
                             COLOURS["light_grey"], "SETTINGS", COLOURS["white"])
    exit_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 160, WIDTH // 4, 60, COLOURS["red"],
                         "EXIT", COLOURS["white"])

    reticule_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60, COLOURS["green"],
                             "EDIT RETICULE", COLOURS["white"])
    back_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60,
                         COLOURS["light_grey"], "BACK", COLOURS["white"])

    width_button = IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 140, WIDTH // 4, 60, COLOURS["green"],
                             "PLAY", COLOURS["white"])

    height_button = IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60, COLOURS["green"],
                              "PLAY", COLOURS["white"])

    dot_button = IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 10, WIDTH // 4, 60, COLOURS["dark_grey"],
                           "RESTART", COLOURS["white"])

    gap_button = IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60,
                           COLOURS["light_grey"], "SETTINGS", COLOURS["white"])

    thickness_button = IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 160, WIDTH // 4, 60, COLOURS["red"],
                                 "EXIT", COLOURS["white"])

    reticule_back_button = Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 235, WIDTH // 4, 60,
                                  COLOURS["light_grey"], "BACK", COLOURS["white"])

    reticule = Reticule()

    ticks = 0

    attribute_bar_ico = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Attribute Bar.png")), (210, 5))
    progress_bar_ico = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Progress Bar.png")), (420, 9))

    icos = []
    r_icos = []
    slash_icos = []
    for i in range(0, 31):
        icos.append(
            pygame.image.load(
                os.path.join("Assets", "Dash_ico", "Dash{}.png".format(i))))
        r_icos.append(
            pygame.image.load(
                os.path.join("Assets", "Rocket_ico", "Rocket{}.png".format(i))))
        slash_icos.append(
            pygame.image.load(
                os.path.join("Assets", "Rocket_ico", "Rocket{}.png".format(i))
            )
        )

    pygame.display.set_caption("Shooter")
    clock = pygame.time.Clock()
    run = True
    while run:
        pygame.mouse.set_visible(pause)
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = not pause

                if event.key == pygame.K_F1:
                    ui = not ui

        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if pause:
            if play_button.is_clicked(0):
                pause = False

            if restart_button.is_clicked(0):
                pause, player, enemies, enemy_spawn_cooldown, esc_time, num, entity_lst, sec_lst = reset()
                runtime, ticks, phase = sec_lst[0], sec_lst[1], sec_lst[2]
                del sec_lst
                bullets, rockets, health_packs, slashes = entity_lst[0], entity_lst[1], entity_lst[2], entity_lst[3]
                del entity_lst
                pause = False

            if settings_button.is_clicked(0):
                settings = True

            if exit_button.is_clicked(0):
                pygame.quit()
                exit()

            if settings:
                if reticule_button.is_clicked(0):
                    reticule_bool = True

                if back_button.is_clicked(0):
                    settings = False

                if reticule_bool:
                    handle_cool_i(width_button, height_button, dot_button, gap_button, thickness_button)
                    handle_cool(reticule_back_button)
                    reticule_display(width_button, height_button, dot_button, gap_button, thickness_button,
                                     reticule_back_button)
                else:
                    handle_cool(reticule_button, back_button)
                    settings_display(reticule_button, back_button)
            else:
                handle_cool(play_button, restart_button, settings_button, exit_button)
                pause_display(play_button, restart_button, settings_button, exit_button)
        else:

            #   gameplay loop

            #   enemy spawn

            if len(enemies) < spawn_rules["max"]:
                if not enemy_spawn_cooldown:
                    if random.random() > 0.1:
                        enemies.update({
                            num:
                                Enemy(random.randint(30, WIDTH - 30),
                                      random.randint(30, HEIGHT - 30),
                                      15, 0, 300, 1)
                        })
                    else:
                        enemies.update({
                            num:
                                Enemy(random.randint(30, WIDTH - 30),
                                      random.randint(30, HEIGHT - 30),
                                      30, 30, 400, 1.2)
                        })
                    num += 1
                    enemy_spawn_cooldown = True

            handle_enemies(enemies, player, bullets, health_packs)
            pause = handle_player(player, keys_pressed, mouse_pressed, bullets, rockets, health_packs, slashes)
            handle_bullets(bullets, player, enemies)
            handle_slashes(slashes, player)
            handle_rockets(rockets, player, enemies, bullets)
            display(player, enemies, icos, bullets, r_icos, slash_icos, rockets, slashes, attribute_bar_ico,
                    progress_bar_ico, health_packs, reticule, phase, runtime, ui)

            if enemy_spawn_cooldown:
                if esc_time >= spawn_rules["delay"] * FPS:
                    enemy_spawn_cooldown = False
                    esc_time = 0
                else:
                    esc_time += 1

            if ticks >= FPS:
                ticks = 0
            else:
                ticks += 1

            if 0 <= runtime < 10:
                phase = "1"
                spawn_rules = {
                    "delay": 4,
                    "max": 5,
                }
            elif 10 <= runtime < 30:
                phase = "2"
                spawn_rules = {
                    "delay": 3,
                    "max": 10,
                }
            elif 30 <= runtime < 60:
                phase = "3"
                spawn_rules = {
                    "delay": 2,
                    "max": 15,
                }
            elif 60 <= runtime < 90:
                phase = "4"
                spawn_rules = {
                    "delay": 1.5,
                    "max": 20,
                }
            elif 90 <= runtime < 150:
                phase = "5"
                spawn_rules = {
                    "delay": 0.5,
                    "max": 30,
                }
            elif runtime >= 150:
                phase = "0"
                spawn_rules = {
                    "delay": 0,
                    "max": 0,
                }
                end_game("You won!      W")
                pause = True

            runtime += 1 / FPS

            #   End of gameplay loop


if __name__ == "__main__":
    main()
