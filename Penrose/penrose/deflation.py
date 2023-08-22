from collections import UserList
from functools import wraps
from multiprocessing import Process
import cmath
import math
import timeit
import cairo
import time

TOLERANCE = 1e-6
golden_ratio = (1 + 5**0.5) / 2

IMAGE_SIZE = 1000

PENROSE_LARGE_TILE = 0
PENROSE_SMALL_TILE = 1

NUM_ITERATIONS = 17


def timeme(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        result = func(*args, **kwargs)
        end = timeit.default_timer()
        print(f"--- {end - start} seconds ---")
        return result

    return wrapper


class PenroseTileSet(UserList):
    def __init__(self, tiles: list[tuple] = None):
        self.data = tiles or []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"PenroseTileSet({self.data})"

    def flatten(self):
        output_list = []
        for tile in self:
            if isinstance(tile, PenroseTileSet):
                output_list.extend(tile.flatten())
            else:
                output_list.append(tile)
        self.data = output_list
        return output_list

    def deflate(self):
        self.data = deflateTileSet(self.data)
        return self

    def draw(self, ctx: cairo.Context):
        for tile in self:
            drawTile(tile, ctx)


def deflateTileSet(tiles: list[tuple]) -> list[tuple]:
    new_data = []
    for tile in tiles:
        if tile[3] == PENROSE_LARGE_TILE:
            new_data.extend(deflateLargeTile(*tile))
        else:
            new_data.extend(deflateSmallTile(*tile))
    if isinstance(tiles, PenroseTileSet):
        return PenroseTileSet(new_data)
    return new_data


def deflateLargeTile(A, B, C, color) -> PenroseTileSet:
    """
    Deflate a large Penrose tile into three smaller tiles.

    If the original tile is ABC where B is the vertex of the kite, then we need
    to add 2 more vertices:
      D. is the vertex on AC side of the kite
      E. is the vertex on AB side of the kite

    The new tiles are:
      DEA: Large tile (mirrored from original orientation)
      CDB: Large tile (same orientation as original but rotated)
      EDB: Small tile (mirrored from original orientation)
    """
    D = A + (C - A) / golden_ratio
    E = A + (B - A) / golden_ratio

    result = [
        (D, E, A, PENROSE_LARGE_TILE),
        (C, D, B, PENROSE_LARGE_TILE),
        (E, D, B, PENROSE_SMALL_TILE),
    ]

    return result
    # return PenroseTileSet(result)


def deflateSmallTile(A, B, C, color) -> PenroseTileSet:
    """
    Deflate a small Penrose tile into two smaller tiles.

    If the original tile is ABC where B is the vertex of the kite, then we need
    to add 1 more vertex:
      D. is the vertex on AB side of the kite

    The new tiles are:
      DCA: Small tile (same orientation as original but rotated)
      CDB: Large tile (same orientation as original but rotated)
    """
    D = B + (A - B) / golden_ratio

    result = [
        (D, C, A, PENROSE_SMALL_TILE),
        (C, D, B, PENROSE_LARGE_TILE),
    ]

    return result
    # return PenroseTileSet(result)


def generateSmallRotatedStarterSet(
    center_point: complex = None, size: int = 1, separate_sets: bool = False
) -> PenroseTileSet:
    """Generates a set of 10 rotated Small tiles, every second one mirrored."""
    output = []
    center_point = center_point or complex()
    for rotation in range(10):
        # A and C are the vertices of the kite on the unit circle. A starts at
        # the top and C is rotated by 36 degrees clockwise.
        A = cmath.rect(size, rotation * math.pi / 5) + center_point
        C = cmath.rect(size, (rotation + 1) * math.pi / 5) + center_point
        if rotation % 2 == 0:
            # Mirror every second tile
            A, C = C, A
        output.append((A, center_point, C, PENROSE_SMALL_TILE))
    if not separate_sets:
        return PenroseTileSet(output)
    else:
        return output


def drawTile(tile: tuple, ctx: cairo.Context):
    # Draw the tile
    ctx.move_to(tile[0].real, tile[0].imag)
    ctx.line_to(tile[1].real, tile[1].imag)
    ctx.line_to(tile[2].real, tile[2].imag)
    ctx.close_path()
    if tile[3] == PENROSE_SMALL_TILE:
        ctx.set_source_rgb(0.8, 0, 0)
    else:
        ctx.set_source_rgb(0, 0, 0.8)
    ctx.fill()

    # Draw the outline
    ctx.move_to(tile[0].real, tile[0].imag)
    ctx.line_to(tile[1].real, tile[1].imag)
    ctx.line_to(tile[2].real, tile[2].imag)
    ctx.close_path()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.1)
    ctx.stroke()


def deflateTileSetNTimes(tiles: PenroseTileSet, n: int = 10) -> PenroseTileSet:
    if not isinstance(tiles, PenroseTileSet):
        tiles = PenroseTileSet([tiles])
    for i in range(n):
        tiles.deflate()
    return tiles


@timeme
def main(n: int = NUM_ITERATIONS):
    scale = 10

    starter_set = generateSmallRotatedStarterSet(
        center_point=complex(IMAGE_SIZE / 2 / scale, IMAGE_SIZE / 2 / scale),
        size=IMAGE_SIZE / scale / 2,
    )

    deflateTileSetNTimes(starter_set, n)

    return len(starter_set)

    # with cairo.SVGSurface("test.svg", IMAGE_SIZE, IMAGE_SIZE) as surface:
    #     ctx = cairo.Context(surface)
    #     ctx.scale(scale, scale)
    #     ctx.set_line_width(0.01)
    #     ctx.set_source_rgb(0, 0, 0)
    #     ctx.set_line_cap(cairo.LineCap.ROUND)
    #     ctx.set_line_join(cairo.LineJoin.ROUND)

    #     starter_set.draw(ctx)
    #     starter_set.deflate().draw(ctx)


@timeme
def parallelized():
    scale = 10

    starter_set = generateSmallRotatedStarterSet(
        center_point=complex(IMAGE_SIZE / 2 / scale, IMAGE_SIZE / 2 / scale),
        size=IMAGE_SIZE / scale / 2,
        separate_sets=True,
    )

    jobs = []
    for i in range(len(starter_set)):
        p = Process(
            target=deflateTileSetNTimes,
            args=(
                starter_set[i],
                NUM_ITERATIONS,
            ),
        )
        jobs.append(p)
        p.start()

    for job in jobs:
        job.join()


if __name__ == "__main__":
    out = []
    for i in range(1, NUM_ITERATIONS + 1):
        print(f"Iterations: {i}")
        out.append(main(i))
        if len(out) > 1:
            print(out[-1], f"Ratio: {out[-1] / out[-2]}")
        else:
            print(out[-1])

    # parallelized()
