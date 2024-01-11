#   \main.py

import pygame
import math
import os
import random
import ui_objects
import entities
from screeninfo import get_monitors

pygame.font.init()

DISPLAY = False

#   Pygame constants

FPS = 120

FONT1 = pygame.font.SysFont("Arial", 60)
FONT2 = pygame.font.SysFont("Arial", 40)
FONT3 = pygame.font.SysFont("Arial", 20)

primary_monitor = get_monitors()[0]

WIDTH = primary_monitor.width  # 2560    #   primary_monitor.width
HEIGHT = primary_monitor.height  # 1440    #    primary_monitor.height

WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

COLOURS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "dark_grey": (50, 50, 50),
    "light_grey": (180, 180, 180),
    "red": (255, 0, 0),
    "pink": (255, 120, 165),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "orange": (255, 125, 0),
    "purple": (160, 70, 160)
}


#   Called once per frame, goes through all enemies, turns them to face the player, mov es them in a random direction,
#   move, and shoot at the player. This function also checks if any of the enemies have a health of 0, and then kills
#   them if this is the case.
def handle_enemies(enemies, player, bullets, health_packs):
    kill_lst = []
    for enemy in enemies:

        #   Face player

        enemies[enemy].angle = (360 - math.atan2(player.y - enemies[enemy].y,
                                                 player.x - enemies[enemy].x) * 180 / math.pi) - 90
        rot_image = pygame.transform.rotate(enemies[enemy].img, enemies[enemy].angle)
        enemies[enemy].rect = rot_image.get_rect(center=(enemies[enemy].x, enemies[enemy].y))

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
            health_packs.append(entities.HealthPack(30, 10, enemies[enemy].x, enemies[enemy].y))
        del enemies[enemy]
        player.kills += 1


#   Called once per frame, this function is primarily used to handle all inputs from the user. This function uses the
#   xy coordinates of the mouse, faces the player towards it, reads key inputs to move, and mouse button to shoot,
#   dash and launch rockets. The function then checks if the player's health is 0, and ends the game if this is the case
def handle_player(player, keys_pressed, mouse_pressed, bullets, rockets, health_packs, glaives):
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

    #   glaive

    if player.glaive_active_cooldown < player.glaive_cooldown:
        player.glaive_active_cooldown += 1
    elif keys_pressed[pygame.K_q]:
        glaives.append(player.glaive())
        player.glaive_active_cooldown = 0
        player.glaive_cooldown_f = 0
        player.glaive_ico_i = 0

    #   check health pack

    for pack in health_packs:
        if pack.timeout == pack.time:
            health_packs.remove(pack)
        else:
            pack.timeout += 1
        if pack.x <= player.x <= pack.x + pack.width or pack.x <= player.x + player.width <= pack.x + pack.width and \
                pack.y <= player.y <= pack.y + pack.height or pack.y <= player.y + player.width <= pack.y + pack.width:
            player.collected_health_packs.append(pack)
            health_packs.remove(pack)

    if player.health < player.max_health:
        if keys_pressed[pygame.K_r]:
            if len(player.collected_health_packs) < 1:
                pass
            else:
                player.heal(player.collected_health_packs[0].health)
                player.collected_health_packs.pop(0)

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


def handle_glaives(glaives, player):
    for glaive in glaives:
        glaive.angle += glaive.vel
        glaive.x = player.x + glaive.radius * math.cos(glaive.angle)
        glaive.y = player.y + glaive.radius * math.sin(glaive.angle)

        rotation_angle = -math.degrees(glaive.angle) + 180
        glaive.rotated_img = pygame.transform.rotate(glaive.img, rotation_angle)
        glaive.rect = glaive.rotated_img.get_rect(center=(glaive.x, glaive.y))


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

                new_angle = (360 - math.atan2(y - rocket.y, x - rocket.x) * 180 / math.pi) - 90
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
                rocket.angle = (360 - math.atan2(y - rocket.y, x - rocket.x) * 180 / math.pi) - 90
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


def display(player, enemies, dashes, bullets, r_icos, glaive_icos, rockets, glaives, attribute_bar_ico, progress_bar_ico,
            health_packs,
            reticule, phase, runtime, ui):
    WIN.fill(COLOURS["black"])
    for pack in health_packs:
        WIN.blit(pack.img, pack.rect)

    #   Show bullets

    for bullet in bullets:
        WIN.blit(
            pygame.transform.rotate(bullet.owner.bullet_img, bullet.angle),
            bullet.rect)

    #   Show player

    WIN.blit(pygame.transform.rotate(player.img, player.angle), player.rect)
    pygame.draw.circle(WIN, COLOURS["pink"], (player.x, player.y), 3)

    #   Show enemies

    for enemy in enemies:
        WIN.blit(
            pygame.transform.rotate(enemies[enemy].img, enemies[enemy].angle), enemies[enemy].rect)

    #   Show glaives

    for glaive in glaives:
        for glaive_print in glaive.glaive_prints:
            WIN.blit(pygame.transform.rotate(glaive.img, glaive_print.angle), glaive_print.rect)
        WIN.blit(glaive.rotated_img, pygame.Rect(
            glaive.x - (glaive.width / 2), glaive.y - (glaive.height / 2), glaive.width, glaive.height))

    #   Show rockets

    for rocket in rockets:
        if rocket.exploding:
            pygame.draw.circle(WIN, COLOURS["orange"], (rocket.x, rocket.y), rocket.explosion_radius)
        else:
            WIN.blit(pygame.transform.rotate(rocket.imgs[rocket.img_ind], rocket.angle), rocket.rect)

    #   Show UI

    if ui:
        display_ui(player, enemies, dashes, r_icos, glaive_icos, attribute_bar_ico, progress_bar_ico, reticule, phase,
                   runtime)

    pygame.display.update()


def display_ui(player, enemies, dashes, r_icos, glaive_icos, attribute_bar_ico, progress_bar_ico, reticule, phase,
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
    WIN.blit(glaive_icos[0], (10, 90))

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

    if player.glaive_ico_i < 0:
        player.glaive_ico_i = 30
    if player.glaive_cooldown_f < 0:
        player.glaive_cooldown_f = player.glaive_cooldown
    if player.glaive_active_cooldown > player.glaive_cooldown_f.__round__(3):
        player.glaive_ico_i += 1
        player.glaive_cooldown_f += player.glaive_cooldown / 30

    WIN.blit(dashes[player.ico_i], (10, 10))
    WIN.blit(r_icos[player.r_ico_i], (10, 50))
    WIN.blit(glaive_icos[player.glaive_ico_i], (10, 90))

    phase_text = FONT3.render("PHASE: {}".format(phase), True, COLOURS["white"])
    WIN.blit(phase_text, (((WIDTH / 2) - (phase_text.get_width() / 2)), (0 + phase_text.get_height())))
    kill_text = FONT3.render("KILLS: {}".format(player.kills), True, COLOURS["white"])
    WIN.blit(kill_text, (((WIDTH / 2) - (kill_text.get_width() / 2)), (20 + kill_text.get_height())))

    healthpack_text = FONT3.render("Health Packs: {}".format(len(player.collected_health_packs)), True,
                                   COLOURS["white"])
    WIN.blit(healthpack_text, (WIDTH - healthpack_text.get_width() - 10, 0 + 10))

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

    pygame.draw.rect(WIN, bar_colour,
                     pygame.Rect(WIDTH - 210 - 20 + 15, HEIGHT - 8, (player.overheat / player.max_overheat) * 200, 1))
    if (player.overheat / player.max_overheat) * 200 > 193:
        pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 22, HEIGHT - 9, 193, 3))
    elif (player.overheat / player.max_overheat) * 200 > 7:
        pygame.draw.rect(WIN, bar_colour,
                         pygame.Rect(WIDTH - 210 - 20 + 22, HEIGHT - 9, (player.overheat / player.max_overheat) * 200,
                                     3))
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
    # returns: pause, player, enemies, enemy_spawn_cooldown, esc_time, num, [bullets, rockets, health_packs, glaives],
    # [runtime, ticks, phase]

    return False, entities.Player(), {}, False, 0, 1, [[], [], [], []], [0, 0, 1]


def main():
    pause = True
    settings = False
    reticule_bool = False
    ui = True

    player = entities.Player()

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
    glaives = []

    play_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60,
                                    COLOURS["green"], "PLAY", COLOURS["white"])
    restart_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 10, WIDTH // 4, 60,
                                       COLOURS["dark_grey"], "RESTART", COLOURS["white"])
    settings_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60,
                                        COLOURS["light_grey"], "SETTINGS", COLOURS["white"])
    exit_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 160, WIDTH // 4, 60,
                                    COLOURS["red"], "EXIT", COLOURS["white"])

    reticule_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60,
                                        COLOURS["green"], "EDIT RETICULE", COLOURS["white"])
    back_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60,
                                    COLOURS["light_grey"], "BACK", COLOURS["white"])

    width_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 140, WIDTH // 4, 60,
                                        COLOURS["green"], "PLAY", COLOURS["white"])

    height_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60,
                                         COLOURS["green"], "PLAY", COLOURS["white"])

    dot_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 10, WIDTH // 4, 60,
                                      COLOURS["dark_grey"], "RESTART", COLOURS["white"])

    gap_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60,
                                      COLOURS["light_grey"], "SETTINGS", COLOURS["white"])

    thickness_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 160, WIDTH // 4, 60,
                                            COLOURS["red"], "EXIT", COLOURS["white"])

    reticule_back_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 235, WIDTH // 4, 60,
                                             COLOURS["light_grey"], "BACK", COLOURS["white"])

    reticule = ui_objects.Reticule()

    ticks = 0

    attribute_bar_ico = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Attribute Bar.png")), (210, 5))
    progress_bar_ico = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Progress Bar.png")), (420, 9))

    icos = []
    r_icos = []
    glaive_icos = []
    for i in range(0, 31):
        icos.append(
            pygame.image.load(
                os.path.join("Assets", "Dash_ico", "Dash{}.png".format(i))))
        r_icos.append(
            pygame.image.load(
                os.path.join("Assets", "Rocket_ico", "Rocket{}.png".format(i))))
        glaive_icos.append(
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
                bullets, rockets, health_packs, glaives = entity_lst[0], entity_lst[1], entity_lst[2], entity_lst[3]
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
                                entities.Enemy(random.randint(30, WIDTH - 30), random.randint(30, HEIGHT - 30), 15, 0,
                                               300, 1)
                        })
                    else:
                        enemies.update({
                            num:
                                entities.Enemy(random.randint(30, WIDTH - 30), random.randint(30, HEIGHT - 30), 30, 30,
                                               400, 1.2)
                        })
                    num += 1
                    enemy_spawn_cooldown = True

            handle_enemies(enemies, player, bullets, health_packs)
            pause = handle_player(player, keys_pressed, mouse_pressed, bullets, rockets, health_packs, glaives)
            handle_bullets(bullets, player, enemies)
            handle_glaives(glaives, player)
            handle_rockets(rockets, player, enemies, bullets)
            display(player, enemies, icos, bullets, r_icos, glaive_icos, rockets, glaives, attribute_bar_ico,
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

#   \main.py
