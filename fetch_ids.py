import requests
import csv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_tournament_ids() -> list:
    """Get the tournament IDs from a CSV file and put them in a list."""
    with open("reference_data/whitelist.csv", newline='') as tournament_info:
        tournament_ids = [int(tournament['league_id']) for tournament in csv.DictReader(tournament_info)]
        return tournament_ids


def get_time() -> int:
    """Retrieves the date from one week prior and changes the time to 0:00 Great Britain time and returns it as an int in unix format."""
    current_dt = datetime.now()
    adjusted_dt = current_dt.replace(hour=0, minute=0, second=0, tzinfo=ZoneInfo("GB")) - timedelta(weeks=1)
    unix_dt = int(adjusted_dt.timestamp())
    return unix_dt


def get_match_ids(tournaments: list, week_time: int) -> list:
    """Retrieves played matches, filtered by tournament ID and given times,
    and return a list of match IDs."""
    match_id_list = []
    close_time = week_time + 604800  # One week in seconds
    api = "https://api.opendota.com/api/"
    params = {}
    while True:
        response = requests.get(url=f"{api}proMatches", params=params)
        match_data = response.json()
        for match in match_data:
            if match['leagueid'] in tournaments and week_time < match['start_time'] < close_time:
                match_id_list.append(match['match_id'])
        if match_data[-1]['start_time'] < week_time:
            return match_id_list
        else:
            last_match_id = match_data[-1]['match_id']
            params = {'less_than_match_id': last_match_id}


def store_ids(match_ids_list: list) -> None:
    """Takes a list of matches ids and put them in a .txt file"""
    with open(f"weekly_data/weekly_match_ids/matches_w{datetime.now().isocalendar().week - 1}.txt", "w") as file:
        for match in match_ids_list:
            file.write(f"{str(match)}\n")


if __name__ == "__main__":
    tournament_list = get_tournament_ids()
    start_time = get_time()
    match_ids = get_match_ids(tournament_list, start_time)
    store_ids(match_ids)
