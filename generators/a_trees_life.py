from generators import *
import random
import math

if __name__ == "__main__":
    INTERVAL = 33

    RED = (0, 1, 0.8)
    BLUE = (0.66, 1, 0.8)
    YELLOW = (0.16, 1, 0.8)
    GREEN_BRIGHT = (0.28, 1, 1)
    GREEN_DARK = (0.28, 1, 0.3)
    BROWN = (0.13, 1, 0.3)
    
    animations = []

    impact = [
        (Sphere((0, 0, 4), 0, 0.1, YELLOW), None, None),
        (Sphere((0, 0, 4), 0, 0.1, YELLOW), 500, inter_linear), # pause
        (Sphere((0, 0, 0.1), 0, 0.1, GREEN_BRIGHT), 500, inter_squared),
    ]
    animations += generate(impact, INTERVAL)

    grow = [
        (Cone((0, 0, 0), 1, 0.2, 0.3, GREEN_BRIGHT), None, None),
        (Cone((0, 0, 0), 3, 0.2, 0.3, GREEN_DARK), 300, inter_linear),
        (Cone((0, 0, 0), 3.5, 0, 0.7, GREEN_DARK), 300, inter_linear),
    ]
    animations += generate(grow, INTERVAL)

    N_ORNAMENTS = 6
    random.seed(0)
    ornament_1 = []
    ornament_2 = []
    for i in range(N_ORNAMENTS):
        prog = i / (N_ORNAMENTS-1)
        z = (1-prog)**2 * 2 + 1
        radius = (3-z)/3 - 0.1
        angle = random.random() * 2 * math.pi
        x = radius * math.sin(angle)
        y = radius * math.cos(angle)
        color = random.choice([BLUE, RED, YELLOW])
        ornament_1.append(Sphere((x, y, z), 0, 0, GREEN_DARK))
        ornament_2.append(Sphere((x, y, z), 0, 0.05, color))
        

    ornaments_grow = [
        (Combiner([Cone((0, 0, 0), 3.5, 0, 0.7, GREEN_DARK)] + ornament_1), None, None),
        (Combiner([Cone((0, 0, 0), 3.5, 0, 0.7, GREEN_DARK)] + ornament_2), 1000, inter_linear),
    ]
    animations += generate(ornaments_grow, INTERVAL)

    rotate = [
        (RotatorZ(0,         Combiner([Cone((0, 0, 0), 3.5, 0, 0.7, GREEN_DARK)] + ornament_2)), None, None),
        (RotatorZ(2*math.pi, Combiner([Cone((0, 0, 0), 3.5, 0, 0.7, BROWN)] + ornament_2)), 5000, inter_linear),
    ]
    animations += generate(rotate, INTERVAL)

    fly_away = [
        (Transformer(Combiner([Cone((0, 0, -2), 3, 0, 0.2, (0.1, 1, 1)), Cone((0, 0, 0), 3.5, 0, 0.7, BROWN)] + ornament_2), offset=[0,0,0]), None, None),
        (Transformer(Combiner([Cone((0, 0, -3), 6, 0, 0.2, (0.1, 1, 0.5)), Cone((0, 0, 0), 3.5, 0, 0.7, GREEN_BRIGHT)] + ornament_2), offset=[0,0,6]), 1000, inter_squared),
    ]
    animations += generate(fly_away, INTERVAL)

    animations = animations
    save(animations, "examples/a_trees_life.csv")