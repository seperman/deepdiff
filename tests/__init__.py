class CustomClass:
    def __init__(self, a, b=None):
        self.a = a
        self.b = b

    def __str__(self):
        return "Custom({}, {})".format(self.a, self.b)

    def __repr__(self):
        return self.__str__()


class CustomClassMisleadingRepr(CustomClass):
    def __str__(self):
        return "({}, {})".format(self.a, self.b)


class CustomClass2:
    def __init__(self, prop1=None, prop2=None):
        self.prop1 = prop1 or []
        self.prop2 = prop2 or []

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
