import copy

from effectivePressure import EffectivePressure
from Qf import Clay, OtherSoils
from Qs import Qs
from Rn import Rn
from plot import Plot
import numpy as np


class MainCalc:
    def __init__(self, gama, h, max_qf_list, beta_or_cu, beta_or_cu_num, d_pile, Qd, delta=0.1):
        self.gama = gama
        self.h = h
        self.max_qf_list = max_qf_list
        self.beta_or_cu = beta_or_cu
        self.beta_or_cu_num = beta_or_cu_num
        self.d_pile = d_pile
        self.Qd = Qd
        self.delta = delta
        effectivePressure = EffectivePressure(self.gama, self.h)
        h_total = sum(h)
        Qs_list = []
        self.h_list = []
        qs_zero = 0
        for i in np.arange(0, h_total + delta, self.delta):
            pressure, lineIndex = effectivePressure.output(i)
            max_qf = self.max_qf_list[lineIndex]
            if not max_qf:
                max_qf = float("inf")
            if beta_or_cu[lineIndex] == "beta":
                beta = self.beta_or_cu_num[lineIndex]
                qf = OtherSoils(beta, pressure, max_qf=max_qf)
            else:
                cu = self.beta_or_cu_num[lineIndex]
                qf = Clay(cu, pressure, max_qf)
            qs = Qs(qf.Qf, self.d_pile, self.delta, qs_zero)
            qs_zero = copy.deepcopy(qs.Qs)
            Qs_list.append(qs.Qs)
            self.h_list.append(i)

        Rn = Qs_list[-1]
        self.rn_qs = []
        self.qs_qd = []

        for qsItem in Qs_list:
            self.rn_qs.append(Rn - qsItem)
            self.qs_qd.append(qsItem + self.Qd)


# main = MainCalc([19, 10, 10], [8, 10, 4], [67, 0, 81], ["beta", "cu", "beta"], [0.29, 70, 0.37], 1, 700, 1)
# print(main.rn_qs)
# print(main.qs_qd)
# print(main.h_list)
#
# plot = Plot(main.h_list, main.rn_qs, main.qs_qd)
# print(plot.effective_depth)
