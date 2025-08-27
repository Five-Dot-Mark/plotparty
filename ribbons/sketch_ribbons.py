import vsketch
import random

class RibbonsSketch(vsketch.SketchClass):
    colums = vsketch.Param(10)
    lines_per_cell = vsketch.Param(3)
    probability = vsketch.Param(0.33, decimals=2)
    two_colors = vsketch.Param(False)
    scale_to_bottle = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("320mm" if self.scale_to_bottle else "220mm", "160mm", landscape=False)
        vsk.scale("mm")
        if self.scale_to_bottle:
            vsk.scale(320/220, 1)

        cols = self.colums
        cell_size = 220 / cols
        rows = int(160 / cell_size)

        cells = []
        for c in range(cols):
            if vsk.random(1) < self.probability:
                for r in range(rows):
                    cells.append( (r, c, True)  )
        for r in range(rows):
            if vsk.random(1) < self.probability:
                for c in range(cols):
                    cells.append( (r, c, False)  )
        
        occupied = [[False for _ in range(cols)] for _ in range(rows)]
        random.shuffle(cells)
        for (r, c, vertical) in cells:
            if occupied[r][c]:
                continue
            vsk.stroke(2 if vertical and self.two_colors else 1)
            x, y = c * cell_size, r * cell_size
            dx = cell_size / (self.lines_per_cell - 1) if vertical else 0
            dy = 0 if vertical else cell_size / (self.lines_per_cell - 1)
            for _ in range(self.lines_per_cell):
                if vertical:
                    vsk.line(x, y, x, y + cell_size)
                else:
                    vsk.line(x, y, x + cell_size, y)
                x += dx
                y += dy
            occupied[r][c] = True

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge deduplicate linesimplify reloop linesort")


if __name__ == "__main__":
    RibbonsSketch.display()
