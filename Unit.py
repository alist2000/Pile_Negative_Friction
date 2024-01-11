class Unit:
    def __init__(self, unitSystem="Metric"):  # Default unitSystem is set to "Metric"
        self.unitSystem = unitSystem  # Single equal sign for assignment

        if self.unitSystem == "US":
            self.lengthUnit = "ft"
            self.pressureUnit = "psi"
            self.densityUnit = "pci"
            self.forceUnit = "lb"
        elif self.unitSystem == "Metric":
            self.lengthUnit = "m"
            self.pressureUnit = "KPa"
            self.densityUnit = "KN/m3"
            self.forceUnit = "KN"



class A(Unit):
    def __init__(self):
        super().__init__()  # Call the __init__ method of the parent class
        print(self.lengthUnit)


# a_instance = A()
