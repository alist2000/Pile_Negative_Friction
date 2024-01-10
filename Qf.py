class Qf:
    def __init__(self):
        self.Qf = None

    def calculate_Qf(self):
        pass


class Clay(Qf):
    def __init__(self, cu, sigma, max_qf):
        super().__init__()
        self.cu = cu
        self.sigma = sigma
        self.max_qf = max_qf
        self.Qf = self.calculate_Qf()

    def calculate_Qf(self):
        control = self.cu / self.sigma
        if control < 1:
            alpha = 0.5 * control ** -0.5
        else:
            alpha = 0.5 * control ** -0.25
        qf = self.cu * alpha
        if qf < self.max_qf:
            return qf
        else:
            return self.max_qf


class OtherSoils(Qf):
    def __init__(self, beta, sigma, max_qf):
        super().__init__()
        self.beta = beta
        self.sigma = sigma
        self.max_qf = max_qf
        self.Qf = self.calculate_Qf()

    def calculate_Qf(self):
        qf = self.beta * self.sigma
        if qf < self.max_qf:
            return qf
        else:
            return self.max_qf



# clay = Clay(70, 192, 67)
# print(clay.Qf)
#
# sand = OtherSoils(0.37, 252, 81)
# print(sand.Qf)
