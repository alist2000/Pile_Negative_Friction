import math


class Qs:
    def __init__(self, qf, d_pile, delta, qs_zero=0):
        self.qf = qf
        self.d_pile = d_pile
        self.delta = delta
        self.qs_zero = qs_zero
        self.Qs = self.calculate_Qs()

    def calculate_Qs(self):
        return self.qf * math.pi * self.d_pile * self.delta + self.qs_zero


# qs = Qs(55.625, 1, 0.5, 925)
# print(qs.Qs)
