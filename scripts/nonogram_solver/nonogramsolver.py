# seems to solve the nonogram correctly, but together with the table to mask it is not revealing the expected hidden message.

from collections import deque


def parse_table(table_str):
    """Convert a whitespace separated table string into a 2D list."""
    rows = []
    for raw_line in table_str.strip().splitlines():
        tokens = raw_line.strip().split()
        if tokens:
            rows.append(tokens)
    return rows


class NonogramSolver:
    def __init__(self, row_clues, col_clues):
        self.row_clues = row_clues
        self.col_clues = col_clues
        self.height = len(row_clues)
        self.width = len(col_clues)
        # Board state: None = unknown, 1 = filled, 0 = empty
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]

    def generate_possibilities(self, line_length, clues, current_line_state):
        """Return every arrangement that matches the clues and the known cells."""
        memo = {}

        def recurse(index, clue_idx):
            key = (index, clue_idx)
            if key in memo:
                return memo[key]

            arrangements = []

            if clue_idx == len(clues):
                remaining = line_length - index
                tail = []
                for offset in range(remaining):
                    cell = current_line_state[index + offset]
                    if cell == 1:
                        memo[key] = []
                        return memo[key]
                    tail.append(0)
                arrangements.append(tail)
                memo[key] = arrangements
                return arrangements

            block_size = clues[clue_idx]
            remaining_clues = clues[clue_idx + 1:]
            min_remaining_space = sum(remaining_clues) + len(remaining_clues)
            max_start = line_length - block_size - min_remaining_space

            for start_pos in range(index, max_start + 1):
                # Validate the gap before the block
                gap_conflict = False
                for gap_index in range(index, start_pos):
                    if current_line_state[gap_index] == 1:
                        gap_conflict = True
                        break
                if gap_conflict:
                    continue

                # Validate the block itself
                block_conflict = False
                for block_index in range(block_size):
                    cell = current_line_state[start_pos + block_index]
                    if cell == 0:
                        block_conflict = True
                        break
                if block_conflict:
                    continue

                next_index = start_pos + block_size
                prefix = [0] * (start_pos - index) + [1] * block_size

                if clue_idx < len(clues) - 1:
                    if next_index >= line_length:
                        continue
                    if current_line_state[next_index] == 1:
                        continue
                    suffixes = recurse(next_index + 1, clue_idx + 1)
                    gap_extension = [0]
                else:
                    suffixes = recurse(next_index, clue_idx + 1)
                    gap_extension = []

                for suffix in suffixes:
                    arrangements.append(prefix + gap_extension + suffix)

            memo[key] = arrangements
            return arrangements

        return recurse(0, 0)

    def solve(self):
        print(f"Solving {self.width}x{self.height} grid...")
        solved = self._search()

        # Verify each row matches its clues
        for row_idx, clues in enumerate(self.row_clues):
            row = self.board[row_idx]
            segments = []
            count = 0
            
            for cell in row:
                if cell == 1:
                    count += 1
                elif count > 0:
                    segments.append(count)
                    count = 0
            
            if count > 0:
                segments.append(count)
            
            if segments != clues:
                print(f"Row {row_idx} does not match clues: got {segments}, expected {clues}")
            
            return False

        # Verify each column matches its clues
        for col_idx, clues in enumerate(self.col_clues):
            col = [self.board[row_idx][col_idx] for row_idx in range(self.height)]
            segments = []
            count = 0
            for cell in col:
                if cell == 1:
                    count += 1
                elif count > 0:
                    segments.append(count)
                    count = 0
            
            if count > 0:
                segments.append(count)
            
            if segments != clues:
                print(f"Column {col_idx} does not match clues: got {segments}, expected {clues}")
            
            return False

        if not solved:
            print("Error: No solution found.")
        return solved

    def _search(self):
        if not self._deduce():
            return False

        if self._is_solved():
            return True

        guess = self._select_guess_line()
        if guess is None:
            return False

        is_row, idx, possibilities = guess
        if not possibilities:
            return False

        for candidate in possibilities:
            snapshot = [row[:] for row in self.board]
            if not self._apply_line(is_row, idx, candidate):
                self.board = snapshot
                continue
            if self._search():
                return True
            self.board = snapshot

        return False

    def _deduce(self):
        queue = deque([(True, i) for i in range(self.height)] + [(False, i) for i in range(self.width)])

        while queue:
            is_row, idx = queue.popleft()
            current_line = self._get_line(is_row, idx)
            if None not in current_line:
                continue

            clues = self.row_clues[idx] if is_row else self.col_clues[idx]
            line_length = self.width if is_row else self.height
            possibilities = self.generate_possibilities(line_length, clues, current_line)

            if not possibilities:
                return False

            consensus = [None] * line_length
            for i in range(line_length):
                candidate = possibilities[0][i]
                if all(p[i] == candidate for p in possibilities):
                    consensus[i] = candidate

            for i, value in enumerate(consensus):
                if value is None:
                    continue

                if is_row:
                    current_value = self.board[idx][i]
                    if current_value is not None and current_value != value:
                        return False
                    if current_value != value:
                        self.board[idx][i] = value
                        if (False, i) not in queue:
                            queue.append((False, i))
                else:
                    current_value = self.board[i][idx]
                    if current_value is not None and current_value != value:
                        return False
                    if current_value != value:
                        self.board[i][idx] = value
                        if (True, i) not in queue:
                            queue.append((True, i))

        return True

    def _select_guess_line(self):
        best_line = None
        best_possibilities = None

        for idx in range(self.height):
            line = self.board[idx]
            if None not in line:
                continue
            possibilities = self.generate_possibilities(self.width, self.row_clues[idx], line)
            if not possibilities:
                return None
            if best_possibilities is None or len(possibilities) < len(best_possibilities):
                best_line = (True, idx)
                best_possibilities = possibilities

        for idx in range(self.width):
            column = [self.board[r][idx] for r in range(self.height)]
            if None not in column:
                continue
            possibilities = self.generate_possibilities(self.height, self.col_clues[idx], column)
            if not possibilities:
                return None
            if best_possibilities is None or len(possibilities) < len(best_possibilities):
                best_line = (False, idx)
                best_possibilities = possibilities

        if best_line is None or best_possibilities is None:
            return None

        return best_line[0], best_line[1], best_possibilities

    def _get_line(self, is_row, idx):
        if is_row:
            return self.board[idx][:]
        return [self.board[r][idx] for r in range(self.height)]

    def _apply_line(self, is_row, idx, values):
        if is_row:
            for i, value in enumerate(values):
                current = self.board[idx][i]
                if current is not None and current != value:
                    return False
            for i, value in enumerate(values):
                self.board[idx][i] = value
        else:
            for i, value in enumerate(values):
                current = self.board[i][idx]
                if current is not None and current != value:
                    return False
            for i, value in enumerate(values):
                self.board[i][idx] = value
        return True

    def _is_solved(self):
        return all(None not in row for row in self.board)

    def print_board(self):
        print("\nFinal Image:\n")
        for r in range(self.height):
            line = ""
            for c in range(self.width):
                value = self.board[r][c]
                if value == 1:
                    line += "██"
                elif value == 0:
                    line += "  "
                else:
                    line += "??"
            print(line)

    def apply_mask(self, table_grid, placeholder=" "):
        """Overlay the solved mask onto the provided table grid."""
        if len(table_grid) != self.height:
            raise ValueError("Table height does not match puzzle height")
        for row in table_grid:
            if len(row) != self.width:
                raise ValueError("Table width does not match puzzle width")

        masked = []

        for r in range(self.height):
            masked_row = []

            for c in range(self.width):
                if self.board[r][c] == 0:
                    masked_row.append(table_grid[r][c])
                else:
                    masked_row.append(placeholder)

            masked.append(masked_row)
            
        return masked

    def print_masked_table(self, masked_table):
        print("\nMasked Table:\n")
        for row in masked_table:
            print(" ".join(row))


# --- DATA FROM IMAGE ---
row_clues = [
    [1, 1, 4, 5, 2],
    [1, 3, 2, 4, 2, 1],
    [2, 6, 1, 4, 7, 1],
    [3, 2, 2, 1, 2, 3, 1],
    [3, 3, 2, 4, 1, 5, 1],
    [2, 3, 1, 4, 5, 2, 2],
    [1, 2, 3, 1, 3, 5, 1, 3],
    [1, 6, 1, 1, 3, 3, 1, 1],
    [1, 6, 3, 2, 5],
    [5, 4, 3, 2, 1, 3],
    [1, 2, 2, 1, 10, 1],
    [3, 11, 3, 1, 2],
    [1, 2, 2, 1, 1, 1, 3, 2],
    [1, 1, 1, 3, 1, 2, 8, 1],
    [6, 4, 1, 1, 2, 3],
    [3, 3, 1, 6, 1, 2, 2],
    [3, 1, 6, 1, 5],
    [1, 1, 1, 4, 4, 1, 2],
    [1, 5, 1, 3, 3, 1, 2],
    [1, 1, 8, 1, 3, 3, 5],
    [1, 1, 5, 1, 3, 2, 1],
    [1, 3, 11, 2, 1],
    [1, 3, 4, 4, 2, 1, 2, 2],
    [1, 3, 2, 2, 2, 2, 5],
    [1, 5, 1, 1, 2, 1],
    [2, 1, 4, 5, 2, 1, 4],
    [1, 2, 7, 12],
    [3, 3, 4, 4, 2],
    [3, 4, 1, 1, 2, 4, 2],
    [1, 2, 1, 2, 1, 6]
]

col_clues = [
    [4, 3, 4, 1],
    [2, 2, 2, 8, 1, 1],
    [5, 1, 1, 3, 1, 2],
    [7, 1, 2, 3, 6, 5],
    [2, 1, 3, 1, 1, 3, 2],
    [1, 4, 2, 3, 3, 2, 2],
    [6, 1, 3, 6],
    [1, 7, 11, 1, 2, 2],
    [1, 1, 3, 1, 2, 1, 2, 2],
    [8, 1, 4, 2, 3, 1],
    [4, 2, 1, 2, 2, 2, 3, 1],
    [1, 1, 4, 1, 2, 1, 2, 1],
    [1, 1, 3, 1, 1, 1, 3, 1, 2, 4, 1],
    [1, 4, 1, 1, 2, 2, 3],
    [6, 6, 6, 4],
    [2, 2, 5, 1, 6],
    [2, 5, 1, 1, 3, 1, 2, 2],
    [3, 15, 3],
    [2, 2, 1, 3, 3, 4],
    [1, 1, 2, 3, 4, 1, 1, 4],
    [1, 8, 2, 5, 2],
    [1, 1, 3, 2, 1, 1, 4, 2, 2, 1],
    [1, 2, 1, 3, 1, 2, 4, 3, 1],
    [1, 4, 1, 1, 2, 1, 1, 1, 2],
    [7, 1, 2, 1, 5, 1, 2],
    [2, 1, 1, 3, 6, 1, 1, 2],
    [2, 3, 7, 1, 1, 2, 2],
    [1, 3, 2, 2, 3, 3, 2],
    [1, 4, 2, 1, 3, 2, 4],
    [5, 3, 2, 4],
]

table = '''
. . . . 6 3 . . . . . . . . . . . . E . . . . . . . . 0 . .
N . . . . . . . . . . . . . . . . . . 0 . . . . . . . . . .
. . 4 . . . . . . . . . . . . . . . . . . . . . . . . . 9 .
. . . . . 2 . . 5 . . . . . . . . . . . . 1 . . . . . . . .
. . . . . . . . . . . . . . . . . 7 . . . . . . . . . . . .
4 . . . . . . . . . . . . . . . . . . . . . 1 . . . . . . E
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
. 6 . . . . . . . . . . 2 . . . . . N . . . . . . . . . . .
. . . . . 3 . . . . . . . . . . . . . . . . 3 . . . . . . 0
. . . . . . . . 3 . . . . . . . . . 4 . . 6 . 1 . 1 . . . .
E . . . . . . . . 2 . . . . . . . . . . . . . . . . . . . .
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
. . . . . . . . . . . 6 . 7 . . 0 . . . . 3 . . . . . . . .
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
. . . . . . . . . . . . . 5 . . 2 . . . . 3 . . . . . . 1 1
0 . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
. . . . . . 6 . . . . . . . . . . . 7 . . . . . . . . . . .
. . . . 4 . 3 . . . . . . . . . . . . . . 3 . . 8 . . . . .
1 . . . . . . . . 8 . 7 . . . . . . . . . . . . 9 . 2 . . 3
1 . 2 . . . . . . . . . . . . . . . . . . . . . . . . . . .
. . . . N . . . . . . . . . . . . . 3 . . . . . . . . . . .
. 3 . . . . . . . . . . . . . . . . . . . . . . . . . . . .
. . . . . . . . . . . . . . . . . . . N . . 3 . . . . . . .
. . . . . . . . . . . 1 . . . . . . . 4 . . . . . . . . . .
. . . . . 9 . . . . . . . . 3 . 6 . . . . . . 1 . 5 . . . 7
. . 7 . . . . . . . . . . . . . . . . . E 0 . . . 1 . . . .
1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
1 . . . . 8 . . . . . . . . . . . 8 . . . . . . . . . . . .
. . . . . . . . . . . . . . . . . . . . . . . . . . . 8 . .
. 0 E . . . . . . 6 . . . . . . . . . . . . . . . . . . . .
'''


if __name__ == "__main__":
    table_grid = parse_table(table)
    solver = NonogramSolver(row_clues, col_clues)
    solved = solver.solve()
    solver.print_board()

    try:
        masked = solver.apply_mask(table_grid, placeholder=" ")
    except ValueError as exc:
        print(f"\nCould not apply mask: {exc}")
    else:
        solver.print_masked_table(masked)
        hidden_chars = [token for row in masked for token in row if token.strip()]
        if hidden_chars:
            print("\nHidden characters:", "".join(hidden_chars))
        else:
            print("\nNo hidden characters found.")

    