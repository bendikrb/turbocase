__all__ = ["batteryholder", "screws", "keyhole"]


class BasePart:
    description = ""
    _substract = False
    _add = True

    @classmethod
    def get_module(cls):
        ref = cls
        mod = ref.__doc__
        while mod is None:
            rn = ref.__name__
            if rn == 'BasePart':
                raise ValueError("None of the parts in the class hierarchy define a module")
            ref = ref.__base__
            mod = ref.__doc__

        raw = mod.lstrip('\n')
        indent = len(raw) - len(raw.lstrip())
        result = []
        for line in raw.splitlines():
            result.append(line[indent:])
        return '\n'.join(result)

    def _get_base(self):
        ref = self.__class__
        while ref.__doc__ is None:
            ref = ref.__base__
        return ref

    def insert(self, footprint, suffix=None):
        base = self._get_base()
        suffix = suffix or ""
        module_name = base.__name__

        args = []
        for var in vars(base):
            if not var.startswith('_'):
                value = getattr(self, var)
                if not isinstance(value, int) and not isinstance(value, float):
                    continue
                args.append(f'{var}={value}')

        return f'{module_name}{suffix}(' + ', '.join(args) + ');'

    def substract(self, footprint):
        return self.insert(footprint, suffix='_substract')

    @classmethod
    def make_footprint(cls):
        return []
