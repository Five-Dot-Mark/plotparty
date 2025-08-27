import vsketch
import shapely
import random
from math import sin, cos, pi as PI, log

class Tile:

    def __init__(self, flip):
        self.colors = [-1, -1]
        self.flip = flip

    def paint(self, vsk: vsketch.Vsketch):
        n = 100
        da = PI/2/n
        points = [ (1 - 0.5 * cos(i * da), 0.5 * sin(i * da) ) for i in range(n+1)  ]
        arc = shapely.LineString(points)
        if self.flip:
            arc = shapely.affinity.rotate(arc, -90, origin=(0.5, 0.5))
        if self.colors[0] != -1:
            vsk.stroke(self.colors[0])
            vsk.geometry(arc)
        if self.colors[1] != -1:
            vsk.stroke(self.colors[1])
            arc = shapely.affinity.rotate(arc, 180, origin=(0.5, 0.5))
            vsk.geometry(arc)
    
    def other_point(self, dir):
        return dir ^ 3 if self.flip else dir ^ 1

    def color_idx(self, dir):
        if not self.flip:
            return int(dir / 2)
        else:
            return int(((dir + 1) % 4)/2)

def neighbor(row, col, dir, rows, cols):
    #dx, dy = [ (0, -1), (1, 0), (0, 1), (-1, 0)][dir]
    if row == 0 and dir == 0:
        offsets = [ (    1 - (col%2) * 2 , 0)]
        new_dir = dir
    elif row == rows - 1 and dir == 2:
        offsets = [ None, None, ( 1 - (col%2) * 2, 0)]
        new_dir = dir
    else:
        new_dir = (dir + 2) % 4
        offsets = [ (0, -1), (1, 0), (0, 1), (-1, 0)]
    dx, dy = offsets[dir]
    return ( (row +  rows + dy) % rows, (col +  cols + dx) % cols , new_dir )

def rowcol(idx, rows, cols):
    return ( int(idx / cols), idx % cols )

def select_tile(tiles: list):
    for idx, t in enumerate(tiles):
        if t.colors[0] == -1:
            return (idx, 0)
        if t.colors[1] == -1:
            return (idx, 1)
    return None

def cap(vsk: vsketch.Vsketch, rot):
    n = 100
    da = PI/2/n
    points = [ (1 - 0.5 * cos(i * da), 1 - 0.5 * sin(i * da) ) for i in range(n+1)  ]
    arc = shapely.LineString(points)
    arc = shapely.affinity.rotate(arc, 90 * rot, origin=(0.5, 0.5))
    vsk.geometry(arc)
    

class TilesSketch(vsketch.SketchClass):
    cols = vsketch.Param(4, step=2)
    scale_to_bottle = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:

        w = 220 if not self.scale_to_bottle else 320
        h = 160
        cols = self.cols
        cell_size = w / cols
        rows = int(h/ cell_size) - 2


        vsk.size(f"{w}mm", f"{h}mm", landscape=False, center=False)
        vsk.scale("mm")
        vsk.scale(w / cols ,  cell_size)
        tiles = [ Tile(random.random() < 0.5) for _ in range(rows * cols) ]

        while True:
            selected =  select_tile(tiles)
            if selected == None:
                break
            start, color = selected
            idx = start
            dir = color * 2
            start_dir = dir
            t = tiles[idx]
            if t.colors[0] == -1 and t.colors[1] == -1:
                cl = random.randint(1,2)
            elif t.colors[0] != -1:
                cl = t.colors[0] ^ 3
            else:
                cl = t.colors[1] ^ 3
            while True:
                tile = tiles[idx]
                cl_idx = tile.color_idx(dir)
                r, c = rowcol(idx, rows, cols)
                if tile.colors[cl_idx] != -1:
                    break
                tile.colors[cl_idx] = cl
                dir = tile.other_point(dir)
                r, c, dir = neighbor(r, c, dir, rows, cols)
                idx = r * cols + c
                if idx == start and dir == start_dir:
                    break

            

        for idx,t in enumerate(tiles):
            with vsk.pushMatrix():
                r, c = rowcol(idx, rows, cols)
                vsk.translate(c, r+1)
                t.paint(vsk)
        with vsk.pushMatrix():
            for c in range(cols):
                t = tiles[c]
                cl_idx = t.color_idx(0)
                vsk.stroke(t.colors[cl_idx])
                cap(vsk, c % 2)
                vsk.translate(1, 0)
        with vsk.pushMatrix():
            vsk.translate(0, rows+1)
            for c in range(cols):
                t = tiles[c + cols * (rows-1)]
                cl_idx = t.color_idx(2)
                vsk.stroke(t.colors[cl_idx])
                cap(vsk, 3 - c % 2 )
                vsk.translate(1, 0)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    Tiles2Sketch.display()
