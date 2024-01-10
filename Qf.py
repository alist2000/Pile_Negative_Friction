class Qf:
    def __init__(self):
        self.Qf = None

    def calculate_Qf(self):
        pass


class Clay(Qf):
    def __init__(self, cu, sigma):
        super().__init__()
        self.cu = cu
        self.sigma = sigma
        self.Qf = self.calculate_Qf()

    def calculate_Qf(self):
        control = self.cu / self.sigma
        if control < 1:
            alpha = 0.5 * control ** -0.5
        else:
            alpha = 0.5 * control ** -0.25
        return self.cu * alpha


class OtherSoils(Qf):
    def __init__(self, beta, sigma):
        super().__init__()
        self.beta = beta
        self.sigma = sigma
        self.Qf = self.calculate_Qf()

    def calculate_Qf(self):
        qf = self.beta * self.sigma
        return qf


# clay = Clay(70, 192)
# print(clay.Qf)

# sand = OtherSoils(0.29, 28.5)
# print(sand.Qf)
