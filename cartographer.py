from math import ceil, exp


def logistic(x):
    # https://en.wikipedia.org/wiki/Logistic_function
    k = 0.2
    f_x = 1 / (1 + exp(-(k*x)))
    return f_x


def equation_of_line(p1, p2):
    if p2[0] == p1[0]:
        # Stops the gradient being infinity
        p2 = (p2[0] - 0.00001, p2[1])
    m = (p2[1] - p1[1]) / (p2[0] - p1[0])
    y_int = p2[1] - m*p2[0]
    return m, y_int


class Cartographer:
    INCREASE_AMOUNT = 1

    def __init__(self, size, square_size, gui_values_signal, starting_grid):
        self.callback_signal = gui_values_signal
        self.square_size = square_size
        self.width = size[0]//self.square_size
        self.height = size[1]//self.square_size

        self.grid = starting_grid if starting_grid is not None else \
            [[0 for _ in range(int(self.width))] for _ in range(int(self.height))]
        self.sigmoid_grid = [list(map(logistic, row)) for row in self.grid]

    def update(self, position, points):
        for point in points:
            from_x = min(point[0], position[0])
            to_x = max(point[0], position[0])

            m, y_int = equation_of_line(point, position)

            # Generate x values to use
            start = [from_x]
            mid_section = range(ceil(from_x / self.square_size), int(to_x // self.square_size))
            apply_square_size = lambda x: x * self.square_size
            mid_section = list(map(apply_square_size, mid_section))
            end = [to_x]
            x_values = start + mid_section + end

            for i in range(len(x_values)-1):
                # Go through each x value at regular y values
                start_y = m * x_values[i] + y_int
                end_y = m * x_values[i+1] + y_int
                if start_y > end_y:
                    start_y, end_y = end_y, start_y
                for y in range(int(start_y//self.square_size), int(end_y//self.square_size+1)):
                    # For each y value in between 2 x values...
                    x = int(x_values[i]//self.square_size)
                    if x < 0 or y < 0 or x >= self.width or y >= self.height:
                        # Point is outside our large rectangle, so ignore it
                        continue

                    self.grid[y][x] -= self.INCREASE_AMOUNT

            # Mark the finish point, but bear in mind that it has already been subtracted once
            x = int(point[0] // self.square_size)
            y = int(point[1] // self.square_size)
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                continue
            self.grid[y][x] += 5 * self.INCREASE_AMOUNT

        self.sigmoid_grid = [list(map(logistic, row)) for row in self.grid]

        self.callback_signal.emit(self.sigmoid_grid)
