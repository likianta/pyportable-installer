class NameConverter:
    
    def __init__(self, raw_name):
        # raw_name is whitespace separated string.
        self._name = raw_name
    
    @property
    def raw(self):
        return self._name
    
    # natual
    
    @property
    def lower_case(self):
        return self._name.lower()
    
    @property
    def upper_case(self):
        return self._name.upper()
    
    @property
    def title_case(self):
        return self._name.title()
    
    # programming
    
    @property
    def snake_case(self):
        return self._name.lower().replace(' ', '_')
    
    @property
    def kebab_case(self):
        return self._name.lower().replace(' ', '-')
    
    @property
    def pascal_case(self):
        return self._name.title().replace(' ', '')
    
    @property
    def camel_case(self):
        if ' ' not in self._name:
            return self._name.lower()
        a, b = self._name.split(' ', 1)
        return a.lower() + b.title()
