"""Level data and the loader that turns a text map into game objects.

Each level is a dict with:
  - "background": background image filename (from assets/Background/)
  - "name": display name of the level
  - "map": a list of equal-length strings, read top-to-bottom, left-to-right.
           Each character is one BLOCK_SIZE grid cell:
             '.'  empty space
             '#'  solid block
             'F'  fire trap (starts on)
             'S'  player spawn point (exactly one per level)
             'G'  goal / end-of-level flag
             'K'  spike (ground spikes)
             'V'  saw (stationary)
             'v'  saw (moving horizontally)
             'T'  trampoline
             'M'  moving platform (horizontal)
             'P'  moving platform (vertical)
             'A'  fruit — Apple
             'B'  fruit — Bananas
             'C'  fruit — Cherries
             'W'  arrow (flies right, resets)
             'D'  falling platform
             'N'  fan (wind push upward)
             'R'  rock head (horizontal crusher)
             'r'  rock head (vertical crusher)
             'H'  spike head (horizontal crusher)
             'h'  spike head (vertical crusher)
             'O'  spiked ball (static hazard)

"""

from objects import (
    Block, Fire, Goal, Spike, Saw, Trampoline, MovingPlatform, Fruit,
    Arrow, FallingPlatform, Fan, RockHead, SpikeHead, SpikedBall,
)
from settings import BLOCK_SIZE


LEVELS = [
    {
        "background": "Blue.png",
        "name": "Moving Platforms 101",
        "map": [
            "................................",
            "................................",
            "..............................G.",
            "...........................#####",
            "................A.......P..#####",
            ".........####.......M......#####",
            "..S...###............KKKKKK#####",
            "################################",
        ],
    },
    {
        "background": "Pink.png",
        "name": "Mechanics 101",
        "map": [
            "................................",
            "..............................G.",
            "...........................#####",
            ".........................#F#####",
            "...........A...........#########",
            ".......B...#..........T#########",
            "..S....#...#.....K....##########",
            "################################",
        ],
    },

    {
        "background": "Blue.png",
        "name": "The Crossroads",
        "map": [
            "..............................G.",
            "............................####",
            "..........B...AAA....C......#...",
            "..........D...MMM....D......#...",
            "........#...................#...",
            "..S...K.#......v.......K.T..#...",
            "#########...########...#########",
        ],
    },

    {
        "background": "Green.png",
        "name": "Meadow Trail",
        "map": [
            "......................................................",
            "......................................................",
            "......................................................",
            ".......W..................A...............V...........",
            ".S........C...V.........r...r..............C........G.",
            "####..D..D..###..T....F........F..T....###..M..M..####",
            "####KKKKKKKK###KK#KKKK##########KK#KKKK###KKKKKKKK####",
        ],
    },
  
    {
        "background": "Blue.png",
        "name": "Spike Valley",
        "map": [
           "......................................................",
            "......................................................",
            "............W......h.....v...........W......v.........",
            "......C....................h....................A.....",
            ".S..................................................G.",
            "####..NN..####..D..D..D..###...D...D....##..M..M..####",
            "####KKKKKK####KKKKKKKKKKK###KKKKKKKKK###KKKKKKKKKK####",
        ],
    },
    {
        "background": "Yellow.png",
        "name": "Sawmill Heights",
        "map": [
            "........................................................",
            "........................................................",
            ".................A....................C.................",
            "..............H.###....V.....B.......###................",
            ".S....................###...###...........V...V......G..",
            "####.......T......................V......D..D...D..#####",
            ".......#########.................####...................",
        ],
    },

    {
        "background": "Pink.png",
        "name": "Wind Fortress",
        "map": [
            "....................................................................................................",
            "....................................................................................................",
            ".......................................r..r...................................h..h..................",
            "....W...........................................W.......................O...............W...........",
            ".S....C...........v............H........B...........A.......C........V.........A.................G..",
            "###..D..D..###..T....###..F..M....###..P..P..###..T....###..N..###..M....###..D..D..###..F..###..###",
            "###KKKKKKKK###KK#KKKK###KK#KKKKKKK###KKKKKKKK###KK#KKKK###KK#KK###KKKKKKK###KKKKKKKK###KK#KK###KK###",
            "####################################################################################################",
        ],
    },

    {
        "background": "Brown.png",
        "name": "Crusher Caverns",
        "map": [
            "....................................................................................................",
            "....................................................................................................",
            ".................r..................h........B..................r......h............................",
            "....W..............H........v.........W..........H..........v.....................W.................",
            ".S...........C........V.........A..........F........B..............O........C..........A.....G......",
            "####..D..D..###..M...###..T....###..D..D..###..N...###..T....T....###..M...###..D..D..###..####.....",
            "####KKKKKKKK###KKKKKK###KK#KKKK###KKKKKKKK###KK#KKK###KK#KKKK#KKKK###KKKKKK###KKKKKKKK###KK####.....",
            "####################################################################################################",
        ],
    },

    {
        "background": "Gray.png",
        "name": "Spike Head Gauntlet",
        "map": [
            "....................................................................................................",
            "....................................................................................................",
            ".........r...............h....................r.............................h.......................",
            "........W............B..........................W..........................O...W....................",
            ".S...........C.......................v.......A....................B.................C..........V..G.",
            "###..F..###..P..###..N..###..T....###..M..M..###..D..D..###..T....###..P..###..D..D..###..F..###..##",
            "###KK#KK###KKKKK###KK#KK###KK#KKKK###KKKKKKKK###KKKKKKKK###KK#KKKK###KKKKK###KKKKKKKK###KK#KK### KK##",
            "####################################################################################################",
        ],
    },

    {
        "background": "Purple.png",
        "name": "The Inferno",
        "map": [
            ".................................................................................",
            ".................................................................................",
            ".........h...r........A.........h............r..........B........h..........C....",
            "..................#####.......#####.........#####......####.........#####........",
            "..........W...v........H..........W...v.........H...........W...v..........G.....",
            ".S......D..D...F....P......O..D..D...F....P.......O..D..D...F....P....##..####...",
            "####.KKK.....####.......KKKKK.......####......KKKKK.......####...................",
            "..N.......N...............N.......N..............N.........N.....................",
        ],
    },
]


def load_level(index):

    level = LEVELS[index]
    grid = level["map"]

    objects = []
    fires = []
    goal = None
    player_start = (100, 100)  # fallback if no 'S' found

    for row_idx, row in enumerate(grid):
        for col_idx, char in enumerate(row):
            x = col_idx * BLOCK_SIZE
            y = row_idx * BLOCK_SIZE

            if char == "#":
                objects.append(Block(x, y, BLOCK_SIZE))

            elif char == "F":
                fire_w, fire_h = 32, 64
                fire_x = x + (BLOCK_SIZE - fire_w) // 2
                fire_y = y + BLOCK_SIZE - fire_h
                fire = Fire(fire_x, fire_y, 16, 32)
                fire.on()
                objects.append(fire)
                fires.append(fire)

            elif char == "K":
                spike_w, spike_h = BLOCK_SIZE, 32
                spike_x = x
                spike_y = y + BLOCK_SIZE - spike_h
                objects.append(Spike(spike_x, spike_y, spike_w, spike_h))

            elif char == "V":
                saw_w, saw_h = 64, 64
                saw_x = x + (BLOCK_SIZE - saw_w) // 2
                saw_y = y + (BLOCK_SIZE - saw_h) // 2
                objects.append(Saw(saw_x, saw_y, saw_w, saw_h, move_range=0))

            elif char == "v":
                saw_w, saw_h = 64, 64
                saw_x = x + (BLOCK_SIZE - saw_w) // 2
                saw_y = y + (BLOCK_SIZE - saw_h) // 2
                objects.append(Saw(saw_x, saw_y, saw_w, saw_h, move_range=160, axis="x", speed=3))

            elif char == "T":
                tramp_w, tramp_h = 56, 56
                tramp_x = x + (BLOCK_SIZE - tramp_w) // 2
                tramp_y = y + BLOCK_SIZE - tramp_h
                objects.append(Trampoline(tramp_x, tramp_y, tramp_w, tramp_h))

            elif char == "M":
                plat_w, plat_h = 128, 32
                plat_x = x
                plat_y = y + BLOCK_SIZE // 2
                objects.append(MovingPlatform(plat_x, plat_y, plat_w, plat_h, move_range=180, axis="x", speed=2))

            elif char == "P":
                plat_w, plat_h = 128, 32
                plat_x = x
                plat_y = y + BLOCK_SIZE // 2
                objects.append(MovingPlatform(plat_x, plat_y, plat_w, plat_h, move_range=150, axis="y", speed=2))

            elif char == "A":
                fruit_x = x + (BLOCK_SIZE - 40) // 2
                fruit_y = y + (BLOCK_SIZE - 40) // 2
                objects.append(Fruit(fruit_x, fruit_y, "Apple"))

            elif char == "B":
                fruit_x = x + (BLOCK_SIZE - 40) // 2
                fruit_y = y + (BLOCK_SIZE - 40) // 2
                objects.append(Fruit(fruit_x, fruit_y, "Bananas"))

            elif char == "C":
                fruit_x = x + (BLOCK_SIZE - 40) // 2
                fruit_y = y + (BLOCK_SIZE - 40) // 2
                objects.append(Fruit(fruit_x, fruit_y, "Cherries"))

            # ── New trap types ────────────────────────────────
            elif char == "W":
                arrow_w, arrow_h = 48, 48
                arrow_x = x + (BLOCK_SIZE - arrow_w) // 2
                arrow_y = y + (BLOCK_SIZE - arrow_h) // 2
                objects.append(Arrow(arrow_x, arrow_y, arrow_w, arrow_h, speed=4, move_range=400))

            elif char == "D":
                plat_w, plat_h = BLOCK_SIZE, 32
                plat_x = x
                plat_y = y + BLOCK_SIZE - plat_h
                objects.append(FallingPlatform(plat_x, plat_y, plat_w, plat_h))

            elif char == "N":
                fan_w, fan_h = 48, 24
                fan_x = x + (BLOCK_SIZE - fan_w) // 2
                fan_y = y + BLOCK_SIZE - fan_h
                objects.append(Fan(fan_x, fan_y, fan_w, fan_h))

            elif char == "R":
                rh_w, rh_h = 84, 84
                rh_x = x + (BLOCK_SIZE - rh_w) // 2
                rh_y = y + (BLOCK_SIZE - rh_h) // 2
                objects.append(RockHead(rh_x, rh_y, rh_w, rh_h, move_range=180, axis="x", speed=3))

            elif char == "r":
                rh_w, rh_h = 84, 84
                rh_x = x + (BLOCK_SIZE - rh_w) // 2
                rh_y = y + (BLOCK_SIZE - rh_h) // 2
                objects.append(RockHead(rh_x, rh_y, rh_w, rh_h, move_range=150, axis="y", speed=3))

            elif char == "H":
                sh_w, sh_h = 84, 84
                sh_x = x + (BLOCK_SIZE - sh_w) // 2
                sh_y = y + (BLOCK_SIZE - sh_h) // 2
                objects.append(SpikeHead(sh_x, sh_y, sh_w, sh_h, move_range=180, axis="x", speed=4))

            elif char == "h":
                sh_w, sh_h = 84, 84
                sh_x = x + (BLOCK_SIZE - sh_w) // 2
                sh_y = y + (BLOCK_SIZE - sh_h) // 2
                objects.append(SpikeHead(sh_x, sh_y, sh_w, sh_h, move_range=150, axis="y", speed=4))

            elif char == "O":
                ball_w, ball_h = 48, 48
                ball_x = x + (BLOCK_SIZE - ball_w) // 2
                ball_y = y + (BLOCK_SIZE - ball_h) // 2
                objects.append(SpikedBall(ball_x, ball_y, ball_w, ball_h))

            elif char == "G":
                goal_w, goal_h = 64, 64
                goal_x = x + (BLOCK_SIZE - goal_w) // 2
                goal_y = y + BLOCK_SIZE - goal_h
                goal = Goal(goal_x, goal_y, goal_w, goal_h)
                objects.append(goal)

            elif char == "S":
                player_start = (x + (BLOCK_SIZE - 50) // 2, y + BLOCK_SIZE - 50)

    return level["background"], player_start, objects, fires, goal


def level_count():
    return len(LEVELS)
