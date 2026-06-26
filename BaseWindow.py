class BaseWindow:

    tag = None
    title = ""
    size = (0, 0)
    position = (0, 0)
    data = None

    @classmethod
    def setup(cls):
        raise NotImplementedError

    @classmethod
    def update(cls):
        pass

    @classmethod
    def resize_window(cls, width, height) -> tuple[int, int, int, int]:
        """params: The current size of the application window
        \n :RETURNS: updated window child sizes
        """
        return (width * cls.size[0], height * cls.size[1], width * cls.position[0], height * cls.position[1])