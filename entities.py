#   \entities.py

import main
import math


#   Rocket class, used as an object that comes from the player and follows the mouse into enemies, which it then
#   damages. All rockets are managed by handle_rockets function.
class Rocket:
    def __init__(self, x, y, ang):
        self.x, self.y = x, y
        self.width = 50
        self.height = 102
        self.explosion_radius = 300
        self.rect = main.pygame.Rect(self.x - (self.width // 2), self.y, self.width, self.height)
        self.angle = ang
        self.vel = 1000 / main.FPS
        self.imgs = [
            main.pygame.transform.scale(main.pygame.image.load(main.os.path.join("Assets", "rocket1.png")), (self.width, self.height)),
            main.pygame.transform.scale(main.pygame.image.load(main.os.path.join("Assets", "rocket2.png")), (self.width, self.height)),
        ]
        self.img_ind = 0
        self.flame_imgs = []
        self.explode_imgs = []
        self.uptime = 0
        self.light_t = 1 * main.FPS
        self.smooth_turn = False
        self.exploding = False
        self.explode_max_time = 0.5 * main.FPS
        self.explode_time = self.explode_max_time
        self.proximity = 40
        self.proximity_time_max = 0.5 * main.FPS
        self.proximity_time = self.proximity_time_max
        self.health = 30

    def check_radius(self, target):
        distance = main.math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
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
        self.img = main.pygame.transform.scale(owner.bullet_img, (self.width, self.height))
        self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
        self.rect = self.img.get_rect(center=(owner.x, owner.y))
        self.angle = owner.angle
        self.vel = 3000 / main.FPS

        self.ricochet_cool_max = 0.02 * main.FPS
        self.ricochet_cool = self.ricochet_cool_max

        self.hit_marker = False
        self.hm_width = 11
        self.hm_height = 11
        self.hm_rect = main.pygame.Rect(self.x, self.y, self.hm_width, self.hm_height)
        self.hit_marker_time_max = 0.2 * main.FPS
        self.hit_marker_time = self.hit_marker_time_max
        self.hit_marker_img = main.pygame.transform.scale(main.pygame.image.load(main.os.path.join("Assets", "hitmarker.png")), (self.hm_width, self.hm_height))

        #   print("b", self.angle)


class HealthPack:

    def __init__(self, health, time, x, y):
        self.x, self.y = x, y
        self.health = health
        self.time = time * main.FPS
        self.width, self.height = 40, 40
        self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
        self.img = main.pygame.transform.scale(
            main.pygame.image.load(main.os.path.join("Assets", "Health pack.png")),
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
            self.img = main.pygame.transform.scale(
                main.pygame.image.load(main.os.path.join("Assets", "Enemy1.png")),  # "IMG_7363.png"  "Enemy1.png" "Th.png"
                (self.width, self.height))
        else:
            self.img = main.pygame.transform.scale(
                main.pygame.image.load(main.os.path.join("Assets", "Enemy2.png")),  # "IMG_7363.png"  "Enemy2.png" "Th.png"
                (self.width, self.height))
        self.angle = 0
        self.x = x
        self.y = y
        self.vel = speed / main.FPS
        self.x_vel = 0
        self.y_vel = 0
        self.dir = 1
        self.move_time = 0
        self.bullet_img = main.pygame.image.load(
            main.os.path.join("Assets", "Bullets", "Bullet_red.png"))
        self.aggression = aggression
        self.cooldown = ((0.8 * main.FPS) + (main.random.randint(0, 4) * main.FPS)) / self.aggression
        self.tag = "1"

    def get_vel(self, edge=0):
        div = main.random.random()
        self.x_vel = self.vel * div
        self.y_vel = self.vel - self.x_vel

        if edge == 0:
            self.dir = main.random.choice((1, 2, 3, 4))
        elif edge == 1:
            self.dir = main.random.choice((3, 4))
        elif edge == 2:
            self.dir = main.random.choice((1, 4))
        elif edge == 3:
            self.dir = main.random.choice((1, 2))
        elif edge == 4:
            self.dir = main.random.choice((2, 3))

    def shoot(self, bullets):
        self.cooldown = ((0.8 * main.FPS) + (main.random.randint(0, 2) * main.FPS)) / self.aggression
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
        self.y = (main.HEIGHT // 3) * 2
        self.x = (main.WIDTH // 2)
        self.vel = 350 / main.FPS
        self.img = main.pygame.transform.scale(
            main.pygame.image.load(main.os.path.join("Assets", "ArrowHead1.png")),
            # "fimsh-threat.png""Rizzvan.png""ArrowHead1.png""Brookiolyn.png"
            (self.width, self.height))
        self.angle = 0
        self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)    #(200, 200)
        self.dash_distance = main.WIDTH / 3
        self.cooldown = 5 * main.FPS
        self.active_cooldown = self.cooldown
        self.cooldown_f = -1
        self.ico_i = -1
        self.r_ico_i = -1
        self.r_cooldown = 10 * main.FPS
        self.r_cooldown_f = -1
        self.r_active_cooldown = self.r_cooldown
        
        self.glaive_ico_i = -1
        self.glaive_cooldown = 10 * main.FPS
        self.glaive_cooldown_f = -1
        self.glaive_active_cooldown = self.glaive_cooldown
        
        self.bullet_img = main.pygame.transform.scale(
            main.pygame.image.load(
                main.os.path.join("Assets", "Bullets", "Bullet_green.png")),
            (5, 20))
        self.max_shoot_delay = 0.2 * main.FPS
        self.shoot_time = self.max_shoot_delay
        self.max_health = 100
        self.health = self.max_health
        self.tag = "0"
        self.overheat = 0
        self.max_overheat = 150
        self.overheat_cooldown = 0
        self.shoot_cool = 0.8 * main.FPS
        self.overheat_cool = 2.4 * main.FPS
        self.cooldown_rate = 30 / main.FPS
        self.kills = 0
        self.collected_health_packs = []
        self.warps = []

        self.warp_ico_i = -1
        self.warp_cooldown = 15 * main.FPS
        self.warp_cooldown_f = -1
        self.warp_active_cooldown = self.warp_cooldown

        self.facing_right = True
        self.invulnerable = False

        #   zoom will make the player move faster in the direction they are facing,
        #   and will grant them 30% damage resistance, but it is limited, and they
        #   will not be able to do anything else.
        self.zoom = False
        self.zoom_vel = 800 / main.FPS
        self.zoom_damage_res = 0.3

        self.zoom_max = 500
        self.zoom_current = self.zoom_max
        self.zoom_cooldown = 0
        self.zoom_cool = 2.4 * main.FPS
        self.zoom_cooldown_rate = 20 / main.FPS

    def dash(self, x, y):  # dash in the direction of the mouse
        a = abs(self.x - x)
        b = abs(self.y - y)

        c = main.math.sqrt(pow(a, 2) + pow(b, 2))

        mult = self.dash_distance / c

        if mult > 1:
            mult = 1

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
        elif self.x >= main.WIDTH:
            self.x = main.WIDTH - 1
        if self.y <= 0:
            self.y = 1
        elif self.y >= main.HEIGHT:
            self.y = main.HEIGHT - 1

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
        if not self.invulnerable:
            self.health -= (dam * self.zoom_damage_res)
            if self.health < 0:
                self.health = 0

    def heal(self, dam):
        self.health += dam
        if self.health > self.max_health:
            self.health = self.max_health

    def glaive(self):
        return Glaive(self)

    def place_warp(self):
        return Warp(self)

    def activate_warp(self, warp):
        self.x = (warp.x - (warp.width / 2)) + (self.width / 2)
        self.y = (warp.y - (warp.height / 2)) + (self.height / 2)
        return warp.detonate(self)


class Warp:

    def __init__(self, player):
        self.x = player.x - (player.width / 2)
        self.y = player.y - (player.height / 2)
        self.cast_time = 1 * main.FPS
        self.width = 80
        self.height = 80
        self.rect = main.pygame.Rect(self.x, self.y, self.width, self.height)
        self.img = main.pygame.transform.scale(main.pygame.image.load(main.os.path.join("Assets", "warp-point.png")), (self.width, self.height))

    def detonate(self, player):
        player.warps = []
        player.warp_active_cooldown = 0
        player.warp_cooldown_f = 0
        player.warp_ico_i = 0
        return Shockwave(self)


class Shockwave:
    def __init__(self, warp):
        self.x = warp.x + (warp.width / 2)
        self.y = warp.y + (warp.height / 2)
        self.radius = 100
        self.thickness = 1
        self.expand_speed = 600 / main.FPS
        self.thicken_speed = 20 / main.FPS
        self.damage_list = []
        self.damage = 1.25
        self.a = 5
        self.b = -0.25
        self.c = -2

        #   n = ax^2 + bx + c


class Glaive:

    #   glaives will spin around the player, dealing damage to enemies that come in contact with them,
    #   and healing the player for the same amount.
    def __init__(self, player):
        self.glaive_prints = []
        self.x = player.x
        self.y = player.y
        self.width = 36
        self.height = 44
        self.vel = 5 / main.FPS
        self.arc = 120
        self.cast_time = 30 * main.FPS
        self.turn_per_frame = self.arc / self.cast_time
        self.display_angle = 0
        self.turn = 12
        self.initial_offset = math.radians(60)
        self.radius = 180
        self.angle = -player.angle + self.initial_offset
        self.length = math.pi * 40
        self.img = main.pygame.transform.scale(main.pygame.image.load(main.os.path.join("Assets", "glaive.png")), (self.width, self.height))
        self.rotated_img = self.img
        self.rect = self.img.get_rect(center=(player.x, player.y))
        self.damage = 20
        self.rotate_speed = -3000 / main.FPS
        self.display_angle = self.angle
        self.uptime = 0
        self.max_uptime = 40 * main.FPS
        #   self.y += 40


class Cover:

    class Segment:
        def __init__(self, a, b):
            self.ax = a[0]
            self.ay = a[-1]
            self.bx = b[0]
            self.by = b[-1]

    def __init__(self, type, position_list, transform=(0, 0)):
        self.type = type

        self.position_list = []
        for position in position_list:
            pos_x, pos_y = position
            pos_x += transform[0]
            pos_y += transform[-1]
            self.position_list.append((pos_x, pos_y))

        self.segments = []
        for i in range(len(self.position_list) - 1):
            self.segments.append(self.Segment(self.position_list[i], self.position_list[i+1]))

        if self.type == "wall":
            self.colour = main.COLOURS["light_grey"]
        elif self.type == "shield":
            self.colour = main.COLOURS["blue"]
        elif self.type == "ricochet":
            self.colour = main.COLOURS["red"]
        self.thickness = 5


class Boss:

    def __init__(self):
        self.x = main.WIDTH//2
        self.y = main.HEIGHT//2
        self.width = 400
        self.height = 400
        self.base_rect = main.pygame.Rect(self.x - (self.width / 2), self.y - (self.height / 2), self.width, self.height)
        self.surface = main.pygame.Surface((self.width, self.height))
        self.angle = 0
        self.rotated = main.pygame.transform.rotate(self.surface, self.angle)
        self.rect = self.rotated.get_rect(center=self.base_rect.center)

        self.surface.fill(main.COLOURS["red"])

#   \entities.py
