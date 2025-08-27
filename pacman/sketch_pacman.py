import vsketch
from math import sqrt, sin, pi as PI

pacman = [
    0b000111110000,
    0b011111111100,
    0b111111111110,
    0b111111111110,
    0b001111111111,
    0b000001111111,
    0b000000001111,
    0b000001111111,
    0b001111111111,
    0b111111111110,
    0b011111111100,
    0b000111110000
]

pinky = [
    0b00000111100000,
    0b00011111111000,
    0b00111111111100,
    0b01001111001110,
    0b00000110000110,
    0b01100111100110,
    0b11100111100111,
    0b11001111001111,
    0b11111111111111,
    0b11111111111111,
    0b11111111111111,
    0b11111111111111,
    0b10001100110001
]

def distance(x, y, pixels, cols):
    min_dist = 1000000
    for px, py in pixels:
        dx = abs(px - x)
        dx = min(dx, cols - dx)
        dist = sqrt(dx * dx + (py-y)*(py-y))
        if dist < min_dist:
            min_dist = dist
    return min_dist


class PacmanSketch(vsketch.SketchClass):
    columns = vsketch.Param(54)
    use_sine = vsketch.Param(True)
    lines_per_row = vsketch.Param(1)
    frequency = vsketch.Param(4)
    scale_to_bottle = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("320mm", "160mm")
        vsk.scale("mm")
        if self.scale_to_bottle:
            vsk.scale(320/220, 1)

        cols = self.columns
        cell_size = 220/cols
        rows = int(160 / cell_size) - 1
        vsk.scale(cell_size)

        pixels = []

        canvas = [ [False]*cols for _ in range(rows)  ]
        cx, cy = int(cols/2), int(rows/2)
        for y, word in enumerate(pacman):
            for x in range(12):
                if word & (1 << (11 - x)) != 0:
                    pixels.append( (x + 1.5, y + cy - 6 +0.5) )
                    canvas[y+cy-6][x+1] = True
        for y, word in enumerate(pinky):
            for x in range(14):
                if word & (1 << (13 - x)) != 0:
                    pixels.append( (x + cx + 1.5, y + cy - 7 +0.5) )
                    canvas[y+cy -7][x + cx + 1] = True
        
        freq = self.frequency
        step_x = 1 / 8 / freq

        step_y = 1.0 / self.lines_per_row
        if self.use_sine:
            for row in range(rows * self.lines_per_row):
                y0 = (row + 0.5) * step_y
                x = 0
                prevx = 0
                prevy = 0
                while x <= cols:
                    dist = distance(x, y0, pixels, cols)
                    amp = 1.0 / (dist + 1) / (dist + 1) * 0.5
                    y = sin(x * 2 * PI * freq) * amp * step_y
                    vsk.line(prevx, prevy + y0, x, y + y0)
                    prevx = x
                    prevy = y
                    x += step_x
        else:
            for row in range(rows):
                for col in range(cols):
                    num_lines = self.lines_per_row if canvas[row][col] else 1
                    for n in range(num_lines):
                        vsk.line(col, (row + 0.5) + n * step_y, col+1, (row + 0.5) + n * step_y)

        

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    PacmanSketch.display()
