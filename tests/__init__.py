def parameterize_cases(argnames, cases):
    """
    This is used for parametrizing pytest test cases.

    argnames: a comma separated string of arguments that the test expects.
    cases: a dictionary of test cases.

    argnames_list = [i.strip() for i in argnames.split(',')]
    ids = list(cases.keys())
    argvalues = [tuple(test_name if k == 'test_name' else i[k - 1] for k in argnames_list) for test_name, i in cases.items()]
    return {'argnames': argnames, 'argvalues': argvalues, 'ids': ids}


    """
    argnames_list = [i.strip() for i in argnames.split(',')]
    if 'test_name' not in argnames_list:
        argnames_list.append('test_name')
    argvalues = [tuple(test_name if (k == 'test_name') else test_dict[k] for k in argnames_list) for test_name, test_dict in cases.items()]
    ids = list(cases.keys())
    return {'argnames': argnames, 'argvalues': argvalues, 'ids': ids}


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

    def __repr__(self):
        return "<CustomClass2 id: {}, prop1: {}, prop2: {}>".format(
            id(self), self.prop1, self.prop2)

    __str__ = __repr__


class PicklableClass:
    def __init__(self, item):
        if item != 'delete':
            self.item = item

    def __reduce__(self):
        if hasattr(self, 'item'):
            item = self.item
        else:
            item = 'delete'
        return (self.__class__, (item, ))

    def __eq__(self, other):
        if hasattr(self, 'item') and hasattr(other, 'item'):
            return self.item == other.item
        if not hasattr(self, 'item') and not hasattr(other, 'item'):
            return True
        return False

    def __str__(self):
        return f"<Picklable: {self.item if hasattr(self, 'item') else 'delete'}>"

    __repr__ = __str__
