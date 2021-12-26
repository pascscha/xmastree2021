from generators import *

if __name__ == "__main__":
    INTERVAL = 33

    GREEN_BRIGHT = (0.28, 1, 1)
    GREEN_DARK = (0.28, 1, 0.3)
    RED_BRIGHT = (0, 1, 1)

    init = Combiner([Cone((0, 0, 0), 3, 0.2, 0.6, GREEN_DARK)])

    events = [
        (init, None, None),
        (Combiner([Cone((0, 0, -2), 3, 0.2, 0.6, GREEN_BRIGHT)]), 500, inter_squared_inv),
        (Combiner([Cone((0, 0, 2), 3, 0.2, 0.6, GREEN_DARK)]), 500, inter_squared_inv),
        (Combiner([Cone((0, 0, 2), -2, 0.2, 0.6, RED_BRIGHT)]), 500, inter_linear),
        (init, 500, inter_linear),
    ]

    animations = generate(events, INTERVAL)

    save(animations, "examples/cones.csv")