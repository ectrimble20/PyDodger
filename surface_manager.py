from pygame import Surface


class SurfaceManager(object):
    """
    Builds and caches surface objects for reuse with multiple sprite objects.

    The manager allows us to simply build and cache a surface while the get_surface method
    gives us quick access with just the string key.
    """
    def __init__(self):
        self._surfaces = {}

    def build(self, name, width, height, fill_color):
        surf = Surface([width, height])
        surf.fill(fill_color)
        self._surfaces[name] = surf

    def get_surface(self, name):
        return self._surfaces.get(name, None)
