from enum import Enum
import copy

class Type(Enum):
    U = 0
    S = 1
    A = 2

class Square:
    def __init__(self,size):
        self.size = size
        self.square = []
        for i in range(size):
            self.square.append([])
            for j in range(size):
                self.square[i].append(None)
    def __getitem__(self, key):
        return self.square[key]
    def __setitem__(self,key,value):
        self.square[key] = value


class Grid:
    def __init__(self, x, y, _type: Type, value=None):
        self.index = (x, y)
        self.value = value
        self.type = _type
        self.nei_num = 0
        self.una_num = 0
        self.una_nei = set()
        self.ass_nei = set()
        self.nei = set()
        self.num_do = 0
        self.aff_num = 0
        self.aff_nei_ini = set()
        self.aff_nei = set()
    def set_nei(self,size):
        x = self.index[0]
        y = self.index[1]
        if x-1 >= 0:
            self.nei_num += 1
            self.nei.add((x-1, y))
        if x+1 < size:
            self.nei_num += 1
            self.nei.add((x+1, y))
        if y-1 >= 0:
            self.nei_num += 1
            self.nei.add((x, y-1))
        if y+1 < size:
            self.nei_num += 1
            self.nei.add((x, y+1))
        self.ass_nei.update(self.nei)
    def add_una_nei(self, x, y):
        self.una_num += 1
        self.una_nei.add((x, y))
        self.ass_nei.discard((x, y))

    def reduce_una_nei(self, x, y):
        self.una_num -= 1
        self.una_nei.discard((x, y))
        self.ass_nei.add((x,y))

    def remove_aff_nei(self,x,y):
        self.aff_nei.discard((x, y))
        self.aff_num -= 1

    def add_aff_nei(self, x, y):
        self.aff_nei.add((x,y))
        self.aff_num += 1

    def get_una_nei(self)->set:
        return self.una_nei

    def get_ass_nei(self)->set:
        return self.ass_nei

    def get_nei(self)->set:
        return self.nei

    def get_aff_nei(self)->set:
        return self.aff_nei

    def get_aff_nei_ini(self)->set:
        return self.aff_nei_ini

    def __lt__(self, other):
        if self.num_do < other.num_do:
            return True
        elif self.num_do == other.num_do:
            if self.aff_num > other.aff_num:
                return True

    def set_value(self, value, square: Square):
        self.value = value
        neighbor = self.get_nei()
        aff = self.get_aff_nei_ini()
        for x, y in neighbor:
            square[x][y].reduce_una_nei(*self.index)
        for x, y in aff:
            square[x][y].remove_aff_nei(*self.index)

    def remove_value(self, square: Square):
        v = self.value
        self.value = None
        neighbor = self.get_nei()
        aff = self.get_aff_nei_ini()
        for x, y in neighbor:
            square[x][y].add_una_nei(*self.index)
        for x, y in aff:
            square[x][y].add_aff_nei(*self.index)
        return v

    def set_domain(self,domain: set, square: Square):
        self.num_do = len(domain)
        neighbor = self.get_nei()
        nei_val = set()
        for x,y in neighbor:
            if square[x][y].value:
                nei_val.add(square[x][y].value)
            else:
                self.add_una_nei(x, y)
        if self.una_num <= 1:
            domain.intersection_update(nei_val)
            self.num_do = len(domain)

    def set_aff_nei(self,square:Square):
        self.aff_nei_ini.update(self.una_nei)
        nei = self.get_ass_nei()
        for x, y in nei:
            una = copy.deepcopy(square[x][y].get_una_nei())
            una.discard(self.index)
            self.aff_nei_ini.update(una)
        self.aff_nei = copy.deepcopy(self.aff_nei_ini)
        self.aff_num = len(self.aff_nei)




