import copy


class EffectivePressure:
    def __init__(self, gama, h):
        """
        The function initializes the values of gamma and h, creates line data, and generates lines.

        :param gama: The parameter `gama` is a list of gamma primes, which represents the effective soil weight. Each
        element in the list corresponds to the gamma prime value for a specific soil layer
        :param h: The parameter `h` is a list that represents the height of every soil layer. Each element in the list
        corresponds to the height of a specific soil layer
        """
        self.gama = gama
        self.h = h
        self.zeroPressure = 0
        lineData = self.line_data_creator()
        self.lines = self.generate_lines(lineData)

    def line_data_creator(self):
        start_z = 0
        lineData = []
        for slope, z in zip(self.gama, self.h):
            z_range = (start_z, z + start_z)
            start_z = copy.deepcopy(z + start_z)
            lineData.append((slope, z_range))
        return lineData

    @staticmethod
    def generate_lines(line_data):
        lines = []
        y0 = 0
        for slope, x_range in line_data:
            line = LineEquation(slope, x_range, y0)
            lines.append(line)
            y0 = line.calculate_pressure(x_range[-1])

        return lines

    @staticmethod
    def find_line(x, lines):
        for i, line in enumerate(lines):
            if line.x_range[0] <= x <= line.x_range[1]:
                return i
        return None

    def output(self, z):
        line_index = self.find_line(z, self.lines)
        if line_index is not None:
            pressure = self.lines[line_index].calculate_pressure(z)
        else:
            pressure = 0
        return pressure


class LineEquation:
    def __init__(self, slope, x_range, y_intercept=0):
        self.slope = slope
        self.y_intercept = y_intercept  # The y-intercept starts from zero for the first line
        self.x_range = x_range

    def calculate_pressure(self, x):
        return self.slope * (x - self.x_range[0]) + self.y_intercept

# effectiveInstance = EffectivePressure([2, 4, 3], [10, 8, 5])
# p = effectiveInstance.output(20)
# print(p)
