from collections import ChainMap
import copy
import heapq
import math
import Grid


def valid( square: Grid.Square, grid: Grid.Grid):
    con = True
    value = grid.value
    nei_num = grid.nei_num
    una_num = grid.una_num
    ass_nei = grid.ass_nei
    same_num = 0
    for x, y in ass_nei:
        if square[x][y].value == value:
            same_num += 1
    if grid.type == Grid.Type.S:
        if same_num > 1:
            return False
        if same_num == 0:
            if una_num == 0:
                return False
    else:
        if same_num > 2:
            return False
        if same_num < 2:
            if same_num+una_num < 2:
                return False
    if grid.type == Grid.Type.U:
        for x,y in ass_nei:
            con = valid(square,square[x][y])
            if not con:
                return con
    return con


def sort_value(value: list, value_info: dict, loc: tuple):
    """
    :param value:
    :param value_info:
    :param loc:
    :return:
    >>> sort_value(value = ['Y','P'], value_info = {'Y':[(6,2),(6,6),4],'P':[(5,3),(7,7),6]}, loc = (6,3))
    [['Y', 0, 4], ['P', 0, 6]]
    >>> sort_value(value = ['Y'], value_info = {'Y':[(6,2),(6,6),4],'P':[(5,3),(7,7),6]}, loc= (7,3))
    [['Y', 0, 4]]
    """
    if len(value) == 1:
        return [[value[0], 0, value_info[value[0]][2]]]
    sorted_value = []
    for v in value:
        head = value_info[v][0]
        tail = value_info[v][1]
        dis = value_info[v][2]
        dis1 = int(math.fabs(head[0]-loc[0]) + math.fabs(head[1]-loc[1]))
        dis2 = int(math.fabs(tail[0]-loc[0]) + math.fabs(tail[1]-loc[1]))
        dis_max = max(dis1,dis2)
        if dis_max < dis:
            color = [v,0,dis]
        else:
            color = [v,1,dis]
        sorted_value.append(color)
    sorted_value.sort(key= lambda e: (e[1],e[2]))
    return sorted_value


def update_value_info(grid:Grid.Grid,value_info:dict):
    nei = grid.get_ass_nei()
    v = grid.value
    i = 0
    while i< 2:
        if value_info[v][i] in nei:
            value_info[v][i] = grid.index
            head = value_info[v][0]
            tail = value_info[v][1]
            dis = int(math.fabs(head[0]-tail[0]) + math.fabs(head[1]-tail[1]))
            value_info[v][2] = dis
            break
        i += 1

def recover_value_info(value_info:dict,square:Grid.Square,x,y):
    v = square[x][y].value
    nei = square[x][y].get_ass_nei()
    for i,j in nei:
        if square[i][j].value == v:
            if (i,j) not in value_info[v]:
                if (x,y) in value_info[v]:
                    index = value_info[v].index((x,y))
                    value_info[v][index] = (i,j)
                    head = value_info[v][0]
                    tail = value_info[v][1]
                    dis = int(math.fabs(head[0] - tail[0]) + math.fabs(head[1] - tail[1]))
                    value_info[v][2] = dis
                    break

def recover_dom(square:Grid.Square,domain:ChainMap):
    size = square.size
    i = 0
    while i < size:
        j = 0
        while j < size:
            if (i, j) in domain.keys():
                square[i][j].num_do = len(domain[(i, j)])
            j += 1
        i += 1


def forwardchecking(square:Grid.Square, domain: ChainMap, index):
    aff = square[index[0]][index[1]].get_aff_nei()
    for x, y in aff:
        grid = square[x][y]
        value = copy.deepcopy(domain[(x,y)])
        for v in value:
            grid.set_value(v,square)
            if not valid(square,grid):
                domain[(x,y)].remove(v)
                grid.num_do -= 1
                if not domain[(x,y)]:
                    grid.remove_value(square)
                    return False
            grid.remove_value(square)
    return True

def arc_consistency(square:Grid.Square,domain:ChainMap,index):
    arc = set()
    aff = square[index[0]][index[1]].get_aff_nei()
    for x, y in aff:
        arc.add((index,(x,y)))
    while arc:
        index1,index2 = arc.pop()
        if revise_domain(square,domain,index1,index2):
            if not domain[index2]:
                return False
            aff = square[index2[0]][index2[1]].get_aff_nei().difference({index1})
            for x, y in aff:
                arc.add((index1, (x, y)))
    return True

def revise_domain(square:Grid.Square,domain:ChainMap,index1,index2):
    revise = False
    if square[index1[0]][index1[1]].value:
        grid = square[index2[0]][index2[1]]
        value = copy.deepcopy(domain[index2])
        for v in value:
            grid.set_value(v,square)
            if not valid(square,grid):
                domain[index2].remove(v)
                grid.num_do -= 1
                revise = True
            grid.remove_value(square)
    else:
        grid1 = square[index1[0]][index1[1]]
        grid2 = square[index2[0]][index2[1]]
        value = copy.deepcopy(domain[index2])
        for v2 in value:
            grid2.set_value(v2,square)
            grid2.type = Grid.Type.A
            has = False
            for v1 in domain[index1]:
                grid1.set_value(v1,square)
                if valid(square,grid1):
                    grid1.remove_value(square)
                    has = True
                    break
                grid1.remove_value(square)
            if not has:
                domain[index2].remove(v2)
                grid2.num_do -= 1
                revise = True
            grid2.remove_value(square)
            grid2.type = Grid.Type.U
    return revise


def arc_ini(square:Grid.Square,domain:ChainMap,un_var:list):
    arc = set()
    for s in un_var:
        aff = s.get_aff_nei()
        for i,j in aff:
            arc.add((s.index,(i,j)))
    while arc:
        index1,index2 = arc.pop()
        if revise_domain(square,domain,index1,index2):
            if not domain[index2]:
                return False
            aff = square[index2[0]][index2[1]].get_aff_nei().difference({index1})
            for x, y in aff:
                arc.add((index1, (x, y)))
    return True


def dumb_search(un_var: list, square: Grid.Square, domain: ChainMap)->tuple:
    att = 0
    solution = dict()
    value_list = []
    order = []
    succ = True
    while un_var:
        grid = un_var.pop()
        if succ:
            value = list(domain[grid.index])
            while value:
                value_list.append(value.pop())
            chain = copy.deepcopy(domain.maps[0])
            domain = domain.new_child(chain)
        elif not domain[grid.index]:
            un_var.append(grid)
            domain = domain.parents
            (x, y) = order.pop()
            grid = square[x][y]
            v = grid.remove_value(square)
            grid.type = Grid.Type.U
            domain[grid.index].remove(v)
            un_var.append(grid)
            del solution[grid.index]
            continue
        v = value_list.pop()
        grid.set_value(v, square)
        att += 1
        if valid(square, grid):
            solution[grid.index] = grid.value
            order.append(grid.index)
            grid.type = Grid.Type.A
            succ = True
        else:
            v = grid.remove_value(square)
            un_var.append(grid)
            domain[grid.index].remove(v)
            succ = False
    return solution,att


def backtracking(un_var: list, square: Grid.Square, domain: ChainMap, value_info:dict):
    att = 0
    solution = dict()
    value_list = []
    order = []
    succ = True
    while un_var:
        if succ:
            heapq.heapify(un_var)
            grid = heapq.heappop(un_var)
            value = list(domain[grid.index])
            sorted_value = sort_value(value, value_info, grid.index)
            while sorted_value:
                value_list.append(sorted_value.pop()[0])
        else:
            grid = un_var.pop()
        if not domain[grid.index]:
            un_var.append(grid)
            domain = domain.parents
            (x, y) = order.pop()
            grid = square[x][y]
            recover_value_info(value_info,square,x,y)
            v = grid.remove_value(square)
            grid.type = Grid.Type.U
            domain[grid.index].remove(v)
            recover_dom(square,domain)
            un_var.append(grid)
            del solution[grid.index]
            continue
        v = value_list.pop()
        grid.set_value(v, square)
        if valid(square, grid):
            att += 1
            grid.type = Grid.Type.A
            chain = copy.deepcopy(domain.maps[0])
            domain = domain.new_child(chain)
            # inference:
            # forwardchecking:
            if forwardchecking(square, domain, grid.index):
            # arc-consistency:
            # if arc_consistency(square,domain,grid.index):
                solution[grid.index] = grid.value
                order.append(grid.index)
                update_value_info(grid,value_info)
                succ = True
            else:
                v = grid.remove_value(square)
                grid.type = Grid.Type.U
                domain = domain.parents
                domain[grid.index].remove(v)
                recover_dom(square,domain)
                un_var.append(grid)
                succ = False
        else:
            v = grid.remove_value(square)
            un_var.append(grid)
            domain[grid.index].remove(v)
            grid.num_do -= 1
            succ = False
    return solution,att
