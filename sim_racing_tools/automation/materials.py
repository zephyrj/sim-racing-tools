
class BilletSteelCrank(object):
    def __init__(self, quality):
        self.quality = quality

    def max_rpm(self):
        # + 15 = 13100
        # - 15 = 11500
        return 12300

    def max_torque(self):
        pass


class ForgedSteelCrank(object):
    def __init__(self, quality):
        self.quality = quality

    def max_rpm(self):
        pass

    def max_torque(self):
        pass

