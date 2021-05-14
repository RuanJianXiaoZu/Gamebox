from settings import Setting


class Algorithm:

    def __init__(self, side, coors_plate):
        self.total_value = 0
        self.coors_plate = coors_plate
        self.score_list = Setting.score
        self.side = side

    def values(self):
        for row in self.coors_plate:
            for col in row:
                if col != 0:
                    self.total_value += self.score_list[int(str(col)[0]+str(col)[1])]
        # print(self.total_value)
