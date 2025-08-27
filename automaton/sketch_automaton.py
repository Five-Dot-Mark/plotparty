import vsketch

def apply_rule(state, rule):
    length = len(state)
    newstate = [False for _ in range(length)]
    for i in range(length):
        a, b, c = state[i-1] if i > 0 else state[length-1], state[i], state[i + 1] if i < length - 1 else state[0]
        bit = 1 << (a * 4 + b * 2 + c)
        newstate[i] = (rule & bit) != 0
    return newstate

class AutomatonSketch(vsketch.SketchClass):
    rule = vsketch.Param(0, 0, 255)
    randomize = vsketch.Param(False)
    bottle_scale = vsketch.Param(False)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("320mm"  if self.bottle_scale else "220mm", "160mm", landscape=False)
        vsk.scale("mm")

        line_width = 2
        spacing = 2.2

        cols = int(220.0 / (line_width + spacing))
        rows = int(160 / 220 * cols)
        vsk.scale(220.0 / cols / (line_width + spacing))

        if self.bottle_scale:
            vsk.scale(320/220, 1)

        state =  [vsk.random(1) > 0.5 if self.randomize else i == int(cols / 2)  for i in range(0, cols)] 

        for b in range(rows):
            for a in range(0, cols):
                if state[a] != 0:
                    vsk.circle(a * (line_width + spacing), b * (line_width + spacing), line_width)
            state = apply_rule(state, self.rule)

        # implement your sketch here
        # vsk.circle(0, 0, self.radius, mode="radius")

    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    AutomatonSketch.display()
