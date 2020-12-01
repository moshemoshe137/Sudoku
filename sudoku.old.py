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
        return "<Cell r%sc%s, value=%s>" % (self.row, self.column, self.value)

    def __repr__(self):
        return "<Cell r%sc%s, value=%s>" % (self.row, self.column, self.value)

    def found_value(self, value):
        self.value = value
        self.unsolved = False
        self.possible_values = [self.value]


def get_rowlist(cell, sdict):
    rowlist = []
    for other_cell in sdict.values():
        if other_cell.row == cell.row and other_cell.value is not None:
            rowlist.append(other_cell.value)
    return rowlist


def get_collist(cell, sdict):
    collist = []
    for other_cell in sdict.values():
        if other_cell.column == cell.column and other_cell.value is not None:
            collist.append(other_cell.value)
    return collist


def get_quadlist(cell, sdict):
    quadlist = []
    for other_cell in sdict.values():
        if other_cell.quad == cell.quad and other_cell.value is not None:
            quadlist.append(other_cell.value)
    return quadlist


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
    # print(d)
    # print(get_quad_values(d["r3c0"], d))
    solved = all([not cell.unsolved for cell in d.values()])
    print(solved)
    count = 0
    while (not solved) and count < 100:
        for cell in d:
            if d[cell].unsolved:
                # print("Cell", cell, "is unsolved")
                # find the values which definitely cannot be, and remove those from possible_values
                impossible_values = get_rowlist(d[cell], d) + get_collist(d[cell], d) + get_quadlist(d[cell], d)
                d[cell].possible_values = list(set(d[cell].possible_values) - set(impossible_values))

                if len(d[cell].possible_values) == 1:
                    # if one value remains, you have solved it!
                    d[cell].found_value(d[cell].possible_values[0])
                    print("Cell", cell, "is", str(d[cell].value))
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
                            print("Cell", cell, "is", str(d[cell].value))
                            break

                    # todo: if 2 cells have the same 2 possible values, then those 2 numbers for sure go in those 2 cells. No other cell in the R/C/Q can have those 2 values.
                    drow_unsolved = {key: value for (key, value) in d.items() if
                                     value.row == d[cell].row and value.unsolved}
                    dcol_unsolved = {key: value for (key, value) in d.items() if
                                     value.column == d[cell].column and value.unsolved}
                    if len(drow_unsolved) <= 3:
                        drow_unsolved0quad = list(drow_unsolved.values())[0].quad
                        drow_unsolved0possible_valueslen = len(list(drow_unsolved.values())[0].possible_values)
                        if all([x.quad == drow_unsolved0quad for x in drow_unsolved.values()]) and \
                                all([len(x.possible_values) == len(drow_unsolved) for x in drow_unsolved.values()]):
                            # if all the missing values are in the same quadrant
                            # and the possible_values lists are the appropriate size (same size as # missing cells)
                            # Then remove their possible values from other cells in the same quadrant

                            # first, create the remove_list
                            remove_list = []
                            for other_cell in drow_unsolved:
                                remove_list += drow_unsolved[other_cell].possible_values

                            # then, loop thru to find other cells in the quad and remove remove_list from possible_values
                            for other_cell in d:
                                if (drow_unsolved0quad == d[other_cell].quad) and (other_cell not in drow_unsolved):
                                    d[other_cell].possible_values = list(
                                        set(d[other_cell].possible_values) - set(remove_list))
                    if len(dcol_unsolved) <= 3:
                        dcol_unsolved0quad = list(dcol_unsolved.values())[0].quad
                        if all([x.quad == dcol_unsolved0quad for x in dcol_unsolved.values()]) and \
                                all([len(x.possible_values) == len(dcol_unsolved) for x in dcol_unsolved.values()]):
                            # if all the missing values are in the same quadrant
                            # and the possible_values lists are the appropriate size (same size as # missing cells)
                            # Then remove their possible values from other cells in the same quadrant

                            # first, create the remove_list
                            remove_list = []
                            for other_cell in dcol_unsolved:
                                remove_list += dcol_unsolved[other_cell].possible_values

                            # then, loop thru to find other cells in the quad and remove remove_list from
                            # possible_values
                            for other_cell in d:
                                if (dcol_unsolved0quad == d[other_cell].quad) and (other_cell not in dcol_unsolved):
                                    d[other_cell].possible_values = list(
                                        set(d[other_cell].possible_values) - set(remove_list))

        solved = all([not cell.unsolved for cell in d.values()])
        count += 1
        print("Run", count)

        # print out the partial puzzle
        # for cell in d:
        #     if d[cell].column == 8:
        #         if d[cell].value is None:
        #             print("X")
        #         else:
        #             print(d[cell].value)
        #     else:
        #         if d[cell].value is None:
        #             print("X", end='')
        #         else:
        #             print(d[cell].value, end='')

    # print out the solved puzzle
    for cell in d:
        if d[cell].column == 8:
            if d[cell].value is None:
                print("X")
            else:
                print(d[cell].value)
        else:
            if d[cell].value is None:
                print("X", end='')
            else:
                print(d[cell].value, end='')

    for cell in d:
        print(cell, "has possible values", d[cell].possible_values)
