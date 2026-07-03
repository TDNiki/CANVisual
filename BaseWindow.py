class BaseWindow:

    tag = None
    title = ""
    data = None

    @classmethod
    def setup(cls):
        raise NotImplementedError

    @classmethod
    def update(cls):
        pass
