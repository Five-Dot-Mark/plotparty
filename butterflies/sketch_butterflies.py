import shapely.affinity
import shapely.geometry
import shapely.geometry.base
import vsketch
from math import sin, cos, pi as PI, exp, pow
import shapely
from random import Random


def poww(x, y):
    if x == 0:
        return 0
    sign = x / abs(x)
    return pow(abs(x), y) * sign


def butterfly(radius, cx, cy, rnd: Random):
    points = []
    np = 200
    radius /= 10
    step = PI / np
    a = rnd.random() * 2 * PI
    for i in range(np * 12):
        t = i*step
        r = exp(sin(t)) - 2 * cos(4*t) + pow(sin(((2*t) - PI)/24), 5)
        points.append((cx + cos(t+a) * r * radius, cy + sin(t+a) * r * radius))
    return (shapely.LinearRing(points), shapely.Polygon(points))


def flower(radius, cx, cy, rnd: Random):
    points = []
    np = 2000
    off = rnd.random()
    scale = 1.0 / (2 + off) * radius
    pw = rnd.random() * 20 + 3
    n = rnd.randint(3, 9)
    s1 = rnd.randint(0, 1) * 2 - 1
    s2 = rnd.randint(0, 1) * 2 - 1
    for i in range(np):
        t = PI * 2 / np * i
        r = poww(cos(n*t), pw) + s1 * sin(s2*n*t) + off
        points.append((cx + cos(t) * r * scale, cy + sin(t) * r * scale))
    return (shapely.LinearRing(points), shapely.Polygon(points))


def polygon(radius, cx, cy, rnd: Random):
    a = rnd.random() * 2 * PI
    n = rnd.randint(3, 9)
    step = 2 * PI / n
    points = [(cx + cos(a + i*step) * radius, cy + sin(a + i*step) * radius)
              for i in range(n)]
    return (shapely.LinearRing(points).normalize(), shapely.Polygon(points).normalize())


def triangle(t, radius):
    return (cos(t) * radius, sin(t) * radius)


def fit_rect(poly: shapely.geometry.base.BaseGeometry, w, h):
    (x1, y1, x2, y2) = poly.bounds
    pw, ph = x2-x1, y2-y1
    return min(w / pw, h / ph)


def cover_rect(poly: shapely.geometry.base.BaseGeometry, w, h):
    ray = shapely.LineString([(0, 0), (w*1000, h * 1000)])
    outline = shapely.LinearRing(poly.exterior.coords)
    intersection = shapely.intersection(ray, outline)
    ix, iy = intersection.coords[0]
    return max(w / 2 / ix, h / 2 / iy)


class ButterfliesSketch(vsketch.SketchClass):
    page_width = vsketch.Param(210)
    page_height = vsketch.Param(297)
    margin = vsketch.Param(15)
    num_colors = vsketch.Param(1, 1, 6)
    gap = vsketch.Param(0.5, decimals=1)
    polygons = vsketch.Param(True)
    fill_probability = vsketch.Param(40, 0, 100)
    num_shapes = vsketch.Param(30, 2, 100)
    num_sides = vsketch.Param(6, 3, 16)
    fit = vsketch.Param(True)
    scale_width = vsketch.Param(210)
    scale_height = vsketch.Param(297)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        rnd = vsk._random
        pw = self.page_width
        ph = self.page_height
        margin = self.margin
        w = pw - 2 * margin
        h = ph - 2 * margin
        vsk.size(f"{self.scale_width}mm", f"{self.scale_height}mm", landscape=False)

        vsk.scale("mm")
        vsk.translate(0, ph)
        vsk.scale(self.scale_width / self.page_width, -self.scale_height/ self.page_height)
        vsk.translate(margin + w/2, margin + h / 2)

        num_sides = self.num_sides

        points = [(cos(i * 2 * PI / num_sides + PI / 2 - PI/num_sides) * 100, sin(i * 2 * PI / num_sides + PI / 2 - PI/num_sides) * 100)
                  for i in range(num_sides)]
        poly = shapely.Polygon(points).normalize()
        scale = fit_rect(poly, w, h) if self.fit else cover_rect(poly, w, h)
        vsk.scale(scale)

        a = PI/2 - PI / num_sides
        mask = shapely.Polygon(
            [(0, 0), (cos(a), sin(a)), (0, sin(a))])
        mask = shapely.affinity.scale(
            mask, 100, 100, origin=(0, 0))

        (mx1, my1, mx2, my2) = shapely.bounds(mask)
        (mw, mh) = (mx2-mx1, my2-my1)

        page_mask = shapely.affinity.scale(shapely.Polygon(
            [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]), 1.0 / scale, 1.0 / scale)

        for loop in range(self.num_shapes):
            gen = rnd.choice([ flower,  polygon])
            size = (rnd.random() * 40 + 20)
            (lines, poly) = gen(size, mw *
                                rnd.random(), mh * rnd.random(), rnd)
            do_fill = rnd.random() < self.fill_probability / 100
            if do_fill:
                visible = shapely.offset_curve(shapely.Polygon(
                    list(poly.exterior.coords)).normalize(), self.gap).normalize()
                visible = shapely.intersection(mask, visible)
            else:
                visible = shapely.intersection(mask, lines)
            visible = shapely.union(visible, shapely.affinity.scale(
                visible, -1, 1, origin=(0, 0)))
            final = visible
            step = 1
            for i in range(step - 1, num_sides-1, step):
                final = shapely.union(final, shapely.affinity.rotate(
                    visible, 360 / num_sides * (i+1), origin=(0, 0)))
            if not self.fit:
                final = shapely.intersection(final, page_mask)
            color = rnd.randint(1, self.num_colors)
            if do_fill:
                vsk.fill(color)
                vsk.noStroke()
            else:
                vsk.stroke(color)
                vsk.noFill()
            vsk.geometry(final)
            if self.polygons:
                exterior = shapely.buffer(shapely.Polygon(
                    list(poly.exterior.coords)).normalize(), self.gap)
            else:
                exterior = shapely.buffer(shapely.LinearRing(
                    list(poly.exterior.coords)).normalize(), self.gap)
            if rnd.random() < 1:
                mask = shapely.difference(mask, exterior)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    SpiralSketch.display()
