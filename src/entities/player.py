class Player:
    def __init__(self, lives: int, score: int = 0) -> None:
        self.lives = lives
        self.score = score
        self.col: int = 0
        self.row: int = 0

    def add_score(self, points: int) -> None:
        self.score += points

    def lose_life(self) -> bool:
        if self.lives > 0:
            self.lives -= 1
            return True
        return False

    def respawn(self, col: int, row: int) -> None:
        pass
