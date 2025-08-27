import vsketch

PI_DIGITS = "3141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165271201909145648566923460348610454326648213393607260249141273724587006606315588174881520920962829254091715364367892590360011330530548820466521384146951941511609433057270365759591953092186117381932611793105118548074462379962749567351885752724891227938183011949129833673362440656643086021394946395224737190702179860943702770539217176293176752384674818467669405132000568127145263560827785771342757789609173637178721468440901224953430146549585371050792279689258923542019956112129021960864034418159813629774771309960"

        

class PiSketch(vsketch.SketchClass):
    scale_to_bottle = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size( "320mm" if self.scale_to_bottle else "220mm", "160mm", landscape=False)
        vsk.scale("mm")
        if self.scale_to_bottle:
            vsk.scale(320/220, 1)

        r0 = 2
        r_step = 1.1
        cols = 18

        step = 220 / cols
        rows = 13


        digits = [[ int(PI_DIGITS[r * cols + c])  for c in range(cols)] for r in range(rows)]
        for r in range(rows):
            for c in range(cols):
                digit = digits[r][c]
                cx, cy = step / 2 + c * step, r * step
                radius = r0 * (r_step ** digit)
                if digit > 0:
                    vsk.circle(cx, cy, radius, mode="radius")
                if digits[r][(c + 1) % cols] == digit:
                    self.wrapped_line(vsk, cx, cy, cx + step, cy)
                if digits[r][(c - 1) % cols] == digit:
                    self.wrapped_line(vsk, cx, cy, cx - step, cy)
                if r > 0:
                    if digits[r-1][c] == digit:
                        self.wrapped_line(vsk, cx, cy, cx, cy-step)
                    if digits[r-1][(c - 1) % cols] == digit:
                        self.wrapped_line(vsk, cx, cy, cx-step, cy-step)
                    if digits[r-1][(c + 1) % cols] == digit:
                        self.wrapped_line(vsk, cx, cy, cx+step, cy-step)

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")

    def wrapped_line(self, vsk, x1, y1, x2, y2):
        if x1 < 0 or x1 > 220 or x2 < 0 or x2 > 220:
            x3 = (x1 + x2) / 2
            y3 = (y1 + y2) / 2

            if x1 < 0:
                vsk.line(x1 + 220, y1, x3+220, y3)
            elif x1 > 220:
                vsk.line(x1 - 220, y1, x3-220, y3)
            else:
                vsk.line(x1, y1, x3, y3)

            if x2 < 0:
                vsk.line(x2 + 220, y2, x3+220, y3)
            elif x2 > 220:
                vsk.line(x2 - 220, y2, x3-220, y3)
            else:
                vsk.line(x2, y2, x3, y3)
        else:
            vsk.line(x1, y1, x2, y2)

if __name__ == "__main__":
    PiSketch.display()
