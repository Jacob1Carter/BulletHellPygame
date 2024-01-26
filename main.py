#   \main.py

import pygame
import math
import os
import random
import ui_objects
import entities
import json
from screeninfo import get_monitors
from tools import shortest_distance, calculate_angle

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

        enemies[enemy].angle = (360 - math.atan2(player.y - enemies[enemy].y, player.x - enemies[enemy].x) * 180 / math.pi) - 90
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
def handle_player(player, keys_pressed, mouse_pressed, bullets, rockets, health_packs, glaives, shockwaves):
    x, y = pygame.mouse.get_pos()

    #   zoom

    if player.zoom_cooldown > 0:
        player.zoom_cooldown -= 1
    else:
        if keys_pressed[pygame.K_SPACE]:
            player.zoom = True
        else:
            player.zoom = False
            if player.zoom_current < player.zoom_max:
                player.zoom_current += player.zoom_cooldown_rate

    #   turn

    player.angle = (360 - math.atan2(y - player.y, x - player.x) * 180 / math.pi) - 90
    flip_image = player.img
    if player.angle >= 360 or player.angle < 180:
        if player.facing_right:
            player.facing_right = False
            flip_image = pygame.transform.flip(player.img, True, False)
    if 360 > player.angle >= 180 and not player.facing_right:
        player.facing_right = True
        flip_image = pygame.transform.flip(player.img, True, False)
    player.img = flip_image

    rot_image = pygame.transform.rotate(player.img, player.angle)
    player.rect = rot_image.get_rect(center=(player.x, player.y))

    if player.zoom:
        #   move (zoom)
        player.x += player.zoom_vel * math.sin(
            math.radians(abs(player.angle - 450) - 90))
        player.y -= player.zoom_vel * math.cos(
            math.radians(abs(player.angle - 450) - 90))

        if player.zoom_current > 0:
            player.zoom_current -= 1
        else:
            player.zoom = False
            player.zoom_cooldown = player.zoom_cool

    else:
        #   move (no zoom)

        if keys_pressed[pygame.K_a] and player.x - player.vel > 0:
            player.x -= player.vel
        if keys_pressed[pygame.K_d] and player.x + player.vel + player.width < WIDTH:
            player.x += player.vel
        if keys_pressed[pygame.K_w] and player.y - player.vel > 0:
            player.y -= player.vel
        if keys_pressed[pygame.K_s] and player.y + player.vel + player.height < HEIGHT:
            player.y += player.vel

    #   dash

    if player.active_cooldown < player.cooldown:
        player.active_cooldown += 1
    elif mouse_pressed[2] and not player.zoom:
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
    elif mouse_pressed[0] and player.overheat < player.max_overheat and not player.zoom:
        bullets.append(player.shoot(bullets))

    #   shoot rocket

    if player.r_active_cooldown < player.r_cooldown:
        player.r_active_cooldown += 1
    elif keys_pressed[pygame.K_e] and not player.zoom:
        rockets.append(player.shoot_rocket())
        player.r_active_cooldown = 0
        player.r_cooldown_f = 0
        player.r_ico_i = 0

    #   glaive

    if player.glaive_active_cooldown < player.glaive_cooldown:
        player.glaive_active_cooldown += 1
    elif keys_pressed[pygame.K_q] and not player.zoom:
        glaives.append(player.glaive())
        player.glaive_active_cooldown = 0
        player.glaive_cooldown_f = 0
        player.glaive_ico_i = 0

    #   warp

    if player.warp_active_cooldown < player.warp_cooldown:
        player.warp_active_cooldown += 1
    elif keys_pressed[pygame.K_f] and not player.zoom:
        if len(player.warps) == 0:
            player.warps.append(player.place_warp())
        else:
            if player.warps[0].cast_time <= 0:
                shockwaves.append(player.activate_warp(player.warps[0]))

    for warp in player.warps:
        if warp.cast_time > 0:
            warp.cast_time -= 1

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

    #   add kills

    if keys_pressed[pygame.K_k]:
        player.kills += 1

    #   check health

    if player.health == 0:
        end_game("You died...       L")
        return True

    return False


#   Called once per frame, this function goes through all bullets currently active and moves them, then checks if it
#   hits an entity of the opposing team, if this is the case, the bullet deals damage, and is removed. There is one
#   final check to ensure the bullet does not go out of bounds.
def handle_bullets(bullets, player, enemies, covers):
    remove_list = []
    for bullet in bullets:

        #   move
        if not bullet.hit_marker:
            bullet.x += bullet.vel * math.sin(
                math.radians(abs(bullet.angle - 450) - 90))
            bullet.y -= bullet.vel * math.cos(
                math.radians(abs(bullet.angle - 450) - 90))

            bullet.rect.center = (int(bullet.x), int(bullet.y))

            #   check if hit cover

            for cover in covers:
                if cover.type == "shield" or cover.type == "wall":
                    for segment in cover.segments:
                        if shortest_distance(segment.ax, segment.ay, segment.bx, segment.by, bullet.x, bullet.y) <= bullet.width * 2:
                            if bullet not in remove_list:
                                remove_list.append(bullet)
                            break
                elif cover.type == "ricochet":
                    for segment in cover.segments:
                        if shortest_distance(segment.ax, segment.ay, segment.bx, segment.by, bullet.x, bullet.y) <= bullet.width * 2:
                            if bullet.tag == "0" and bullet.ricochet_cool == bullet.ricochet_cool_max:
                                line_angle = calculate_angle(segment.ax, segment.ay, segment.bx, segment.by)
                                #   bullet.angle += 180
                                bullet.angle = bullet.angle - line_angle
                                if bullet.angle >= 360:
                                    bullet.angle -= 360
                                bullet.img = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Bullets", "Bullet_yellow.png")), (bullet.width, bullet.height))
                                bullet.tag = "2"
                                bullet.damage *= 2
                                bullet.vel *= 1.5
                                bullet.ricochet_cool = 0
                            else:
                                if bullet not in remove_list:
                                    remove_list.append(bullet)
                                break

            #   check for hit
            if bullet.tag == "1" or bullet.tag == "2":
                distance = math.sqrt((bullet.x - player.x) ** 2 + (bullet.y - player.y) ** 2)
                if distance <= (player.width/2):
                    player.take_damage(bullet.damage)
                    bullet.hit_marker = True
            if bullet.tag == "0" or bullet.tag == "2":
                for enemy in enemies:
                    distance = math.sqrt((bullet.x - enemies[enemy].x) ** 2 + (bullet.y - enemies[enemy].y) ** 2)
                    if distance <= (enemies[enemy].width * (2/3)):
                        enemies[enemy].take_damage(bullet.damage)
                        bullet.hit_marker = True
                        player.heal(3)
                        break

            #   check if out of bounds

            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                if bullet not in remove_list:
                    remove_list.append(bullet)

            if bullet.ricochet_cool < bullet.ricochet_cool_max:
                bullet.ricochet_cool += 1
            if bullet.ricochet_cool > bullet.ricochet_cool_max:
                bullet.ricochet_cool = bullet.ricochet_cool_max

        else:
            if bullet.hit_marker_time > 0:
                bullet.hit_marker_time -= 1
            else:
                if bullet not in remove_list:
                    remove_list.append(bullet)

    #   remove bullets

    for bullet in remove_list:
        bullets.remove(bullet)


def handle_glaives(glaives, player, enemies):
    for glaive in glaives:
        #   Move

        glaive.angle += glaive.vel
        glaive.x = player.x + glaive.radius * math.cos(glaive.angle)
        glaive.y = player.y + glaive.radius * math.sin(glaive.angle)

        glaive.rotated_img = pygame.transform.rotate(glaive.img, glaive.display_angle)
        glaive.rect = glaive.rotated_img.get_rect(center=(glaive.x, glaive.y))

        #   Rotate

        glaive.display_angle -= glaive.rotate_speed

        #   Check for hit

        for enemy in enemies:
            distance = math.sqrt((glaive.x - enemies[enemy].x) ** 2 + (glaive.y - enemies[enemy].y) ** 2)
            if distance <= enemies[enemy].width:
                enemies[enemy].take_damage(glaive.damage)
                glaives.remove(glaive)
                player.heal(glaive.damage)
                break

        if glaive.uptime >= glaive.max_uptime:
            glaives.remove(glaive)
        else:
            glaive.uptime += 1


def handle_shockwaves(shockwaves, enemies):
    for shockwave in shockwaves:
        shockwave.radius += shockwave.expand_speed
        shockwave.thickness += shockwave.thicken_speed

        for enemy in enemies:
            distance = math.sqrt((shockwave.x - enemies[enemy].x) ** 2 + (shockwave.y - enemies[enemy].y) ** 2)
            if (shockwave.radius - shockwave.thickness) <= distance <= shockwave.radius:
                if enemy not in shockwave.damage_list:
                    shockwave.damage_list.append(enemy)
                    enemies[enemy].take_damage(shockwave.damage)

        shockwave.damage = (shockwave.a * (math.sqrt(shockwave.thickness))) + (shockwave.b * shockwave.thickness) + shockwave.c

        if WIDTH >= HEIGHT:
            if shockwave.radius > WIDTH * 1.2:
                shockwaves.remove(shockwave)
        else:
            if shockwave.radius > HEIGHT * 1.2:
                shockwaves.remove(shockwave)


def handle_rockets(rockets, player, enemies, bullets, covers):
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
                if distance < (rocket.width + rocket.height)/2:
                    dmg_lst = rocket.take_damage(bullet.damage, player, enemies)
                    bullets.remove(bullet)

            for enemy in enemies:
                distance = math.sqrt((enemies[enemy].x - rocket.x) ** 2 + (enemies[enemy].y - rocket.y) ** 2)
                if distance <= enemies[enemy].width:
                    dmg_lst = rocket.explode(player, enemies)

            for cover in covers:
                for segment in cover.segments:
                    if shortest_distance(segment.ax, segment.ay, segment.bx, segment.by, rocket.x, rocket.y) <= rocket.width * (2 / 3):
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


def display(player, enemies, dashes, bullets, r_icos, glaive_icos, warp_icos, warp_active_ico, rockets, glaives, shockwaves, covers, attribute_bar_ico, progress_bar_ico, health_packs, reticule, phase, ui, bosses):
    WIN.fill(COLOURS["black"])
    for pack in health_packs:
        WIN.blit(pack.img, pack.rect)

    #   show cover

    for cover in covers:
        for segment in cover.segments:
            pygame.draw.line(WIN, cover.colour, (segment.ax, segment.ay), (segment.bx, segment.by), cover.thickness)
        #   pygame.draw.circle(WIN, COLOURS["orange"], (cover.segments[0].ax, cover.segments[0].ay), 5)
        #   pygame.draw.circle(WIN, COLOURS["pink"], (cover.segments[0].bx, cover.segments[0].by), 5)

    #   Show warp point

    for warp in player.warps:
        WIN.blit(warp.img, warp.rect)

    #   Show shockwave

    for shockwave in shockwaves:
        pygame.draw.circle(WIN, COLOURS["pink"], (shockwave.x, shockwave.y), shockwave.radius, int(shockwave.thickness))

    #   Show bullets

    for bullet in bullets:
        if not bullet.hit_marker:
            WIN.blit(
                pygame.transform.rotate(bullet.img, bullet.angle),
                bullet.rect)

    #   Show boss

    for boss in bosses:
        WIN.blit(boss.rotated, boss.rect)
        pygame.draw.rect(WIN, COLOURS["blue"], boss.rect)

    #   Show player

    WIN.blit(pygame.transform.rotate(player.img, player.angle), player.rect)

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
            #   pygame.draw.circle(WIN, COLOURS["pink"], (rocket.x, rocket.y), rocket.width * (2 / 3))

    #   Show UI

    if ui:
        display_ui(player, enemies, dashes, r_icos, glaive_icos, warp_icos, warp_active_ico, attribute_bar_ico, progress_bar_ico, reticule, phase)

    pygame.display.update()


def display_ui(player, enemies, dashes, r_icos, glaive_icos, warp_icos, warp_active_ico, attribute_bar_ico, progress_bar_ico, reticule, phase):
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
    #   Show hit markers

    """
    for bullet in bullets:
        pygame.draw.circle(WIN, COLOURS["pink"], (bullet.x, bullet.y), 5)
        if bullet.hit_marker:
            WIN.blit(bullet.hit_marker_img, bullet.hm_rect)
    """

    #   display cooldowns

    WIN.blit(dashes[0], (10, 10))
    WIN.blit(r_icos[0], (10, 50))
    WIN.blit(glaive_icos[0], (10, 90))
    WIN.blit(warp_icos[0], (10, 130))

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

    if player.warp_ico_i < 0:
        player.warp_ico_i = 30
    if player.warp_cooldown_f < 0:
        player.warp_cooldown_f = player.warp_cooldown
    if player.warp_active_cooldown > player.warp_cooldown_f.__round__(3):
        player.warp_ico_i += 1
        player.warp_cooldown_f += player.warp_cooldown / 30
    if player.warp_ico_i > 30:
        player.warp_ico_i = 30

    WIN.blit(dashes[player.ico_i], (10, 10))
    WIN.blit(r_icos[player.r_ico_i], (10, 50))
    WIN.blit(glaive_icos[player.glaive_ico_i], (10, 90))
    WIN.blit(warp_icos[player.warp_ico_i], (10, 130))

    if len(player.warps) > 0:
        WIN.blit(warp_active_ico, (10, 130))

    #   phase text

    phase_text = FONT3.render("PHASE: {}".format(phase), True, COLOURS["white"])
    WIN.blit(phase_text, (((WIDTH / 2) - (phase_text.get_width() / 2)), (0 + phase_text.get_height())))
    kill_text = FONT3.render("KILLS: {}".format(player.kills), True, COLOURS["white"])
    WIN.blit(kill_text, (((WIDTH / 2) - (kill_text.get_width() / 2)), (20 + kill_text.get_height())))

    #   Health packs

    healthpack_text = FONT3.render("Health Packs: {}".format(len(player.collected_health_packs)), True, COLOURS["white"])
    WIN.blit(healthpack_text, (WIDTH - healthpack_text.get_width() - 10, 0 + 10))

    #   Player health bar

    if not player.invulnerable:
        pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(15, HEIGHT - 8, (player.health / player.max_health) * 200, 1))
        if (player.health / player.max_health) * 200 > 193:
            pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(22, HEIGHT - 9, 193, 3))
        elif (player.health / player.max_health) * 200 > 7:
            pygame.draw.rect(WIN, COLOURS["red"], pygame.Rect(22, HEIGHT - 9, (player.health / player.max_health) * 200, 3))
        WIN.blit(attribute_bar_ico, (10, HEIGHT - 10))

    #   Player zoom bar

    pygame.draw.rect(WIN, COLOURS["blue"], pygame.Rect(((WIDTH/2)-(210/2))+5, HEIGHT - 8, (player.zoom_current / player.zoom_max) * 200, 1))
    if (player.zoom_current / player.zoom_max) * 200 > 193:
        pygame.draw.rect(WIN, COLOURS["blue"], pygame.Rect(((WIDTH/2)-(210/2))+12, HEIGHT - 9, 193, 3))
    elif (player.zoom_current / player.zoom_max) * 200 > 7:
        pygame.draw.rect(WIN, COLOURS["blue"], pygame.Rect(((WIDTH/2)-(210/2))+12, HEIGHT - 9, (player.zoom_current / player.zoom_max) * 200, 3))
    WIN.blit(attribute_bar_ico, (((WIDTH/2)-(210/2)), HEIGHT - 10))

    #   Player ammo bar

    bar_colour = COLOURS["green"]
    if player.overheat >= player.max_overheat:
        bar_colour = COLOURS["red"]
    elif player.max_overheat * 0.8 <= player.overheat < player.max_overheat:
        bar_colour = COLOURS["yellow"]

    pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 15, HEIGHT - 8, (player.overheat / player.max_overheat) * 200, 1))
    if (player.overheat / player.max_overheat) * 200 > 193:
        pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 22, HEIGHT - 9, 193, 3))
    elif (player.overheat / player.max_overheat) * 200 > 7:
        pygame.draw.rect(WIN, bar_colour, pygame.Rect(WIDTH - 210 - 20 + 22, HEIGHT - 9, (player.overheat / player.max_overheat) * 200, 3))
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

    pygame.draw.rect(WIN, phase_colour, pygame.Rect((WIDTH / 2 - (420 / 2)) + 8, 14, (player.kills / 100) * 408, 1))
    if (player.kills / 100) * 408 >= 8:
        if (player.kills / 100) * 408 >= 400:
            pygame.draw.rect(WIN, phase_colour, pygame.Rect((WIDTH / 2 - (420 / 2)) + 15, 12, 392, 5))
        else:
            pygame.draw.rect(WIN, phase_colour, pygame.Rect((WIDTH / 2 - (420 / 2)) + 15, 12, ((player.kills / 100) * 408) - 7, 5))

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


def pause_display(play_button, restart_button, settings_button, exit_button, player):
    WIN.fill(COLOURS["black"])

    if player.health > 0 and player.kills < 100:
        pygame.draw.rect(WIN, play_button.colour, play_button.rect)
        play_text = FONT2.render(play_button.text, True, play_button.text_colour)
        WIN.blit(play_text, (play_button.x + ((play_button.width - play_text.get_width()) / 2), (play_button.y + ((play_button.height - play_text.get_height()) / 2))))

    pygame.draw.rect(WIN, restart_button.colour, restart_button.rect)
    restart_text = FONT2.render(restart_button.text, True, restart_button.text_colour)
    WIN.blit(restart_text, (restart_button.x + ((restart_button.width - restart_text.get_width()) / 2), (restart_button.y + ((restart_button.height - restart_text.get_height()) / 2))))

    pygame.draw.rect(WIN, settings_button.colour, settings_button.rect)
    settings_text = FONT2.render(settings_button.text, True, settings_button.text_colour)
    WIN.blit(settings_text, (settings_button.x + ((settings_button.width - settings_text.get_width()) / 2), (settings_button.y + ((settings_button.height - settings_text.get_height()) / 2))))

    pygame.draw.rect(WIN, exit_button.colour, exit_button.rect)
    exit_text = FONT2.render(exit_button.text, True, exit_button.text_colour)
    WIN.blit(exit_text, (exit_button.x + ((exit_button.width - exit_text.get_width()) / 2), (exit_button.y + ((exit_button.height - exit_text.get_height()) / 2))))

    pygame.display.update()


def settings_display(width_button, height_button, dot_button, gap_button, thickness_button, back_button, data):
    WIN.fill(COLOURS["black"])

    #   Width button

    pygame.draw.rect(WIN, width_button.jumpDown.colour, width_button.jumpDown.rect)
    width_jump_down_text = FONT2.render(width_button.jumpDown.text, True, width_button.jumpDown.text_colour)
    WIN.blit(width_jump_down_text, (width_button.jumpDown.x + ((width_button.jumpDown.width - width_jump_down_text.get_width()) / 2), (width_button.jumpDown.y + ((width_button.jumpDown.height - width_jump_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, width_button.down.colour, width_button.down.rect)
    width_down_text = FONT2.render(width_button.down.text, True, width_button.down.text_colour)
    WIN.blit(width_down_text, (width_button.down.x + ((width_button.down.width - width_down_text.get_width()) / 2), (width_button.down.y + ((width_button.down.height - width_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, width_button.body.colour, width_button.body.rect)
    width_body_text = FONT2.render("{0}: {1}".format(width_button.body.text, data["width"]), True, width_button.body.text_colour)
    WIN.blit(width_body_text, (width_button.body.x + ((width_button.body.width - width_body_text.get_width()) / 2), (width_button.body.y + ((width_button.body.height - width_body_text.get_height()) / 2))))

    pygame.draw.rect(WIN, width_button.up.colour, width_button.up.rect)
    width_up_text = FONT2.render(width_button.up.text, True, width_button.up.text_colour)
    WIN.blit(width_up_text, (width_button.up.x + ((width_button.up.width - width_up_text.get_width()) / 2), (width_button.up.y + ((width_button.up.height - width_up_text.get_height()) / 2))))

    pygame.draw.rect(WIN, width_button.jumpUp.colour, width_button.jumpUp.rect)
    width_jump_up_text = FONT2.render(width_button.jumpUp.text, True, width_button.jumpUp.text_colour)
    WIN.blit(width_jump_up_text, (width_button.jumpUp.x + ((width_button.jumpUp.width - width_jump_up_text.get_width()) / 2), (width_button.jumpUp.y + ((width_button.jumpUp.height - width_jump_up_text.get_height()) / 2))))

    #   Height button

    pygame.draw.rect(WIN, height_button.jumpDown.colour, height_button.jumpDown.rect)
    height_jump_down_text = FONT2.render(height_button.jumpDown.text, True, height_button.jumpDown.text_colour)
    WIN.blit(height_jump_down_text, (height_button.jumpDown.x + ((width_button.jumpDown.height - height_jump_down_text.get_width()) / 2), (height_button.jumpDown.y + ((height_button.jumpDown.height - height_jump_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, height_button.down.colour, height_button.down.rect)
    height_down_text = FONT2.render(height_button.down.text, True, height_button.down.text_colour)
    WIN.blit(height_down_text, (height_button.down.x + ((height_button.down.width - height_down_text.get_width()) / 2), (height_button.down.y + ((height_button.down.height - height_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, height_button.body.colour, height_button.body.rect)
    height_body_text = FONT2.render("{0}: {1}".format(height_button.body.text, data["height"]), True, height_button.body.text_colour)
    WIN.blit(height_body_text, (height_button.body.x + ((height_button.body.width - height_body_text.get_width()) / 2), (height_button.body.y + ((height_button.body.height - height_body_text.get_height()) / 2))))

    pygame.draw.rect(WIN, height_button.up.colour, height_button.up.rect)
    height_up_text = FONT2.render(height_button.up.text, True, height_button.up.text_colour)
    WIN.blit(height_up_text, (height_button.up.x + ((height_button.up.width - height_up_text.get_width()) / 2), (height_button.up.y + ((height_button.up.height - height_up_text.get_height()) / 2))))

    pygame.draw.rect(WIN, height_button.jumpUp.colour, height_button.jumpUp.rect)
    height_jump_up_text = FONT2.render(height_button.jumpUp.text, True, height_button.jumpUp.text_colour)
    WIN.blit(height_jump_up_text, (height_button.jumpUp.x + ((height_button.jumpUp.width - height_jump_up_text.get_width()) / 2), (height_button.jumpUp.y + ((height_button.jumpUp.height - height_jump_up_text.get_height()) / 2))))

    #   Dot button

    pygame.draw.rect(WIN, dot_button.jumpDown.colour, dot_button.jumpDown.rect)
    dot_jump_down_text = FONT2.render(dot_button.jumpDown.text, True, dot_button.jumpDown.text_colour)
    WIN.blit(dot_jump_down_text, (dot_button.jumpDown.x + ((dot_button.jumpDown.width - dot_jump_down_text.get_width()) / 2), (dot_button.jumpDown.y + ((dot_button.jumpDown.height - dot_jump_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, dot_button.down.colour, dot_button.down.rect)
    dot_down_text = FONT2.render(dot_button.down.text, True, dot_button.down.text_colour)
    WIN.blit(dot_down_text, (dot_button.down.x + ((dot_button.down.width - dot_down_text.get_width()) / 2), (dot_button.down.y + ((dot_button.down.height - dot_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, dot_button.body.colour, dot_button.body.rect)
    dot_body_text = FONT2.render("{0}: {1}".format(dot_button.body.text, data["dot"]), True, dot_button.body.text_colour)
    WIN.blit(dot_body_text, (dot_button.body.x + ((dot_button.body.width - dot_body_text.get_width()) / 2), (dot_button.body.y + ((dot_button.body.height - dot_body_text.get_height()) / 2))))

    pygame.draw.rect(WIN, dot_button.up.colour, dot_button.up.rect)
    dot_up_text = FONT2.render(dot_button.up.text, True, dot_button.up.text_colour)
    WIN.blit(dot_up_text, (dot_button.up.x + ((dot_button.up.width - dot_up_text.get_width()) / 2), (dot_button.up.y + ((dot_button.up.height - dot_up_text.get_height()) / 2))))

    pygame.draw.rect(WIN, dot_button.jumpUp.colour, dot_button.jumpUp.rect)
    dot_jump_up_text = FONT2.render(dot_button.jumpUp.text, True, dot_button.jumpUp.text_colour)
    WIN.blit(dot_jump_up_text, (dot_button.jumpUp.x + ((dot_button.jumpUp.width - dot_jump_up_text.get_width()) / 2), (dot_button.jumpUp.y + ((dot_button.jumpUp.height - dot_jump_up_text.get_height()) / 2))))

    #   Gap button

    pygame.draw.rect(WIN, gap_button.jumpDown.colour, gap_button.jumpDown.rect)
    gap_jump_down_text = FONT2.render(gap_button.jumpDown.text, True, gap_button.jumpDown.text_colour)
    WIN.blit(gap_jump_down_text, (gap_button.jumpDown.x + ((gap_button.jumpDown.width - gap_jump_down_text.get_width()) / 2), (gap_button.jumpDown.y + ((gap_button.jumpDown.height - gap_jump_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, gap_button.down.colour, gap_button.down.rect)
    gap_down_text = FONT2.render(gap_button.down.text, True, gap_button.down.text_colour)
    WIN.blit(gap_down_text, (gap_button.down.x + ((gap_button.down.width - gap_down_text.get_width()) / 2), (gap_button.down.y + ((gap_button.down.height - gap_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, gap_button.body.colour, gap_button.body.rect)
    gap_body_text = FONT2.render("{0}: {1}".format(gap_button.body.text, data["gap"]), True, gap_button.body.text_colour)
    WIN.blit(gap_body_text, (gap_button.body.x + ((gap_button.body.width - gap_body_text.get_width()) / 2), (gap_button.body.y + ((gap_button.body.height - gap_body_text.get_height()) / 2))))

    pygame.draw.rect(WIN, gap_button.up.colour, gap_button.up.rect)
    gap_up_text = FONT2.render(gap_button.up.text, True, gap_button.up.text_colour)
    WIN.blit(gap_up_text, (gap_button.up.x + ((gap_button.up.width - gap_up_text.get_width()) / 2), (gap_button.up.y + ((gap_button.up.height - gap_up_text.get_height()) / 2))))

    pygame.draw.rect(WIN, gap_button.jumpUp.colour, gap_button.jumpUp.rect)
    gap_jump_up_text = FONT2.render(gap_button.jumpUp.text, True, gap_button.jumpUp.text_colour)
    WIN.blit(gap_jump_up_text, (gap_button.jumpUp.x + ((gap_button.jumpUp.width - gap_jump_up_text.get_width()) / 2), (gap_button.jumpUp.y + ((gap_button.jumpUp.height - gap_jump_up_text.get_height()) / 2))))

    #   Thickness button

    pygame.draw.rect(WIN, thickness_button.jumpDown.colour, thickness_button.jumpDown.rect)
    thickness_jump_down_text = FONT2.render(thickness_button.jumpDown.text, True, thickness_button.jumpDown.text_colour)
    WIN.blit(thickness_jump_down_text, (thickness_button.jumpDown.x + ((thickness_button.jumpDown.width - thickness_jump_down_text.get_width()) / 2), (thickness_button.jumpDown.y + ((thickness_button.jumpDown.height - thickness_jump_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, thickness_button.down.colour, thickness_button.down.rect)
    thickness_down_text = FONT2.render(thickness_button.down.text, True, thickness_button.down.text_colour)
    WIN.blit(thickness_down_text, (thickness_button.down.x + ((thickness_button.down.width - thickness_down_text.get_width()) / 2), (thickness_button.down.y + ((thickness_button.down.height - thickness_down_text.get_height()) / 2))))

    pygame.draw.rect(WIN, thickness_button.body.colour, thickness_button.body.rect)
    thickness_body_text = FONT2.render("{0}: {1}".format(thickness_button.body.text, data["thickness"]), True, thickness_button.body.text_colour)
    WIN.blit(thickness_body_text, (thickness_button.body.x + ((thickness_button.body.width - thickness_body_text.get_width()) / 2), (thickness_button.body.y + ((thickness_button.body.height - thickness_body_text.get_height()) / 2))))

    pygame.draw.rect(WIN, thickness_button.up.colour, thickness_button.up.rect)
    thickness_up_text = FONT2.render(thickness_button.up.text, True, thickness_button.up.text_colour)
    WIN.blit(thickness_up_text, (thickness_button.up.x + ((thickness_button.up.width - thickness_up_text.get_width()) / 2), (thickness_button.up.y + ((thickness_button.up.height - thickness_up_text.get_height()) / 2))))

    pygame.draw.rect(WIN, thickness_button.jumpUp.colour, thickness_button.jumpUp.rect)
    thickness_jump_up_text = FONT2.render(thickness_button.jumpUp.text, True, thickness_button.jumpUp.text_colour)
    WIN.blit(thickness_jump_up_text, (thickness_button.jumpUp.x + ((thickness_button.jumpUp.width - thickness_jump_up_text.get_width()) / 2), (thickness_button.jumpUp.y + ((thickness_button.jumpUp.height - thickness_jump_up_text.get_height()) / 2))))

    #   Back button

    pygame.draw.rect(WIN, back_button.colour, back_button.rect)
    back_text = FONT2.render(back_button.text, True, back_button.text_colour)
    WIN.blit(back_text, (back_button.x + ((back_button.width - back_text.get_width()) / 2), (back_button.y + ((back_button.height - back_text.get_height()) / 2))))

    pygame.display.update()


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
    # returns: pause, player, enemies, enemy_spawn_cooldown, esc_time, num, [bullets, rockets, health_packs, glaives, shockwaves],
    # [ticks, phase]

    return False, entities.Player(), {}, False, 0, 1, [[], [], [], [], []], [0, 1]


def main():
    pause = True
    settings = False
    ui = True
    spawn_enemies = True

    enemy_spawn_cooldown = False
    esc_time = 0
    spawn_rules = {
        "delay": 3,
        "max": 10,
    }

    phase = "1"
    num = 1

    player = entities.Player()
    enemies = {}

    bullets = []
    rockets = []
    health_packs = []
    glaives = []
    shockwaves = []
    bosses = [entities.Boss()]
    covers = [
        entities.Cover(
            "shield",
            [
                (
                    WIDTH * (1 / 4),
                    HEIGHT * (1 / 3),
                ),
                (
                    WIDTH * (1 / 4),
                    HEIGHT - (HEIGHT * (1 / 3)),
                ),
            ]
        ),
        entities.Cover(
            "shield",
            [
                (
                    WIDTH - (WIDTH * (1 / 4)),
                    HEIGHT * (1 / 3),
                ),
                (
                    WIDTH - (WIDTH * (1 / 4)),
                    HEIGHT - (HEIGHT * (1 / 3)),
                ),
            ]
        ),
        entities.Cover(
            "shield",
            [
                (
                    WIDTH * (3 / 8),
                    HEIGHT * (1 / 4),
                ),
                (
                    WIDTH - (WIDTH * (3 / 8)),
                    HEIGHT * (1 / 4),
                ),
            ]
        ),
        entities.Cover(
            "shield",
            [
                (
                    WIDTH * (3 / 8),
                    HEIGHT - (HEIGHT * (1 / 4)),
                ),
                (
                    WIDTH - (WIDTH * (3 / 8)),
                    HEIGHT - (HEIGHT * (1 / 4)),
                ),
            ]
        ),

        entities.Cover(
            "ricochet",
            [
                (
                    WIDTH * (3 / 8),
                    HEIGHT * (1 / 4),
                ),
                (
                    WIDTH * (1 / 4),
                    HEIGHT * (1 / 3),
                ),
            ],
            (-80, -120)
        ),
        entities.Cover(
            "ricochet",
            [
                (
                    WIDTH - (WIDTH * (3 / 8)),
                    HEIGHT * (1 / 4),
                ),
                (
                    WIDTH - (WIDTH * (1 / 4)),
                    HEIGHT * (1 / 3),
                ),
            ],
            (80, -120)
        ),
        entities.Cover(
            "ricochet",
            [
                (
                    WIDTH - (WIDTH * (3 / 8)),
                    HEIGHT - (HEIGHT * (1 / 4)),
                ),
                (
                    WIDTH - (WIDTH * (1 / 4)),
                    HEIGHT - (HEIGHT * (1 / 3)),
                ),
            ],
            (80, 120)
        ),
        entities.Cover(
            "ricochet",
            [
                (
                    WIDTH * (1 / 4),
                    HEIGHT - (HEIGHT * (1 / 3)),
                ),
                (
                    WIDTH * (3 / 8),
                    HEIGHT - (HEIGHT * (1 / 4)),
                ),
            ],
            (-80, 120)
        ),
    ]

    play_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) - 65, WIDTH // 4, 60, COLOURS["green"], "PLAY", COLOURS["white"])
    restart_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 10, WIDTH // 4, 60, COLOURS["dark_grey"], "RESTART", COLOURS["white"])
    settings_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 85, WIDTH // 4, 60, COLOURS["light_grey"], "SETTINGS", COLOURS["white"])
    exit_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 4) / 2), (HEIGHT // 2) + 160, WIDTH // 4, 60, COLOURS["red"], "EXIT", COLOURS["white"])

    width_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 3) / 2), (HEIGHT // 2) - 140, WIDTH // 3, 60, COLOURS["green"], "WIDTH", COLOURS["white"])
    height_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 3) / 2), (HEIGHT // 2) - 65, WIDTH // 3, 60, COLOURS["green"], "HEIGHT", COLOURS["white"])
    dot_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 3) / 2), (HEIGHT // 2) + 10, WIDTH // 3, 60, COLOURS["dark_grey"], "DOT", COLOURS["white"])
    gap_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 3) / 2), (HEIGHT // 2) + 85, WIDTH // 3, 60, COLOURS["light_grey"], "GAP", COLOURS["white"])
    thickness_button = ui_objects.IntButton((WIDTH // 2) - ((WIDTH // 3) / 2), (HEIGHT // 2) + 160, WIDTH // 3, 60, COLOURS["red"], "THICKNESS", COLOURS["white"])
    back_button = ui_objects.Button((WIDTH // 2) - ((WIDTH // 3) / 2), (HEIGHT // 2) + 235, WIDTH // 3, 60, COLOURS["light_grey"], "BACK", COLOURS["white"])

    reticule = ui_objects.Reticule()

    ticks = 0

    attribute_bar_ico = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Attribute Bar.png")), (210, 5))
    progress_bar_ico = pygame.transform.scale(pygame.image.load(os.path.join("Assets", "Progress Bar.png")), (420, 9))

    icos = []
    r_icos = []
    glaive_icos = []
    warp_icos = []
    for i in range(0, 31):
        icos.append(
            pygame.image.load(
                os.path.join("Assets", "Dash_ico", "Dash{}.png".format(i))
            )
        )
        r_icos.append(
            pygame.image.load(
                os.path.join("Assets", "Rocket_ico", "Rocket{}.png".format(i))
            )
        )
        glaive_icos.append(
            pygame.image.load(
                os.path.join("Assets", "Glaive_ico", "Glaive{}.png".format(i))
            )
        )
        warp_icos.append(
            pygame.image.load(
                os.path.join("Assets", "Warp_ico", "Warp{}.png".format(i))
            )
        )

    warp_active_ico = pygame.image.load(os.path.join("Assets", "Warp_ico", "WarpActive.png"))

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
                    if not pause:
                        settings = False

                if event.key == pygame.K_F1:
                    ui = not ui

                if event.key == pygame.K_F5:
                    player.health = player.max_health
                    player.invulnerable = not player.invulnerable

                if event.key == pygame.K_F6:
                    spawn_enemies = not spawn_enemies
                    enemies = {}

        keys_pressed = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()

        if pause:
            if settings:

                #   settings loop

                with open(os.path.join("Settings", "reticule.json"), 'r') as file:
                    data = json.load(file)

                #   width button

                if width_button.jumpDown.is_clicked(0):
                    data["width"] -= 10
                    if data["width"] < 0:
                        data["width"] = 0

                if width_button.down.is_clicked(0):
                    data["width"] -= 1
                    if data["width"] < 0:
                        data["width"] = 0

                if width_button.up.is_clicked(0):
                    data["width"] += 1
                    if data["width"] > 100:
                        data["width"] = 100

                if width_button.jumpUp.is_clicked(0):
                    data["width"] += 10
                    if data["width"] > 100:
                        data["width"] = 100

                #   height button

                if height_button.jumpDown.is_clicked(0):
                    data["height"] -= 10
                    if data["height"] < 0:
                        data["height"] = 0

                if height_button.down.is_clicked(0):
                    data["height"] -= 1
                    if data["height"] < 0:
                        data["height"] = 0

                if height_button.up.is_clicked(0):
                    data["height"] += 1
                    if data["height"] > 100:
                        data["height"] = 100

                if height_button.jumpUp.is_clicked(0):
                    data["height"] += 10
                    if data["height"] > 100:
                        data["height"] = 100

                #   dot button

                if dot_button.jumpDown.is_clicked(0):
                    data["dot"] -= 10
                    if data["dot"] < 0:
                        data["dot"] = 0

                if dot_button.down.is_clicked(0):
                    data["dot"] -= 1
                    if data["dot"] < 0:
                        data["dot"] = 0

                if dot_button.up.is_clicked(0):
                    data["dot"] += 1
                    if data["dot"] > 100:
                        data["dot"] = 100

                if dot_button.jumpUp.is_clicked(0):
                    data["dot"] += 10
                    if data["dot"] > 100:
                        data["dot"] = 100

                #   gap button

                if gap_button.jumpDown.is_clicked(0):
                    data["gap"] -= 10
                    if data["gap"] < 0:
                        data["gap"] = 0

                if gap_button.down.is_clicked(0):
                    data["gap"] -= 1
                    if data["gap"] < 0:
                        data["gap"] = 0

                if gap_button.up.is_clicked(0):
                    data["gap"] += 1
                    if data["gap"] > 100:
                        data["gap"] = 100

                if gap_button.jumpUp.is_clicked(0):
                    data["gap"] += 10
                    if data["gap"] > 100:
                        data["gap"] = 100

                #   thickness button

                if thickness_button.jumpDown.is_clicked(0):
                    data["thickness"] -= 10
                    if data["thickness"] < 1:
                        data["thickness"] = 1

                if thickness_button.down.is_clicked(0):
                    data["thickness"] -= 1
                    if data["thickness"] < 1:
                        data["thickness"] = 1

                if thickness_button.up.is_clicked(0):
                    data["thickness"] += 1
                    if data["thickness"] > 100:
                        data["thickness"] = 100

                if thickness_button.jumpUp.is_clicked(0):
                    data["thickness"] += 10
                    if data["thickness"] > 100:
                        data["thickness"] = 100

                #   apply changes

                with open(os.path.join("Settings", "reticule.json"), 'w') as file:
                    json.dump(data, file, indent=4)

                #   back button

                if back_button.is_clicked(0):
                    reticule = ui_objects.Reticule()
                    settings = False

                else:
                    handle_cool_i(width_button, height_button, dot_button, gap_button, thickness_button)
                    handle_cool(back_button)
                    settings_display(width_button, height_button, dot_button, gap_button, thickness_button, back_button, data)
            else:

                #   pause loop

                if play_button.is_clicked(0):
                    pause = False

                if restart_button.is_clicked(0):
                    pause, player, enemies, enemy_spawn_cooldown, esc_time, num, entity_lst, sec_lst = reset()
                    ticks, phase = sec_lst[0], sec_lst[1]
                    del sec_lst
                    bullets, rockets, health_packs, glaives, shockwaves = entity_lst[0], entity_lst[1], entity_lst[2], entity_lst[3], entity_lst[4]
                    del entity_lst
                    pause = False
                    settings = False

                if settings_button.is_clicked(0):
                    settings = True

                if exit_button.is_clicked(0):
                    pygame.quit()
                    exit()

                else:
                    handle_cool(play_button, restart_button, settings_button, exit_button)
                    pause_display(play_button, restart_button, settings_button, exit_button, player)

        else:

            #   gameplay loop

            #   enemy spawn

            if spawn_enemies:
                if len(enemies) < spawn_rules["max"]:
                    if not enemy_spawn_cooldown:
                        if random.random() > 0.1:
                            enemies.update({
                                num:
                                    entities.Enemy(random.randint(30, WIDTH - 30), random.randint(30, HEIGHT - 30), 15, 0, 300, 1)
                            })
                        else:
                            enemies.update({
                                num:
                                    entities.Enemy(random.randint(30, WIDTH - 30), random.randint(30, HEIGHT - 30), 30, 30, 400, 1.2)
                            })
                        num += 1
                        enemy_spawn_cooldown = True

            #   entity handling

            handle_enemies(enemies, player, bullets, health_packs)
            pause = handle_player(player, keys_pressed, mouse_pressed, bullets, rockets, health_packs, glaives, shockwaves)
            handle_bullets(bullets, player, enemies, covers)
            handle_glaives(glaives, player, enemies)
            handle_rockets(rockets, player, enemies, bullets, covers)
            handle_shockwaves(shockwaves, enemies)
            display(player, enemies, icos, bullets, r_icos, glaive_icos, warp_icos, warp_active_ico, rockets, glaives, shockwaves, covers, attribute_bar_ico,
                    progress_bar_ico, health_packs, reticule, phase, ui, bosses)

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

            if player.kills == 0 or player.kills <= 15:
                phase = "1"
                spawn_rules = {
                    "delay": 4,
                    "max": 5,
                }
            elif 15 < player.kills <= 40:
                phase = "2"
                spawn_rules = {
                    "delay": 3,
                    "max": 10,
                }
            elif 40 < player.kills <= 60:
                phase = "3"
                spawn_rules = {
                    "delay": 2,
                    "max": 15,
                }
            elif 60 < player.kills <= 80:
                phase = "4"
                spawn_rules = {
                    "delay": 1.5,
                    "max": 20,
                }
            elif 80 < player.kills <= 100:
                phase = "5"
                spawn_rules = {
                    "delay": 0.5,
                    "max": 30,
                }
            elif player.kills >= 100:
                phase = "0"
                spawn_rules = {
                    "delay": 0,
                    "max": 0,
                }
                end_game("You won!      W")
                pause = True

            #   End of gameplay loop


if __name__ == "__main__":
    main()

#   \main.py
