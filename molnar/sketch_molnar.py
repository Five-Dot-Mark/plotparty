import vsketch


class MolnarSketch(vsketch.SketchClass):
    # Sketch parameters:
    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("320mm", "170mm", landscape=False)
        vsk.scale("mm")
        vsk.scale(320.0 / 220, 1)

        penWidth = 1.2
        numCellsX = 4
        numCellsY = 3
        cellSize = 220.0 / numCellsX
        rectSize = cellSize - penWidth * 2

        #implement your sketch here
        for x in range(0, numCellsX):
            for y in range(0, numCellsY):
                size = rectSize
                while size > penWidth * 3:
                    vsk.pushMatrix()
                    vsk.translate(x * cellSize, y * cellSize)
                    #vsk.rotate(vsk.random(-0.05, 0.05))
                    if vsk.random(1) > 0.35:
                        vsk.rect(- size / 2, - size/2, size, size)
                    vsk.popMatrix()
                    size -= penWidth*3


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    MolnarSketch.display()
