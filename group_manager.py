from pygame.sprite import Group


class GroupManager(object):
    """
    Manages PyGame sprite groups.

    Using the "add_group" function, it ensures that the order the group is added
    is the order the group is drawn.  This is similar to what LayeredUpdates does
    but allows me to just use the basic PyGame sprite groups.
    """
    def __init__(self):
        self._groups = {}
        self._order = []

    def add_group(self, name):
        self._groups[name] = Group()
        self._order.append(name)

    def insert(self, name, sprite):
        if name in self._groups:
            self._groups[name].add(sprite)

    def delete(self, name, sprite):
        if name in self._groups:
            self._groups[name].remove(sprite)

    def draw(self, surface):
        for n in self._order:
            self._groups[n].draw(surface)

    def count(self, name) -> int:
        if name in self._groups:
            return len(self.get_sprites(name))

    def get_sprites(self, name) -> list:
        if name in self._groups:
            return self._groups[name].sprites()

    def get_raw_group(self, name) -> Group:
        if name in self._groups:
            return self._groups[name]
