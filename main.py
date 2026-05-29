import csv
import os
from datetime import datetime
import requests

GAMES_FILE = "games.txt"
OUTPUT_FILE = "games.csv"

def get_universe_id(place_id):
    url = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return data.get("universeId")

def get_game_data(universe_id, start_time):
    url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    if not data["data"]:
        return None
    game = data["data"][0]
    return {
        "game_id": universe_id,
        "name": game["name"],
        "creator": game["creator"]["name"],
        "creator_type": game["creator"]["type"],
        "playing": game.get("playing", 0),
        "visits": game.get("visits", 0),
        "favorites": game.get("favoritedCount", 0),
        "created": game["created"],
        "updated": game["updated"],
        "checked_at": start_time,  # Пишем время запуска скрипта
    }

def load_ids():
    with open(GAMES_FILE, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_csv(rows):
    file_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "game_id",
                "name",
                "creator",
                "creator_type",
                "playing",
                "visits",
                "favorites",
                "created",
                "updated",
                "checked_at",
            ],
        )
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)

def main():
    # Фиксируем точное время старта скрипта (в формате ГГГГ-ММ-ДД ЧЧ:ММ:СС)
    script_start_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    ids = load_ids()
    rows = []
    for game_id in ids:
        print(f"Checking {game_id}")
        universe_id = get_universe_id(game_id)
        if universe_id is None:
            universe_id = game_id
        data = get_game_data(universe_id, script_start_time)
        if data:
            rows.append(data)
    save_csv(rows)
    print(f"Done. Batch timestamp: {script_start_time}")
if __name__ == "__main__":
    main()
