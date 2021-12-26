from generators import *

if __name__ == "__main__":
    INTERVAL = 33

    WHITE = (0, 0, 1)
    BLACK = (0, 0, 0)

    events = [
        (Combiner([
            Sphere((0, 0, 3.1), 0, 0.05, WHITE),
            Sphere((0, 0, 3.1), 0, 0.05, WHITE),
            Sphere((0, 0, 3.1), 0, 0.05, WHITE),
            Sphere((0, 0, 3.1), 0, 0.05, WHITE)
        ]) , None, None),
        (Combiner([
            Sphere((0, 1, -0.1), 0, 0.05, BLACK),
            Sphere((1, 0, -0.1), 0, 0.05, BLACK),
            Sphere((0, -1, -0.1), 0, 0.05, BLACK),
            Sphere((-1, 0, -0.1), 0, 0.05, BLACK)
        ]) , 1000, inter_linear),
    ]

    animations = generate(events, INTERVAL)

    save(animations, "examples/spheres.csv")