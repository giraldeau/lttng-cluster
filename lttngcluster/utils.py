
class DictCmpListener(object):
    def missing(self, d1, d2, path):
        pass
    def present(self, d1, d2, path):
        pass

class DictCmp(object):
    def __init__(self):
        self._listeners = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def compare(self, ref, sec):
        stack = [(ref, sec, [])]
        while(len(stack) > 0):
            d1, d2, p = stack.pop()
            for k in d1.keys():
                curr = p + [k]
                if not isinstance(d2, dict) or \
                   not d2.has_key(k):
                    self._fire_missing(ref, sec, curr)
                else:
                    self._fire_present(ref, sec, curr)
                    v1 = d1.get(k)
                    v2 = d2.get(k)
                    if isinstance(v1, dict):
                        stack.append((v1, v2, curr))

    def _fire_missing(self, ref, sec, p):
        for l in self._listeners:
            l.missing(ref, sec, p)

    def _fire_present(self, ref, sec, p):
        for l in self._listeners:
            l.present(ref, sec, p)

class RecipeChecker(DictCmpListener):
    def __init__(self, errors):
        self._errors = errors
        super(RecipeChecker, self).__init__()
    def missing(self, d1, d2, path):
        self._errors.add('.'.join(path))

def recipe_verify(opts, required, errors):
    comp = DictCmp()
    checker = RecipeChecker(errors)
    comp.add_listener(checker)
    comp.compare(opts, required)

def coerce_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        x = v.lower()
        if x in ('yes', 'true'):
            return True
        if x in ('no', 'false'):
            return False
    if isinstance(v, int):
        if v == 0:
            return False
        else:
            return True
    raise ValueError('boolean conversion failed: %s' % (v))

def dict_product(params):
    import itertools
    keys = []
    values = []
    for k, v in params.items():
        keys.append(k)
        values.append(v)
    prod = itertools.product(*values)
    for item in prod:
        d = {}
        for k, v in zip(keys, item):
            d[k] = v
        yield d
