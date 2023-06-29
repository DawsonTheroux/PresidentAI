import sqlite3
import re


class Leaderboard:
    def __init__(self):
        self.con = sqlite3.connect("leaderboard.db")
        self.position_info={"President":        {"index": 1, "header": "president"},
                            "Vice President":   {"index": 2, "header": "vp"},
                            "Neutral 1":        {"index": 3, "header": "neutral1"},
                            "Neutral 2":        {"index": 4, "header": "neutral2"},
                            "Vice Ass":         {"index": 5, "header": "va"},
                            "Ass":              {"index": 6, "header": "ass"},}


    def create_leaderboard_table(self):
        cur = self.con.cursor()
        cur.execute("CREATE TABLE Leaderboard(name, num_president, num_vp, num_neutral1, num_neutral2, num_va, num_ass)")
        self.con.commit()
        
    def create_history_table(self):
        cur = self.con.cursor()
        cur.execute("CREATE TABLE Game_History(date, president, vp, neutral1, neutral2, va, ass)")
        self.con.commit()

    def fetch_player(self, player_name):
        # Checks if the player exists, if not then adds it.
        # Returns the values stored for the player
        cur = self.con.cursor()
        cur.execute(f"SELECT * from Leaderboard WHERE name='{player_name}'")
        player_entry = cur.fetchone()

        if player_entry == None:
            player_entry = (player_name, 0, 0, 0, 0, 0, 0)
            cur.execute(f"INSERT INTO Leaderboard VALUES {player_entry}")
            self.con.commit()
            print("Didn't find entry creating new entry")
        
        return player_entry

    def update_score(self, player_name, position):
        # Position will be a value from 
        cur = self.con.cursor()
        player_entry = self.fetch_player(player_name)
        column_to_update = f"num_{self.position_info[position]['header']}"
        new_value= player_entry[self.position_info[position]["index"]] + 1
        command = f"UPDATE Leaderboard SET {column_to_update}={new_value} WHERE name='{player_name}'"
        print(f"The command: {command}")
        cur.execute(command)
        self.con.commit()
        print("Updated player")
    
    def add_history(self, standings):
        # Standings is an array of dicitonaries.
        #       dict: {"result": <position>, "name": <player_name>}
        standings_dict = {}
        for player in standings:
            standings_dict[player["position"]] = player["name"]

        cur = self.con.cursor()    
        #game_entry = (sqlite3.datetime(), standings_dict["President"], standings_dict["Vice President"], standings_dict["Neutral 1"], standings_dict["Neutral 2"], standings_dict["Vice Ass"], standings_dict["Ass"])
        cur.execute(f"INSERT INTO Game_History VALUES (datetime('now', 'localtime'), '{standings_dict['President']}', '{standings_dict['Vice President']}', '{standings_dict['Neutral 1']}', '{standings_dict['Neutral 2']}', '{standings_dict['Vice Ass']}', '{standings_dict['Ass']}')")
        self.con.commit()


    def add_game_to_db(self, standings):
        # Standings is an array of dicitonaries.
        #       dict: {"position": <position>, "name": <player_name>}

        # Add the game to the history table
        self.add_history(standings)

        # Update the names in the leaderboard
        for player in standings:
            # Don't add if it matches the following regex:

            if re.search("^AI \([0-9]\)", player["name"]) == None:
                self.update_score(player["name"], player["position"])
        

        print("\n\nDONE adding game to history and updating leaderboard")
        print("Printing Leaderboard table")
        cur = self.con.cursor()
        for row in cur.execute("SELECT * FROM Leaderboard"):
            print(row)
        
        print("\n\nPrinting Game History table")
        for row in cur.execute("SELECT * FROM Game_History"):
            print(row)



        






if __name__ == "__main__":
    # Running this file will initialize the databases
    leaderboard = Leaderboard()
    leaderboard.create_history_table()
    leaderboard.create_leaderboard_table()


