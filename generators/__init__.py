import numpy as np
from visualization.visualize import Animation
import colorsys


def write_animation(animation, path):
    animation = animation.reshape(animation.shape[0], -1)

    with open(path, "w+") as f:
        # Write header
        f.write("FRAME_ID")
        for i in range(animation.shape[1]//3):
            f.write(f",R_{i},G_{i},B_{i}")
        f.write("\n")

        for frame_id, frame in enumerate(animation):
            f.write(f"{frame_id}," + ",".join(map(str, frame)) + "\n")


def rgb_to_hsv(animation):
    for frame_idx in range(len(animation)):
        for pixel_idx in range(len(animation[frame_idx])):
            r, g, b = animation[frame_idx][pixel_idx]
            animation[frame_idx][pixel_idx] = colorsys.rgb_to_hsv(r, g, b)
    return animation


def hsv_to_rgb(animation):
    for frame_idx in range(len(animation)):
        for pixel_idx in range(len(animation[frame_idx])):
            h, s, v = animation[frame_idx][pixel_idx]
            animation[frame_idx][pixel_idx] = colorsys.hsv_to_rgb(h, s, v)
    return animation


class AnimatedFunction:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @classmethod
    def _mul_args(cls, args, amount):
        if isinstance(args, list):
            return [cls._mul_args(a, amount) for a in args]
        elif isinstance(args, tuple):
            return tuple([cls._mul_args(a, amount) for a in args])
        elif isinstance(args, dict):
            return {k: cls._mul_args(v, amount) for k, v in args.items()}
        elif args is None:
            return None
        else:
            return args * amount

    @classmethod
    def _add_args(cls, args1, args2):
        if isinstance(args1, list):
            assert isinstance(args2, list) and len(args1) == len(args2)
            return [cls._add_args(a1, a2) for a1, a2 in zip(args1, args2)]
        elif isinstance(args1, tuple):
            assert isinstance(args2, tuple) and len(args1) == len(args2)
            return tuple([cls._add_args(a1, a2) for a1, a2 in zip(args1, args2)])
        elif isinstance(args1, dict):
            assert isinstance(args2, dict) and len(args1) == len(args2)
            return {k1: cls._add_args(v1, args2[k1]) for k1, v1 in args1.items()}
        elif args1 is None:
            assert args2 is None
            return None
        else:
            return args1 + args2

    def __mul__(self, amount):
        args = self._mul_args(self.args, amount)
        kwargs = self._mul_args(self.kwargs, amount)
        return self.__class__(*args, **kwargs)

    def __add__(self, other):
        args = self._add_args(self.args, other.args)
        kwargs = self._add_args(self.kwargs, other.kwargs)
        return self.__class__(*args, **kwargs)

    def get_frame(self, coords, frame):
        raise NotImplementedError("Please implement this method.")


class Cone(AnimatedFunction):
    def __init__(self, base, height, inner_radius, outer_radius, color):
        super().__init__(base, height, inner_radius, outer_radius, color)
        self.base = base
        self.height = height
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.color = color

    def get_frame(self, coords, frame):
        for i, coord in enumerate(coords):
            vect = coord - self.base
            r = 1 - vect[2] / self.height
            if 0 < r < 1:
                d = (vect[0] ** 2 + vect[1] ** 2) ** 1/2
                if self.inner_radius * r <= d < self.outer_radius * r:
                    frame[i] = self.color
        return frame


class Sphere(AnimatedFunction):
    def __init__(self, center, inner_radius, outer_radius, color):
        super().__init__(center, inner_radius, outer_radius, color)
        self.center = center
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.color = color

    def get_frame(self, coords, frame):
        for i, coord in enumerate(coords):
            vect = coord - self.center
            d = (vect[0] ** 2 + vect[1] ** 2 + vect[2] ** 2) ** 1/2
            if self.inner_radius <= d < self.outer_radius:
                frame[i] = self.color
        return frame


class Combiner(AnimatedFunction):
    def __init__(self, functions):
        super().__init__(functions)
        self.functions = functions

    def get_frame(self, coords, frame):
        for f in self.functions:
            frame = f.get_frame(coords, frame)
        return frame


class Transformer(AnimatedFunction):
    def __init__(self, function, offset=None, transform=None):
        super().__init__(function, offset=offset, transform=transform)
        self.offset = offset
        self.transform = transform
        self.function = function

    def get_frame(self, coords, frame):
        coords = coords.copy()
        if self.transform is not None:
            for i in range(len(coords)):
                coords[i] = coords[i] @ self.transform
        if self.offset is not None:
            for i in range(len(coords)):
                coords[i] = coords[i] - self.offset

        return self.function.get_frame(coords, frame)


class RotatorZ(AnimatedFunction):
    def __init__(self, angle, function):
        super().__init__(angle, function)
        self.angle = angle
        self.function = function

    def get_frame(self, coords, frame):
        transform = np.array([
            [np.cos(self.angle), -np.sin(self.angle), 0],
            [np.sin(self.angle), np.cos(self.angle), 0],
            [0, 0, 1]
        ])
        trans = Transformer(self.function, transform=transform)
        return trans.get_frame(coords, frame)


def inter_linear(x):
    return x


def inter_squared(x):
    return x**2


def inter_squared_inv(x):
    return 1 - (1-x)**2


def animate(coords, f1, f2, interval, duration, interpolation=inter_linear):
    n_frames = int(duration / interval)
    out = np.zeros((n_frames, len(coords), 3), dtype=np.float32)
    for i in range(n_frames):
        prog = interpolation((i+1)/n_frames)
        f = f1 * (1 - prog) + f2 * prog
        out[i] = f.get_frame(coords, out[i])
    return out


def generate(events, interval):
    coords = Animation.load_csv("coords_2021.csv")
    animations = []
    for i in range(len(events) - 1):
        animations.append(
            animate(
                coords,
                events[i][0],
                events[i+1][0],
                interval,
                events[i+1][1],
                interpolation=events[i+1][2]
            )
        )

    return animations


def save(animations, path):
    tot_len = sum(len(a) for a in animations)
    animation = np.empty(
        (tot_len, animations[0].shape[1], 3), dtype=np.float32)
    i = 0
    for a in animations:
        animation[i:i+len(a)] = a
        i += len(a)

    animation = (hsv_to_rgb(animation) * 255).astype(np.uint8)
    write_animation(animation, path)
