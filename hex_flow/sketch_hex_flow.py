import vsketch
import math
import shapely
import random

from math import cos, sin, pi as PI, sqrt

PI_DIV_3 = math.pi / 3
COS60 = math.sqrt(3) / 2
RAD = 1.0 / COS60


def iterate_tiles(n_cols, n_rows, callback):
    for row in range(n_rows):
        for col in range(-(row % 2), n_cols):
            x = col * 2 + (row % 2)
            y = row * COS60 * 2
            if row == 0 and col == 0:
                indexes = range(0, 7)
            if row == 0 and col != 0:
                indexes = [5, 0, 1, 2, 3, 4]
            elif row % 2 == 1 and col == -1:
                indexes = [3, 4, 5, 0, 1, 2]
            elif row % 2 == 1 and col == n_cols - 1:
                indexes = [5, 0, 1, 2, 3]
            elif row % 2 == 1:
                indexes = [5, 0, 1, 2]
            elif row % 2 == 0 and col == 0:
                indexes = [4, 5, 0, 1, 2]
            elif row % 2 == 0:
                indexes = [5, 0, 1, 2]

            points = [(x + RAD * math.sin(i*PI_DIV_3), y + RAD *
                       math.cos(i*PI_DIV_3)) for i in range(0, 7)]
            geom = shapely.LineString([points[i] for i in range(0, 7)])
            poly = shapely.Polygon(points)
            callback(x, y, geom, poly)


def hatch(cx, cy, angle, spacing, offset):
    radius = 1 / COS60
    cs, sn = cos(angle), sin(angle)
    cs1, sn1 = cos(
        angle + PI / 2), sin(angle + PI / 2)
    if offset:
        cx += cs1*spacing / 2
        cy += sn1 * spacing / 2
    mx, my = 0, 0
    lines = []
    first = True
    while (mx >= -(1+spacing) and mx <= 1+spacing) and (my >= -(1+spacing) and my <= 1+spacing):
        x, y = cs*radius, sn * radius
        points = [(mx + cx + x, my + cy + y), (mx + cx - x, my + cy - y)]
        lines.append(points)
        if not first:
            points = [(-mx + cx + x, -my + cy + y),
                      (-mx + cx - x, -my + cy - y)]
            lines.append(points)
        x, y = cs1*spacing, sn1 * spacing
        mx, my = mx + x, my + y
        first = False
    random.shuffle(lines)
    remove_count = random.randint(1, 2)
    lines = lines[remove_count:]
    lines = [shapely.linestrings(p) for p in lines]
    lines = shapely.geometrycollections(lines)
    return lines


class HexFlowSketch(vsketch.SketchClass):
    cell_size = vsketch.Param(5.00, decimals=3)
    scale_to_bottle = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        pw = 220
        if self.scale_to_bottle:
            pw = 320
        vsk.size(f"{pw}mm", "160mm", landscape=False)

        vsk.scale("mm")
        vsk.translate(0, 160)
        vsk.scale(1, -1)

        usable_w = 220
        usable_h = 160
        n_cols = int(usable_w / self.cell_size) - 1

        scale = usable_w/(n_cols+1)/2
        n_rows = int(usable_h / scale / 2 / COS60)

        vsk.scale(scale)
        if self.scale_to_bottle:
            vsk.scale(320/220, 1)

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")
        mask = shapely.Polygon([(-scale, -scale), (220 / scale, -scale), (220 /
                               scale, 160 / scale), (-scale, 160/scale), (-scale, -scale)])
        self.cells = []
        self.spacing_range = (1, 0)
        iterate_tiles(n_cols, n_rows, self.process_cell)
        self.draw_cells(mask)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge deduplicate")

    def process_cell(self, x, y, geom, poly):
        vsk = self.vsk
        mn, mx = self.spacing_range
        angle = vsk.noise(x/20, y/20) * 2 * PI
        spacing = vsk.noise(x/5 + 500, y/5 + 500)
        self.spacing_range = (min(mn, spacing), max(mx, spacing))
        self.cells.append((x, y, geom, poly, angle, spacing))

    def draw_cells(self, mask):
        vsk = self.vsk
        mn, mx = self.spacing_range
        for cell in self.cells:
            (x, y, geom, poly, angle, spacing) = cell
            do_hatch = True
            noise_value = vsk.noise(x*1000 + 5000, y*1000 + 5000)
            if noise_value > 0.6:
                # mask = shapely.difference(mask, poly)
                do_hatch = False
                pass

            scaled_spacing = ((spacing - mn) / (mx - mn))
            spacing = 0.5 + 1.0 * scaled_spacing
            if do_hatch:
                #vsk.stroke(1)
                vsk.geometry(shapely.intersection(mask, geom))
                #vsk.stroke(2)
                vsk.geometry(shapely.intersection_all(
                    [mask, poly, hatch(x, y, angle, spacing, True)]))
                #vsk.stroke(3)
                vsk.geometry(shapely.intersection_all(
                    [mask, poly, hatch(x, y, angle, spacing, False)]))


if __name__ == "__main__":
    HexFlowSketch.display()
