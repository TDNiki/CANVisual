class BaseWindow:

    tag = None
    title = ""

    @classmethod
    def setup(cls):
        raise NotImplementedError

    @classmethod
    def update(cls):
        pass