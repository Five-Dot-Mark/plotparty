import vsketch


class MolnarSketch(vsketch.SketchClass):
    scale_to_bottle = vsketch.Param(False)
    spacing = vsketch.Param(3.5, decimals=2)
    cells_x = vsketch.Param(4)
    def draw(self, vsk: vsketch.Vsketch) -> None:
        height = 170
        vsk.size("320mm" if self.scale_to_bottle else "220mm", f"{height}mm", landscape=False)
        vsk.scale("mm")
        if self.scale_to_bottle:
            vsk.scale(320.0 / 220, 1)

        numCellsX = self.cells_x
        cellSize = 220.0 / numCellsX
        numCellsY = int(height / cellSize)
        rectSize = cellSize - self.spacing

        for x in range(0, numCellsX):
            for y in range(0, numCellsY):
                size = rectSize
                while size > self.spacing:
                    vsk.pushMatrix()
                    vsk.translate(x * cellSize, y * cellSize)
                    vsk.rotate(vsk.random(-0.05 * y / 4, 0.05 * y / 4))
                    if vsk.random(1) > 0.35:
                        vsk.rect(- size / 2, - size/2, size, size)
                    vsk.popMatrix()
                    size -= self.spacing


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MolnarSketch.display()
