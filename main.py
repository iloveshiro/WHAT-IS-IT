import json

import pygame as pg
import pytmx

pg.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 80

TILE_SCALE = 1.5

font = pg.font.Font(None, 75)


class Platform(pg.sprite.Sprite):
    def __init__(self, img, x, y, w, h):
        super(Platform, self).__init__()

        self.image = pg.transform.scale(img, (w * TILE_SCALE, h * TILE_SCALE))
        self.rect = self.image.get_rect(x=x * TILE_SCALE, y=y * TILE_SCALE)


class Player(pg.sprite.Sprite):
    def __init__(self, map_width, map_height):
        super(Player, self).__init__()

        self.load_animation()

        self.current_a = self.idle_animation_r
        self.image = self.current_a[0]
        self.current_i = 0

        self.rect = self.image.get_rect()
        self.rect.center = (200, 100)  # Начальное положение персонажа

        self.timer = pg.time.get_ticks()
        self.interval = 225

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width
        self.map_height = map_height

        self.hp = 10
        self.damage_timer = pg.time.get_ticks()
        self.damage_interval = 1000

    def load_animation(self):
        tile_size = 32
        tile_scale = 4

        self.idle_animation_r = []

        img_num = 5

        spritesheet = pg.image.load("sprites/the witch n the beast/2 - Lil Wiz/Idle_(32 x 32).png")

        for i in range(img_num):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            img = spritesheet.subsurface(rect)
            img = pg.transform.scale(img, (tile_scale * tile_size, tile_scale * tile_size))
            self.idle_animation_r.append(img)

        self.idle_animation_l = [pg.transform.flip(i, True, False) for i in self.idle_animation_r]

        self.run_animation_r = []

        img_num = 6

        spritesheet = pg.image.load("sprites/the witch n the beast/2 - Lil Wiz/Running_(32 x 32).png")

        for i in range(img_num):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            img = spritesheet.subsurface(rect)
            img = pg.transform.scale(img, (tile_scale * tile_size, tile_scale * tile_size))
            self.run_animation_r.append(img)

        self.run_animation_l = [pg.transform.flip(i, True, False) for i in self.run_animation_r]

    def get_dmg(self):
        if pg.time.get_ticks() - self.damage_timer > self.damage_interval:
            self.hp -= 1
            self.damage_timer = pg.time.get_ticks()

    def update(self, platforms):
        keys = pg.key.get_pressed()

        if keys[pg.K_SPACE] and not self.is_jumping:
            self.jump()

        if keys[pg.K_d]:
            if self.current_a != self.run_animation_r:
                self.current_a = self.run_animation_r
                self.current_i = 0
            self.velocity_x = 10
        elif keys[pg.K_a]:
            if self.current_a != self.run_animation_l:
                self.current_a = self.run_animation_l
                self.current_i = 0
            self.velocity_x = -10

        else:
            if self.current_a == self.run_animation_r:
                self.current_a = self.idle_animation_r
                self.current_i = 0
            if self.current_a == self.run_animation_l:
                self.current_a = self.idle_animation_l
                self.current_i = 0
            self.velocity_x = 0

        new_x = self.rect.x + self.velocity_x
        if new_x <= self.map_width - self.rect.width + 40:
            self.rect.x = -40 if not new_x >= -40 else new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_i += 1
            if self.current_i >= len(self.current_a):
                self.current_i = 0

            self.image = self.current_a[self.current_i]
            self.timer = pg.time.get_ticks()

    def jump(self):
        self.velocity_y = -25
        self.is_jumping = True


class Pumpkin(pg.sprite.Sprite):    # pumpkin(enemy)
    def __init__(self, map_width, map_height, start, end):
        super(Pumpkin, self).__init__()

        self.direction = 'r'

        self.load_animation()
        self.current_a = self.animation_r
        self.image = self.current_a[0]
        self.current_i = 0

        self.rect = self.image.get_rect()
        self.r_edge = start[0]
        self.l_edge = end[0] + self.image.get_width()
        self.rect.bottomleft = start

        self.timer = pg.time.get_ticks()
        self.interval = 225

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width
        self.map_height = map_height

    def load_animation(self):
        tile_scale = 3
        tile_size = 16

        self.animation_r = []

        spritesheet = pg.image.load("sprites/living food/4 - Robo Pumpkin/Walking (16 x 16).png")
        img_num = 2

        for i in range(img_num):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            img = spritesheet.subsurface(rect)
            img = pg.transform.scale(img, (tile_scale * tile_size, tile_scale * tile_size))
            self.animation_r.append(img)

        self.animation_l = [pg.transform.flip(i, True, False) for i in self.animation_r]

    def update(self, platforms):
        if self.direction == 'r':
            self.velocity_x = 10
            if self.rect.right <= self.r_edge:
                self.direction = 'l'
        if self.direction == 'l':
            self.velocity_x = -10
            if self.rect.left >= self.l_edge:
                self.direction = 'r'

        if self.direction == 'l':
            self.current_a = self.animation_l
        elif self.direction == 'r':
            self.current_a = self.animation_r

        new_x = self.rect.x + self.velocity_x
        if new_x <= self.map_width - self.rect.width:
            self.rect.x = 0 if not new_x >= 0 else new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:
            if pg.sprite.collide_mask(self, platform):
                if self.velocity_y > 0:
                    self.rect.y = platform.rect.y - self.rect.height
                    self.velocity_y = 0
                elif self.velocity_y < 0:
                    self.rect.y = platform.rect.y + platform.rect.height
                    self.velocity_y = 0

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_i += 1
            if self.current_i >= len(self.current_a):
                self.current_i = 0

            self.image = self.current_a[self.current_i]
            self.timer = pg.time.get_ticks()


class Mochi(pg.sprite.Sprite):  # mochi(enemy)
    def __init__(self, map_width, map_height, start, end):
        super(Mochi, self).__init__()

        self.direction = 'r'

        self.load_animation()
        self.current_a = self.animation_r
        self.image = self.current_a[0]
        self.current_i = 0

        self.rect = self.image.get_rect()
        self.r_edge = start[0]
        self.l_edge = end[0] + self.image.get_width()
        self.rect.bottomleft = start

        self.timer = pg.time.get_ticks()
        self.interval = 225

        # Начальная скорость и гравитация
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 2
        self.is_jumping = False
        self.map_width = map_width
        self.map_height = map_height

    def load_animation(self):
        tile_scale = 3
        tile_size = 32

        self.animation_r = []

        spritesheet = pg.image.load("sprites/living food/2 - Mr. Mochi/Running (32 x 32).png")
        img_num = 4

        for i in range(img_num):
            x = i * tile_size
            y = 0
            rect = pg.Rect(x, y, tile_size, tile_size)
            img = spritesheet.subsurface(rect)
            img = pg.transform.scale(img, (tile_scale * tile_size, tile_scale * tile_size))
            self.animation_r.append(img)

        self.animation_l = [pg.transform.flip(i, True, False) for i in self.animation_r]

    def update(self, platforms):
        if self.direction == 'r':
            self.velocity_x = 10
            if self.rect.right <= self.r_edge:
                self.direction = 'l'
        if self.direction == 'l':
            self.velocity_x = -10
            if self.rect.left >= self.l_edge:
                self.direction = 'r'

        if self.direction == 'l':
            self.current_a = self.animation_l
        elif self.direction == 'r':
            self.current_a = self.animation_r

        new_x = self.rect.x + self.velocity_x
        if new_x <= self.map_width - self.rect.width:
            self.rect.x = 0 if not new_x >= 0 else new_x

        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        for platform in platforms:
            if platform.rect.collidepoint(self.rect.midright):
                self.rect.right = platform.rect.left
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midleft):
                self.rect.left = platform.rect.right
                self.velocity_x = 0

            if platform.rect.collidepoint(self.rect.midbottom):
                self.rect.bottom = platform.rect.top
                self.velocity_y = 0
                self.is_jumping = False

            if platform.rect.collidepoint(self.rect.midtop):
                self.rect.top = platform.rect.bottom
                self.velocity_y = 0

        if pg.time.get_ticks() - self.timer > self.interval:
            self.current_i += 1
            if self.current_i >= len(self.current_a):
                self.current_i = 0

            self.image = self.current_a[self.current_i]
            self.timer = pg.time.get_ticks()


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Платформер")

        self.setup()

    # noinspection PyAttributeOutsideInit

    def setup(self):
        self.mode = 'game'
        self.clock = pg.time.Clock()
        self.is_running = False

        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()
        self.enemies = pg.sprite.Group()

        # self.map_tmx = pytmx.load_pygame('maps/swamp map 1.tmx')
        self.map_tmx = pytmx.load_pygame('maps/swamp/swamp lvl 1.tmx')
        # self.map_tmx = pytmx.load_pygame('maps/swamp_tiles.tsx')

        self.map_p_w = self.map_tmx.width * self.map_tmx.tilewidth * TILE_SCALE
        self.map_p_h = self.map_tmx.height * self.map_tmx.tileheight * TILE_SCALE

        self.player = Player(self.map_p_w, self.map_p_h)
        self.all_sprites.add(self.player)

        with open('maps/swamp/lvl1_enemies_location.json', 'r') as f:
            data = json.load(f)
            for enemy in data['enemies']:
                if enemy['name'] == "Mochi":
                    x1 = enemy['start'][0] * TILE_SCALE * self.map_tmx.tilewidth
                    x2 = enemy['end'][0] * TILE_SCALE * self.map_tmx.tilewidth
                    y1 = enemy['start'][1] * TILE_SCALE * self.map_tmx.tilewidth
                    y2 = enemy['end'][1] * TILE_SCALE * self.map_tmx.tilewidth
                    mochi = Mochi(self.map_p_w, self.map_p_h, [x1, y1], [x2, y2])
                    self.all_sprites.add(mochi)
                    self.enemies.add(mochi)
                elif enemy['name'] == "Pumpkin":
                    x1 = enemy['start'][0] * TILE_SCALE * self.map_tmx.tilewidth
                    x2 = enemy['end'][0] * TILE_SCALE * self.map_tmx.tilewidth
                    y1 = enemy['start'][1] * TILE_SCALE * self.map_tmx.tilewidth
                    y2 = enemy['end'][1] * TILE_SCALE * self.map_tmx.tilewidth
                    pumpkin = Pumpkin(self.map_p_w, self.map_p_h, [x1, y1], [x2, y2])
                    self.all_sprites.add(pumpkin)
                    self.enemies.add(pumpkin)

        for layer in self.map_tmx:
            for x, y, gid in layer:
                tile = self.map_tmx.get_tile_image_by_gid(gid)

                if tile:
                    platform = Platform(tile,
                                        x * self.map_tmx.tilewidth,
                                        y * self.map_tmx.tileheight,
                                        self.map_tmx.tilewidth,
                                        self.map_tmx.tileheight
                                        )
                    self.all_sprites.add(platform)
                    self.platforms.add(platform)

        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 4

        self.run()

    def run(self):
        self.is_running = True
        while self.is_running:
            self.event()
            self.update()
            self.draw()
            self.clock.tick(60)
        pg.quit()
        quit()

    def event(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False
            if self.mode == 'gameover':
                if event.type == pg.KEYDOWN:
                    self.setup()


        keys = pg.key.get_pressed()

        # if keys[pg.K_LEFT]:
        #     self.camera_x += self.camera_speed
        # if keys[pg.K_RIGHT]:
        #     self.camera_x -= self.camera_speed
        # if keys[pg.K_UP]:
        #     self.camera_y += self.camera_speed
        # if keys[pg.K_DOWN]:
        #     self.camera_y -= self.camera_speed

    def update(self):
        if self.player.hp <= 0:
            self.mode = 'gameover'

        for enemy in self.enemies.sprites():

            if pg.sprite.collide_mask(self.player, enemy):
                self.player.get_dmg()

        self.player.update(self.platforms)
        for enemy in self.enemies.sprites():
            enemy.update(self.platforms)

        self.camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_y = self.player.rect.centery - SCREEN_WIDTH // 2

        self.camera_x = max(0, min(self.camera_x, self.map_p_w - SCREEN_WIDTH))
        self.camera_y = max(0, min(self.camera_y, self.map_p_h - SCREEN_HEIGHT))

    def draw(self):
        self.screen.fill((255, 255, 255))

        # self.all_sprites.draw(self.screen)

        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, sprite.rect.move(-self.camera_x, -self.camera_y))

        pg.draw.rect(self.screen, pg.Color("red"), (SCREEN_WIDTH - self.player.hp * 10 - 10, 10, self.player.hp * 10, 20))
        pg.draw.rect(self.screen, pg.Color("black"), (SCREEN_WIDTH - 100 - 10, 10, 100, 20), 1)

        if self.mode == 'gameover':
            text = font.render('Вы погибли.', True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

        pg.display.flip()


if __name__ == "__main__":
    game = Game()
