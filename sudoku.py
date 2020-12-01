import itertools


class Cell:

    def __init__(self, row, column, value=None):
        self.row = row
        self.column = column
        self.value = value
        self.possible_values = []
        self.unsolved = True
        self.quad = (self.row // 3, self.column // 3)
        if self.value is None:
            self.possible_values = range(1, 10)
        else:
            self.possible_values = [self.value]
            self.unsolved = False

    def __str__(self):
        if self.unsolved:
            return "<Cell r%sc%s, PS=%s>" % (self.row, self.column, list(self.possible_values))
        else:
            return "<Cell r%sc%s, value=%s>" % (self.row, self.column, self.value)

    def __repr__(self):
        if self.unsolved:
            return "<Cell r%sc%s, PS=%s>" % (self.row, self.column, list(self.possible_values))
        else:
            return "<Cell r%sc%s, value=%s>" % (self.row, self.column, self.value)

    def found_value(self, value):
        self.value = value
        self.unsolved = False
        self.possible_values = [self.value]


def get_row_values(cell, sdict):
    # returns the determined cell values in the row
    rowlist = []
    for other_cell in sdict.values():
        if other_cell.row == cell.row and other_cell.value is not None:
            rowlist.append(other_cell.value)
    return rowlist


def get_col_values(cell, sdict):
    # returns the determined cell values in the column
    collist = []
    for other_cell in sdict.values():
        if other_cell.column == cell.column and other_cell.value is not None:
            collist.append(other_cell.value)
    return collist


def get_quad_values(cell, sdict):
    # returns the determined cell values in the quadrant
    quadlist = []
    for other_cell in sdict.values():
        if other_cell.quad == cell.quad and other_cell.value is not None:
            quadlist.append(other_cell.value)
    return quadlist


def print_sudoku(d):
    print("-" * 31)
    for cell in d:
        # if d[cell].column == 8:
        #     if d[cell].value is None:
        #         print("X")
        #     else:
        #         print(d[cell].value)
        # else:
        #     if d[cell].value is None:
        #         print("X", end='')
        #     else:
        #         print(d[cell].value, end='')
        if d[cell].value is None:
            string = " _ "
        else:
            string = f' {d[cell].value} '
        if d[cell].column in [0, 3, 6]:
            print(f'|{string}', end='')
        elif d[cell].column != 8:
            print(f'{string}', end='')
        else:
            print(f'{string}|')
        if d[cell].row in [2, 5, 8] and d[cell].column == 8:
            print("-" * 31)


def is_valid(d):
    for cell in d:
        d_row = {key: value for (key, value) in d.items() if value.row == d[cell].row}
        d_col = {key: value for (key, value) in d.items() if value.column == d[cell].column}
        d_quad = {key: value for (key, value) in d.items() if value.quad == d[cell].quad}
        for cell_value in range(1, 10):
            row_count = sum([1 for x in d_row if d_row[x].value == cell_value])
            col_count = sum([1 for x in d_col if d_col[x].value == cell_value])
            quad_count = sum([1 for x in d_quad if d_quad[x].value == cell_value])
            if row_count > 1 or col_count > 1 or quad_count > 1:
                return False
    return True


def solve(sudoku):
    original_board = sudoku
    rows = sudoku.split("\n")
    d = {}
    for row in range(9):
        for col in range(9):
            if rows[row][col].isnumeric():
                d["r" + str(row) + "c" + str(col)] = Cell(row, col, int(rows[row][col]))
            else:
                d["r" + str(row) + "c" + str(col)] = Cell(row, col)
    print_sudoku(d)

    # print(get_quad_values(d["r3c0"], d))
    solved = all([not cell.unsolved for cell in d.values()])
    count = 0
    while not solved and is_valid(d) and count < 100:
        print("Run", count + 1)
        for cell in d:
            if d[cell].unsolved:
                # find the values which definitely cannot be, and remove those from possible_values
                impossible_values = get_row_values(d[cell], d) + get_col_values(d[cell], d) + get_quad_values(d[cell],
                                                                                                              d)
                d[cell].possible_values = list(set(d[cell].possible_values) - set(impossible_values))

                if len(d[cell].possible_values) == 1:
                    # if one value remains, you have solved it!
                    d[cell].found_value(d[cell].possible_values[0])
                    print(f'Cell {cell} is {d[cell].value}!')

                else:
                    # if there are still multiple possible values, check if one is unique to the row/col/quadrant
                    Rpossible_values, Cpossible_values, Qpossible_values = [], [], []

                    # find all the possible values of other cells in the R/C/Q
                    for other_cell in d:
                        if d[cell].row == d[other_cell].row and cell != other_cell:
                            Rpossible_values += d[other_cell].possible_values
                        if d[cell].column == d[other_cell].column and cell != other_cell:
                            Cpossible_values += d[other_cell].possible_values
                        if d[cell].quad == d[other_cell].quad and cell != other_cell:
                            Qpossible_values += d[other_cell].possible_values

                    # if any of my possible values is unique to the R/C/Q possible values, then you have solved it!
                    for possible_value in d[cell].possible_values:
                        if (possible_value not in Rpossible_values) or (possible_value not in Cpossible_values) or (
                                possible_value not in Qpossible_values):
                            d[cell].found_value(possible_value)
                            print(f'Cell {cell} is {d[cell].value}!')
                            break

                # search for naked subsets
                # There are n<=5 cells in the same R/C/Q. Each of the cells has some combination of the same n values.
                # Then, no other cell in the R/C/Q cannot be any of those n values.

                d_row_naked = {key: value for (key, value) in d.items() if
                               value.row == d[cell].row and set(value.possible_values).issubset(
                                   set(d[cell].possible_values))}
                d_col_naked = {key: value for (key, value) in d.items() if
                               value.column == d[cell].column and set(value.possible_values).issubset(
                                   set(d[cell].possible_values))}
                d_quad_naked = {key: value for (key, value) in d.items() if
                                value.quad == d[cell].quad and set(value.possible_values).issubset(
                                    set(d[cell].possible_values))}
                # there must be n values in the n cells altogether
                # if len(d_row_naked) >= max(map(len, [x.possible_values for x in d_row_naked.values()])):
                if len(d_row_naked) == len(d[cell].possible_values):
                    for other_cell in d:
                        if d[other_cell].row == d[cell].row and other_cell not in d_row_naked:
                            d[other_cell].possible_values = list(
                                set(d[other_cell].possible_values) - set(d[cell].possible_values))
                if len(d_col_naked) == len(d[cell].possible_values):
                    for other_cell in d:
                        if d[other_cell].column == d[cell].column and other_cell not in d_col_naked:
                            d[other_cell].possible_values = list(
                                set(d[other_cell].possible_values) - set(d[cell].possible_values))
                if len(d_quad_naked) == len(d[cell].possible_values):
                    for other_cell in d:
                        if d[other_cell].quad == d[cell].quad and other_cell not in d_quad_naked:
                            d[other_cell].possible_values = list(
                                set(d[other_cell].possible_values) - set(d[cell].possible_values))

                # search for hidden subsets
                # There are n<=4 cells in the same R/C/Q. If these n cells are the only cells
                # in the R/C/Q to contain n particular possible values, then they for sure contain those values
                # and all other candidates can be removed.

                # todo: tried to do it for any hidden subset. For now, I will just try with hidden pairs
                # d_row_hidden_counter = {
                #     key: sum([list(x.possible_values) for x in d.values() if x.row == d[cell].row], []).count(key)
                #     for key in range(1, 10)}
                # d_col_hidden_counter = {
                #     key: sum([list(x.possible_values) for x in d.values() if x.column == d[cell].column], []).count(key)
                #     for key in range(1, 10)}
                # d_quad_hidden_counter = {
                #     key: sum([list(x.possible_values) for x in d.values() if x.quad == d[cell].quad], []).count(key)
                #     for key in range(1, 10)}
                #
                # for i in range(2, 5):
                #     # loop thru hidden pair, triple, quad
                #     if d_row_hidden_counter.values().count(i) == i:
                #         pass

                # The following did not work. It detected cells with exactly 2 values in common. It did not ensure
                # that other cells in the same family did not share those two values
                """for value1 in d[cell].possible_values:
                    d_row_hidden_value1 = {key: value for (key, value) in d.items() if
                                           value.row == d[cell].row and value1 in value.possible_values}
                    d_col_hidden_value1 = {key: value for (key, value) in d.items() if
                                           value.column == d[cell].column and value1 in value.possible_values}
                    d_quad_hidden_value1 = {key: value for (key, value) in d.items() if
                                            value.quad == d[cell].quad and value1 in value.possible_values}
                    for value2 in list(set(d[cell].possible_values) - set([value1])):
                        d_row_hidden = {key: value for (key, value) in d_row_hidden_value1.items() if
                                        value2 in value.possible_values}
                        d_col_hidden = {key: value for (key, value) in d_col_hidden_value1.items() if
                                        value2 in value.possible_values}
                        d_quad_hidden = {key: value for (key, value) in d_quad_hidden_value1.items() if
                                         value2 in value.possible_values}
                        if len(d_row_hidden) == 2:
                            print("Hidden pair found")
                            for hidden_pair_cell in d_row_hidden:
                                d_row_hidden[hidden_pair_cell].possible_values = [value1, value2]
                        if len(d_col_hidden) == 2:
                            print("Hidden pair found")
                            for hidden_pair_cell in d_col_hidden:
                                d_col_hidden[hidden_pair_cell].possible_values = [value1, value2]
                        if len(d_quad_hidden) == 2:
                            print("Hidden pair found")
                            for hidden_pair_cell in d_quad_hidden:
                                d_quad_hidden[hidden_pair_cell].possible_values = [value1, value2]
                """
                for value1 in d[cell].possible_values:
                    for value2 in list(set(d[cell].possible_values) - {value1}):
                        # for R/C/Qs, find the cells containing BOTH values simultaneously
                        # and and the cells containing EITHER value.
                        # If these lists are the exact same, then we've found a hidden pair.
                        d_row_hidden_both = {key: value for (key, value) in d.items() if
                                             value.row == d[cell].row and (
                                                     value1 in value.possible_values and value2 in value.possible_values)}
                        d_row_hidden_either = {key: value for (key, value) in d.items() if
                                               value.row == d[cell].row and (
                                                       value1 in value.possible_values or value2 in value.possible_values)}
                        d_col_hidden_both = {key: value for (key, value) in d.items() if
                                             value.column == d[cell].column and (
                                                     value1 in value.possible_values and value2 in value.possible_values)}
                        d_col_hidden_either = {key: value for (key, value) in d.items() if
                                               value.column == d[cell].column and (
                                                       value1 in value.possible_values or value2 in value.possible_values)}
                        d_quad_hidden_both = {key: value for (key, value) in d.items() if
                                              value.quad == d[cell].quad and (
                                                      value1 in value.possible_values and value2 in value.possible_values)}
                        d_quad_hidden_either = {key: value for (key, value) in d.items() if
                                                value.quad == d[cell].quad and (
                                                        value1 in value.possible_values or value2 in value.possible_values)}
                        if d_row_hidden_both == d_row_hidden_either and len(d_row_hidden_both) == 2:
                            for hidden_pair_cell in d_row_hidden_both:
                                d_row_hidden_both[hidden_pair_cell].possible_values = [value1, value2]
                        if d_col_hidden_both == d_col_hidden_either and len(d_col_hidden_both) == 2:
                            for hidden_pair_cell in d_col_hidden_both:
                                d_col_hidden_both[hidden_pair_cell].possible_values = [value1, value2]
                        if d_quad_hidden_both == d_quad_hidden_either and len(d_quad_hidden_both) == 2:
                            for hidden_pair_cell in d_quad_hidden_both:
                                d_quad_hidden_both[hidden_pair_cell].possible_values = [value1, value2]

                # next, we will search for pointing pairs to remove row/column candidates.
                # If n<=3 cells in the same quadrant are in a row/column and share a candidate that is not
                # a candidate elsewhere in the quadrant, then that candidate can be removed from all cells in
                # the row/column outside the quadrant.

                # for now, will just do pointing pairs

                d_empty_row_quad = {key: value for (key, value) in d.items() if
                                    value.row == d[cell].row and value.quad == d[cell].quad and value.unsolved}
                d_empty_col_quad = {key: value for (key, value) in d.items() if
                                    value.column == d[cell].column and value.quad == d[cell].quad and value.unsolved}
                for possible_value in d[cell].possible_values:
                    if all([possible_value in x.possible_values for x in d_empty_row_quad.values()]):
                        # if this possible value is in all the cells in this row/quad
                        # Then, check that it's not a candidate elsewhere in the quad
                        d_quad_other_row = {key: value for (key, value) in d.items() if
                                            value.row != d[cell].row and value.quad == d[cell].quad}
                        if all([possible_value not in x.possible_values for x in d_quad_other_row.values()]):
                            # if it is not a candidate elsewhere in the quad
                            # then, remove it from all cells in the row outside the quad
                            for other_cell in d:
                                if other_cell not in d_empty_row_quad and d[other_cell].row == d[cell].row and d[
                                    other_cell].unsolved:
                                    d[other_cell].possible_values = list(
                                        set(d[other_cell].possible_values) - {possible_value})
                    if all([possible_value in x.possible_values for x in d_empty_col_quad.values()]):
                        # if this possible value is in all the cells in this col/quad
                        # Then, check that it's not a candidate elsewhere in the quad
                        d_quad_other_col = {key: value for (key, value) in d.items() if
                                            value.column != d[cell].column and value.quad == d[cell].quad}
                        if all([possible_value not in x.possible_values for x in d_quad_other_col.values()]):
                            # if it is not a candidate elsewhere in the quad
                            # then, remove it from all cells in the col outside the quad
                            for other_cell in d:
                                if other_cell not in d_empty_col_quad and d[other_cell].column == d[cell].column and d[
                                    other_cell].unsolved:
                                    d[other_cell].possible_values = list(
                                        set(d[other_cell].possible_values) - {possible_value})
                # next, we will search for pointing pairs to remove quadrant candidates
                # If n<=3 cells in the same quadrant are in a row/column and share a candidate that is not a candidate
                # elsewhere in the row/column, then that candidate can be removed from all cells in the quadrant.

                # for now, just pointing pairs

                for possible_value in d[cell].possible_values:
                    # generate a list of cells in the row that contain this possible value
                    d_row_possible_value = {key: value for (key, value) in d.items() if
                                            value.row == d[cell].row and possible_value in value.possible_values and
                                            value.unsolved}
                    if all([value.quad == d[cell].quad for value in d_row_possible_value.values()]):
                        # if all those cells are in the same quadrant
                        # then, they can be removed from all other cells in the quadrant
                        for other_cell in d:
                            if d[other_cell].quad == d[cell].quad and other_cell not in d_row_possible_value and d[
                                other_cell].unsolved:
                                d[other_cell].possible_values = list(set(d[other_cell].possible_values) -
                                                                     {possible_value})
                for possible_value in d[cell].possible_values:
                    # generate a list of cells in the col that contain this possible value
                    d_col_possible_value = {key: value for (key, value) in d.items() if
                                            value.column == d[
                                                cell].column and possible_value in value.possible_values and
                                            value.unsolved}
                    if all([value.quad == d[cell].quad for value in d_col_possible_value.values()]):
                        # if all those cells are in the same quadrant
                        # then, they can be removed from all other cells in the quadrant
                        for other_cell in d:
                            if d[other_cell].quad == d[cell].quad and other_cell not in d_col_possible_value and \
                                    d[other_cell].unsolved:
                                d[other_cell].possible_values = list(set(d[other_cell].possible_values) -
                                                                     set([possible_value]))

        solved = all([not cell.unsolved for cell in d.values()])
        count += 1
        # print_sudoku(d)

    # print_sudoku(d)
    print(f'Finished in {count} runs')
    # print(is_valid(d))
    # for cell in d:
    #     print(cell, "has possible values", d[cell].possible_values)


def solve_brute_force(sudoku):
    original_board = sudoku
    rows = sudoku.split("\n")
    d = {}
    for row in range(9):
        for col in range(9):
            if rows[row][col].isnumeric():
                d["r" + str(row) + "c" + str(col)] = Cell(row, col, int(rows[row][col]))
            else:
                d["r" + str(row) + "c" + str(col)] = Cell(row, col)
    print_sudoku(d)
    count = 0
    print("Run", count + 1)
    for cell in d:
        if d[cell].unsolved:
            # find the values which definitely cannot be, and remove those from possible_values
            impossible_values = get_row_values(d[cell], d) + get_col_values(d[cell], d) + get_quad_values(d[cell],
                                                                                                          d)
            d[cell].possible_values = list(set(d[cell].possible_values) - set(impossible_values))

    d_unsolved = {key: value for (key, value) in d.items() if value.unsolved}
    d_unsolved_possible_values = [x.possible_values for x in d_unsolved.values()]
    all_possibilities = itertools.product(*d_unsolved_possible_values)
    length = 1
    for lst in d_unsolved_possible_values:
        length *= len(lst)
    for possibility in all_possibilities:
        print(f'Run {(count + 1) / length:.50%}')
        index = 0
        for cell in d_unsolved:
            d[cell].value = possibility[index]
            if is_valid(d):
                continue
            else:
                break
        if is_valid(d):
            print_sudoku(d)
            return
        count += 1

# EOF
