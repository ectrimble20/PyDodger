class GameTimer(object):
    """
    Fancy dancy timer class that allows me to add timers by name, reset them
    and pull their time values.

    This needs it's update method within the game's update method and you need
    to pass it the delta time in order to accurately track times
    """

    def __init__(self, start_time=0):
        self._run_time = start_time
        self.timers = {}

    def update(self, delta_time):
        self._run_time += delta_time
        if len(self.timers) > 0:
            for k, v in self.timers.items():
                self.timers[k] = v + delta_time
                # print("Timer", k, "at", self.timers[k])

    def add_timer(self, timer_name):
        self.timers[timer_name] = 0

    def set_timer_to_zero(self, timer_name):
        self.timers[timer_name] = 0

    def get_time(self, timer_name=None):
        if timer_name is None:
            return self._run_time
        else:
            return self.timers.get(timer_name, 0)
