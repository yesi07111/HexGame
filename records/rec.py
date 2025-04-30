from collections import defaultdict

class GameRecords:
    def __init__(self):
        self.records = defaultdict(lambda: {'wins_j1': 0, 'wins_j2': 0})
        self.load_records()
    
    def load_records(self):
        try:
            with open("records.txt", "r") as f:
                for line in f:
                    players, wins_j1, wins_j2 = line.strip().split(";")
                    j1, j2 = players.split(',')
                    key = tuple(sorted([j1, j2]))
                    self.records[key] = {
                        'wins_j1': int(wins_j1),
                        'wins_j2': int(wins_j2)
                    }
        except FileNotFoundError:
            pass
    
    def save_record(self, winner, loser):
        players = tuple(sorted([winner, loser]))
        if winner == players[0]:
            self.records[players]['wins_j1'] += 1
        else:
            self.records[players]['wins_j2'] += 1
        with open("records.txt", "w") as f:
            for players_pair, stats in self.records.items():
                f.write(f"{','.join(players_pair)};{stats['wins_j1']};{stats['wins_j2']}\n")