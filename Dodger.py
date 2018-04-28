import pygame
from random import randint
from dodger_sprite import DodgerSprite
from game_timer import GameTimer
from surface_manager import SurfaceManager
from group_manager import GroupManager


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

# build surface cache and populate it
surface_cache = SurfaceManager()
surface_cache.build("enemy_small", ENEMY_SMALL_SIZE, ENEMY_SMALL_SIZE, color_baddie)
surface_cache.build("enemy_medium", ENEMY_MEDIUM_SIZE, ENEMY_MEDIUM_SIZE, color_baddie)
surface_cache.build("enemy_large", ENEMY_LARGE_SIZE, ENEMY_LARGE_SIZE, color_baddie)
surface_cache.build("player", PLAYER_SIZE, PLAYER_SIZE, color_player)
surface_cache.build("projectile", PROJECTILE_SIZE, PROJECTILE_SIZE, color_pewpew_projectile)
surface_cache.build("pu_projectile", POWER_UP_SIZE, POWER_UP_SIZE, color_pewpew_power_up)
surface_cache.build("pu_repeal", POWER_UP_SIZE, POWER_UP_SIZE, color_repeal_power_up)
surface_cache.build("pu_doomsday", POWER_UP_SIZE, POWER_UP_SIZE, color_doomsday_power_up)

# build our group manager
group_manager = GroupManager()
group_manager.add_group('enemy')
group_manager.add_group('player')
group_manager.add_group('power_up')
group_manager.add_group('projectile')
group_manager.add_group('gui')

top_banner = pygame.sprite.Sprite()
top_banner.image = pygame.Surface([SCREEN_WIDTH, 100])
top_banner.image.fill([255, 255, 255])
top_banner.rect = top_banner.image.get_rect()
top_banner.rect.x = 0
top_banner.rect.y = 0
group_manager.insert('gui', top_banner)

gui_font = pygame.font.Font(None, 24)

player = DodgerSprite(SCREEN_WIDTH // 2 + PLAYER_SIZE, SCREEN_HEIGHT - (PLAYER_SIZE * 5),
                      surface_cache.get_surface('player'))
group_manager.insert('player', player)


def group_updates(dt):
    global PLAYER_SCORE
    global player
    # check if we killed anything first
    # this needs some adjustment cuz we can't track how many enemies died... oh wait
    killed = 0
    alive_before = group_manager.count('enemy')
    pygame.sprite.groupcollide(group_manager.get_raw_group('projectile'), group_manager.get_raw_group('enemy'), True,
                               True)
    killed = alive_before - group_manager.count('enemy')
    PLAYER_SCORE += killed
    for sprite in group_manager.get_sprites('projectile'):
        sprite.move(0, -PROJECTILE_SPEED * dt)
        if sprite.rect.y < 0 or sprite.rect.y > SCREEN_HEIGHT:
            sprite.kill()
    for sprite in group_manager.get_sprites('enemy'):
        sprite.move(0, BADDIE_SPEED * dt)
        if sprite.rect.y < 0 or sprite.rect.y > SCREEN_HEIGHT:
            sprite.kill()
    collisions = pygame.sprite.spritecollideany(player, group_manager.get_raw_group('enemy'))
    if collisions is not None:
        collisions.kill()
        PLAYER_SCORE -= 1
        player.kill()
        player = DodgerSprite(SCREEN_WIDTH // 2 + PLAYER_SIZE, SCREEN_HEIGHT - (PLAYER_SIZE * 5),
                              surface_cache.get_surface('player'))
        group_manager.insert('player', player)


def spawn_projectile():
    # projectile offset is player rect X - 1/2 player size, player Y + projectile size
    px = player.rect.x + ((PLAYER_SIZE // 2) - (PROJECTILE_SIZE // 2))
    py = player.rect.y
    spawn_at(px, py, surface_cache.get_surface("projectile"), 'projectile')


def spawn_random_baddie():
    rx = randint(0, SCREEN_WIDTH - ENEMY_LARGE_SIZE)
    size = randint(0, 3)
    baddie_size = "enemy_small"
    if size == 1:
        baddie_size = "enemy_medium"
    if size == 2:
        baddie_size = "enemy_large"
    spawn_at(rx, 0, surface_cache.get_surface(baddie_size), 'enemy')


def spawn_at(x, y, surface, group):
    s = DodgerSprite(x, y, surface)
    group_manager.insert(group, s)


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
        spawn_at(randint(100, 700), randint(100, 500), surface_cache.get_surface('pu_projectile'), "power_up")
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
    group_manager.draw(display)
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
