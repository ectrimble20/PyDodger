import pygame
from random import randint
from dodger_sprite import DodgerSprite
from game_timer import GameTimer


# General settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
resolution = SCREEN_WIDTH, SCREEN_HEIGHT
color_background = (0, 0, 0)
color_player = (255, 255, 255)
color_baddie = (0, 255, 0)
color_pewpew_power_up = (0, 0, 255)
color_pewpew_projectile = (99, 99, 99)
color_repeal_power_up = (255, 0, 0)
color_doomsday_power_up = (255, 255, 0)

#game timer stuff
timer = GameTimer(0)

# counts and things
MAX_ENEMIES_ON_SCREEN = 30
ENEMY_SMALL_SIZE = 8
ENEMY_MEDIUM_SIZE = 16
ENEMY_LARGE_SIZE = 32
PLAYER_SIZE = 16
POWER_UP_SIZE = 8
PROJECTILE_SIZE = 4
PLAYER_SCORE = 0

# speed settings
PROJECTILE_SPEED = 200
BADDIE_SPEED = 75
PLAYER_SPEED = 150

# init pygame stuff
pygame.init()
pygame.font.init()
display = pygame.display.set_mode(resolution)
pygame.key.set_repeat(50, 50)


# build and cache surfaces
cached_surfaces = {}
cached_surfaces["enemy_small"] = pygame.Surface([ENEMY_SMALL_SIZE, ENEMY_SMALL_SIZE])
cached_surfaces["enemy_small"].fill(color_baddie)
cached_surfaces["enemy_medium"] = pygame.Surface([ENEMY_MEDIUM_SIZE, ENEMY_MEDIUM_SIZE])
cached_surfaces["enemy_medium"].fill(color_baddie)
cached_surfaces["enemy_large"] = pygame.Surface([ENEMY_LARGE_SIZE, ENEMY_LARGE_SIZE])
cached_surfaces["enemy_large"].fill(color_baddie)
cached_surfaces["player"] = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
cached_surfaces["player"].fill(color_player)
cached_surfaces["projectile"] = pygame.Surface([PROJECTILE_SIZE, PROJECTILE_SIZE])
cached_surfaces["projectile"].fill(color_pewpew_projectile)
cached_surfaces["pu_projectile"] = pygame.Surface([POWER_UP_SIZE, POWER_UP_SIZE])
cached_surfaces["pu_projectile"].fill(color_pewpew_power_up)
cached_surfaces["pu_repeal"] = pygame.Surface([POWER_UP_SIZE, POWER_UP_SIZE])
cached_surfaces["pu_repeal"].fill(color_repeal_power_up)
cached_surfaces["pu_doomsday"] = pygame.Surface([POWER_UP_SIZE, POWER_UP_SIZE])
cached_surfaces["pu_doomsday"].fill(color_doomsday_power_up)

# Define our groups
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
power_up_group = pygame.sprite.Group()
pewpew_group = pygame.sprite.Group()
top_gui_group = pygame.sprite.Group()

top_banner = pygame.sprite.Sprite()
top_banner.image = pygame.Surface([SCREEN_WIDTH, 100])
top_banner.image.fill([255, 255, 255])
top_banner.rect = top_banner.image.get_rect()
top_banner.rect.x = 0
top_banner.rect.y = 0
top_gui_group.add(top_banner)

gui_font = pygame.font.Font(None, 24)

player = DodgerSprite(SCREEN_WIDTH // 2 + PLAYER_SIZE, SCREEN_HEIGHT - (PLAYER_SIZE * 5), cached_surfaces['player'])
player_group.add(player)


def group_updates(dt):
    global PLAYER_SCORE
    global player
    # check if we killed anything first
    # this needs some adjustment cuz we can't track how many enemies died... oh wait
    killed = 0
    alive_before = len(enemy_group.sprites())
    pygame.sprite.groupcollide(pewpew_group, enemy_group, True, True)
    killed = alive_before - len(enemy_group.sprites())
    PLAYER_SCORE += killed
    for sprite in pewpew_group.sprites():
        sprite.move(0, -PROJECTILE_SPEED * dt)
        if sprite.rect.y < 0 or sprite.rect.y > SCREEN_HEIGHT:
            pewpew_group.remove(sprite)
            sprite.kill()
    for sprite in enemy_group.sprites():
        sprite.move(0, BADDIE_SPEED * dt)
        if sprite.rect.y < 0 or sprite.rect.y > SCREEN_HEIGHT:
            enemy_group.remove(sprite)
            sprite.kill()
    collisions = pygame.sprite.spritecollideany(player, enemy_group)
    if collisions is not None:
        collisions.kill()
        PLAYER_SCORE -= 1
        player.kill()
        player = DodgerSprite(SCREEN_WIDTH // 2 + PLAYER_SIZE, SCREEN_HEIGHT - (PLAYER_SIZE * 5),
                              cached_surfaces['player'])
        player_group.add(player)


def spawn_projectile():
    # projectile offset is player rect X - 1/2 player size, player Y + projectile size
    px = player.rect.x + ((PLAYER_SIZE // 2) - (PROJECTILE_SIZE // 2))
    py = player.rect.y
    spawn_at(px, py, cached_surfaces["projectile"], pewpew_group)


def spawn_random_baddie():
    rx = randint(0, SCREEN_WIDTH - ENEMY_LARGE_SIZE)
    size = randint(0, 3)
    baddie_size = "enemy_small"
    if size == 1:
        baddie_size = "enemy_medium"
    if size == 2:
        baddie_size = "enemy_large"
    spawn_at(rx, 0, cached_surfaces[baddie_size], enemy_group)


def spawn_at(x, y, surface, group):
    s = DodgerSprite(x, y, surface)
    group.add(s)


def check_keyboard_user_input(dt):
    global PLAYER_SPEED
    if pygame.key.get_focused():
        x_off = 0
        y_off = 0
        adjusted = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            y_off -= PLAYER_SPEED * dt
            adjusted = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x_off -= PLAYER_SPEED * dt
            adjusted = True
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            y_off += PLAYER_SPEED * dt
            adjusted = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x_off += PLAYER_SPEED * dt
            adjusted = True
        if keys[pygame.K_PLUS] or keys[pygame.K_KP_PLUS]:
            PLAYER_SPEED += 1
        if keys[pygame.K_MINUS] or keys[pygame.K_KP_MINUS]:
            PLAYER_SPEED -= 1
        # I'm only interested in adjustment if something changed
        if adjusted:
            player.move(x_off, y_off)
            player.clamp(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


clock = pygame.time.Clock()
delta_time = 0  # initialize to 0

game_running = True
for _ in range(0, 5):
    spawn_random_baddie()

game_timer = 0
wave_spawn_clock = 0
spawn_wave_every = 2
power_up_spawn = randint(10, 40)
power_up_spawn_clock = 0

timer.add_timer('wave_spawn')
timer.add_timer('power_up_spawn')


while game_running:
    # process user input
    player_debug = "X: {} Y: {} SCORE: {}".format(player.rect.x, player.rect.y, PLAYER_SCORE)
    pygame.display.set_caption(player_debug)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game_running = False
            break
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                spawn_projectile()
    if timer.get_time('power_up_spawn') > power_up_spawn:
        power_up_spawn = randint(10, 40)
        timer.set_timer_to_zero('power_up_spawn')
        spawn_at(randint(100, 700), randint(100, 500), cached_surfaces["pu_projectile"], power_up_group)
    if timer.get_time('wave_spawn') > spawn_wave_every:
        for _ in range(0, randint(5, 20)):
            spawn_random_baddie()
        timer.set_timer_to_zero('wave_spawn')
        spawn_wave_every = randint(1, 3)
    check_keyboard_user_input(delta_time)
    group_updates(delta_time)
    # do logic
    # 1: update positions
    # 2: check for deadly collisions
    # 3: update score
    # 4: update text
    # repeat
    display.fill(color_background)
    enemy_group.draw(display)
    player_group.draw(display)
    power_up_group.draw(display)
    pewpew_group.draw(display)
    top_gui_group.draw(display)
    # draw score text
    render = gui_font.render("Score: {}".format(PLAYER_SCORE), 0, (0, 0, 0), (255, 255, 255))
    display.blit(render, (20, 20))

    pygame.event.pump()
    pygame.display.update()
    delta_time = clock.tick(60) / 1000
    game_timer += delta_time
    timer.update(delta_time)
pygame.quit()
quit()
