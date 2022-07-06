from . import mpmatching

class Matcher:
    def __init__(self, G, trellis):
        self.G
        self.trellis

    def match(self):
        path_prob, predecessor = mpmatching.viterbi_search(self.G_interp, self.trellis, "start", "target")

        return results