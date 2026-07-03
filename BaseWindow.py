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

    @classmethod
    def resize_window(cls, width, height) -> tuple[int, int, int, int]:
        """params: The current size of the application window
        \n :RETURNS: updated window child sizes
        """
        return (int(width * cls.size[0]), int(height * cls.size[1]), int(width * cls.position[0]), int(height * cls.position[1]))