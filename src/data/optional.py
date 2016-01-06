
class Optional(object):
    """
    This object represents a computation, which fails.
    """
    def __init__(self):
        self.result = None

    def map(self, f):
        """
        Optional is an (endo)functor.
        If there is a result map will apply the function to the result.

        The following may be expected by the programmer:

        o.map(f).map(g) == o.map(f . g)
        o.map(id) = id

        where . is function composition
        """
        return self

    def join(self):
        return self


    @property
    def hasResult(self):
        return False

    @property
    def extract(self):
        """
        This is an dangerous operation, because a failing computation has no result.
        """
        if self.hasResult:
            return self.result
        else:
            return None

class Result(Optional):
    def __init__(self, result):
        self.result = result

    def map(self, f):
        self.result = f(result)
        return self

    def join(self):
        """
        Join two nested Optionals to one:
        Result(Result) -> Result
        Result(NoResult) -> NoResult
        NoResult -> NoResult
        The last one seems to be strange, but if the type of the computation
        is Optional(Optional a) it can happen.
        """
        if self.result.hasResult():
            self.result = self.result.result
            return self
        else:
            return NoResult()

    @property
    def hasResult(self):
        return True

class NoResult(Optional):
    pass
