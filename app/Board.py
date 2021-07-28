

class Board:
    """Represents a board for the game of "Connect 4"

    Attributes:
        grid (List) -   A 1D-grid of length (7*6 = 42) representing the board itself. Since the board in Connect 4
                        consists of 6 rows and 7 columns. Indices [0-6] represents the topmost row, and so on.
                        Each element should be either 1 (RED TOKEN), -1 (YELLOW TOKEN) or 0 (EMPTY)
    """


    def __init__(self):
        self.grid = [0] * 7 * 6


    def insert_token(self, token, column):
        """Inserts a token into the board at provided column.

        :param token (int): Integer representing token colour. 1 is RED, -1 is YELLOW
        :param column (int): Column number to insert the token. Should be in range [0, 6]
        :return (bool): True if insertion successful. False otherwise
        """
        for i in range(35+column, -1, -7):
            if not self.grid[i]:
                self.grid[i] = token
                return True
        return False


    def check_win(self):
        """Performs a brute force checking whether the game continues, or RED/YELLOW wins, or Tie

        :return (None|int): Returns None if the game continues
                            Returns 0 if it is a Tie
                            Returns 1 if RED TOKEN wins
                            Returns -1 if YELLOW TOKEN wins
        """
        # Tie checking
        if all(self.grid):
            return 0
        # Check Horizontally
        for row in range(0, 42, 7):
            for offset in range(4):
                if sum(self.grid[row+offset: row+offset+4]) in (4, -4):
                    return sum(self.grid[row+offset: row+offset+4]) // 4
        # Check vertically.
        for col in range(7):
            for idx in range(col, 15 + col, 7):
                tot = sum(self.grid[idx+offset*7] for offset in range(4) )
                if tot in (4, -4):
                    return tot // 4
        # Check \ and / direction
        for row in range(0,15,7):
            for col in range(4):
                # \ direction
                tot = sum(self.grid[row+col+offset] for offset in range(0,25,8))
                if tot in (4, -4):
                    return tot // 4
                # / direction
                tot = sum(self.grid[row+6-col+offset] for offset in range(0,19,6))
                if tot in (4, -4):
                    return tot // 4
        return None


    def __str__(self):
        """String representation of the board. First line is the column number followed by a linebreak.
        The rest will be the board tokens. Note that emoji is used

        :return (str): String representatin of the board
        """
        res = '0️⃣ 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣\n\n'
        for row in range(6):
            for col in range(7):
                res += '⚪ ' if not self.grid[row*7+col] else '🔴 ' if self.grid[row*7+col] == 1 else '🟡 '
            res += '\n'
        return res
