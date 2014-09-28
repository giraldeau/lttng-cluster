
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

def recipe_verify(opts, required, errors):
    cmp = DictCmp()
    checker = RecipeChecker(errors)
    cmp.add_listener(checker)
    cmp.compare(opts, required)