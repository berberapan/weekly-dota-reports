import csv
import requests
import time


def get_data_list(week: int) -> list:
    """Takes a week number as a parameter to return a list of match ids saved from the given week"""
    try:
        with open(f"weekly_data/weekly_match_ids/matches_w{week}.txt", newline='') as match_ids_file:
            match_id_list = [int(match[0]) for match in csv.reader(match_ids_file)]
            return match_id_list
    except FileNotFoundError:
        print("No file for that week found. Please check that your input is correct.")


def fetch_match_data(matchid: int) -> dict:
    """Fetches the match data from the OpenDota API for a given match id and returns it as json."""
    api = f"https://api.opendota.com/api/matches/{matchid}"
    response = requests.get(api)
    if response.status_code != 200:
        print(f"Can't fetch data from API. Response code {response.status_code}")
    return response.json()


def create_csv(week: int):
    with open(f'weekly_data/weekly_match_data/data_w{week}.csv', 'a', newline='') as file:
        fieldnames = ['match_id', 'league_id', 'winner', 'dire_team_id', 'radiant_team_id', 'duration', 'total_kills',
                      'kill_diff', 'first_blood', 'fb_time', 'total_towers', 'tower_diff', 'first_tower',
                      'first_tower_time', 'total_roshans', 'first_roshan', 'first_roshan_time', 'total_rax',
                      'first_rax', 'first_rax_time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()


def append_file(week: int, match: dict) -> None:
    n_tower = 11
    n_rax = 6
    with open(f'weekly_data/weekly_match_data/data_w{week}.csv', 'a', newline='') as file:
        fieldnames = ['match_id', 'league_id', 'winner', 'dire_team_id', 'radiant_team_id', 'duration', 'total_kills',
                      'kill_diff', 'first_blood', 'fb_time', 'total_towers', 'tower_diff', 'first_tower',
                      'first_tower_time', 'total_roshans', 'first_roshan', 'first_roshan_time', 'total_rax',
                      'first_rax', 'first_rax_time']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        total_kills = match['radiant_score'] + match['dire_score']
        kill_diff = abs(match['radiant_score'] - match['dire_score'])
        radiant_towers = (bin(match["tower_status_radiant"])[2:]).zfill(n_tower)
        dire_towers = (bin(match['tower_status_dire'])[2:]).zfill(n_tower)
        total_towers = radiant_towers.count('0') + dire_towers.count('0')
        tower_diff = abs(radiant_towers.count('0') - dire_towers.count('0'))
        radiant_rax = (bin(match["barracks_status_radiant"])[2:]).zfill(n_rax)
        dire_rax = (bin(match["barracks_status_dire"])[2:]).zfill(n_rax)
        total_rax = radiant_rax.count('0') + dire_rax.count('0')
        if match['radiant_win']:
            winner = 'radiant'
        else:
            winner = 'dire'

        if match['objectives'] is not None:
            objectives = [obj for obj in match['objectives']]
            player_fb = [obj['player_slot'] for obj in objectives if obj['type'] == 'CHAT_MESSAGE_FIRSTBLOOD']
            if len(player_fb) == 0:
                first_blood = None
                fb_time = None
            elif len(str(player_fb[0])) == 3:
                first_blood = 'dire'
                fb_time_list = [obj["time"] for obj in objectives if obj['type'] == "CHAT_MESSAGE_FIRSTBLOOD"]
                fb_time = fb_time_list[0]
            else:
                first_blood = 'radiant'
                fb_time_list = [obj["time"] for obj in objectives if obj['type'] == "CHAT_MESSAGE_FIRSTBLOOD"]
                fb_time = fb_time_list[0]

            buildings_taken = [obj for obj in objectives if obj['type'] == 'building_kill']
            if 'badguys' in buildings_taken[0]['key']:
                first_tower = 'radiant'
            else:
                first_tower = 'dire'
            first_tower_time = buildings_taken[0]['time']

            roshans_killed = []
            for obj in objectives:
                if obj['type'] == "CHAT_MESSAGE_ROSHAN_KILL":
                    roshans_killed.append(obj)
            total_roshans = len(roshans_killed)
            if len(roshans_killed) > 0:
                if roshans_killed[0]['team'] == 2:
                    first_roshan = 'radiant'
                else:
                    first_roshan = 'dire'
                first_roshan_time = roshans_killed[0]['time']
            else:
                first_roshan = None
                first_roshan_time = None

            rax = [obj for obj in buildings_taken if 'rax' in obj['key']]
            if len(rax) == 0:
                first_rax = None
                first_rax_time = None
            elif 'badguys' in rax[0]['key']:
                first_rax = 'radiant'
                first_rax_time = rax[0]['time']
            else:
                first_rax = 'dire'
                first_rax_time = rax[0]['time']


        else:
            objectives = None
            first_blood = None
            fb_time = None
            first_tower = None
            first_tower_time = None
            total_roshans = None
            first_roshan = None
            first_roshan_time = None
            first_rax = None
            first_rax_time = None

        writer.writerow({
            'winner': winner,
            'match_id': match['match_id'],
            'league_id': match['leagueid'],
            'dire_team_id': match['dire_team_id'],
            'radiant_team_id': match['radiant_team_id'],
            'duration': match['duration'],
            'total_kills': total_kills,
            'kill_diff': kill_diff,
            'first_blood': first_blood,
            'fb_time': fb_time,
            'total_towers': total_towers,
            'tower_diff': tower_diff,
            'first_tower': first_tower,
            'first_tower_time': first_tower_time,
            'total_roshans': total_roshans,
            'first_roshan': first_roshan,
            'first_roshan_time': first_roshan_time,
            'total_rax': total_rax,
            'first_rax': first_rax,
            'first_rax_time': first_rax_time,
        })


if __name__ == "__main__":
    week_user_input = int(input("What week do you want to generate data from? (just add numbers): "))
    match_ids = get_data_list(week_user_input)
    api_requests = 1
    create_csv(week_user_input)

    for match in match_ids:
        if api_requests % 30 == 0:
            time.sleep(90)
        json_data = fetch_match_data(match)
        append_file(week_user_input, json_data)
        api_requests += 1
