import requests
import os
import json
from datetime import datetime

def fetch_scores(user_list=None):
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?groups=50"
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        return None, f"Error fetching data: {e}"

    events = data.get('events', [])
    all_today_games = []
    matches = []

    for event in events:
        competitions = event.get('competitions', [{}])[0]
        competitors = competitions.get('competitors', [])
        if len(competitors) < 2: continue

        t1 = competitors[0].get('team', {}).get('displayName')
        t2 = competitors[1].get('team', {}).get('displayName')
        game_str = f"{t2} @ {t1}"
        all_today_games.append(game_str)

        if user_list:
            for requested in user_list:
                t1_lower = t1.lower()
                t2_lower = t2.lower()
                r_lower = requested.lower()
                
                def is_match(team_name, query):
                    name_parts = team_name.lower().split()
                    query_parts = query.lower().split()
                    if query.lower() == 'florida' and 'state' in name_parts:
                        return False
                    if query.lower() == 'miami' and 'ohio' in name_parts:
                        return False
                    return all(q in name_parts for q in query_parts)

                if is_match(t1, requested) or is_match(t2, requested):
                    matches.append(event)
                    break
    
    return all_today_games, matches

def format_output(events):
    live_games = []
    scheduled_games = []
    final_games = []

    for event in events:
        status_type = event.get('status', {}).get('type', {}).get('state')
        competitions = event.get('competitions', [{}])[0]
        competitors = competitions.get('competitors', [])
        
        rank1 = competitors[0].get('curatedRank', {}).get('current', 99)
        rank2 = competitors[1].get('curatedRank', {}).get('current', 99)
        t1_display = f"#{rank1} {competitors[0]['team']['displayName']}" if rank1 < 99 else competitors[0]['team']['displayName']
        t2_display = f"#{rank2} {competitors[1]['team']['displayName']}" if rank2 < 99 else competitors[1]['team']['displayName']

        if competitors[1].get('homeAway') == 'away':
            away_team, away_score = t2_display, competitors[1].get('score')
            home_team, home_score = t1_display, competitors[0].get('score')
        else:
            away_team, away_score = t1_display, competitors[0].get('score')
            home_team, home_score = t2_display, competitors[1].get('score')

        win_prob = 0.5
        prob = competitions.get('situation', {}).get('lastPlay', {}).get('probability', {})
        if 'homeWinPercentage' in prob: win_prob = prob['homeWinPercentage']
        
        broadcasts = competitions.get('broadcasts', [])
        tv_names = broadcasts[0].get('names', ["N/A"]) if broadcasts else ["N/A"]
        
        game_data = {
            "awayTeam": away_team, "awayScore": away_score,
            "homeTeam": home_team, "homeScore": home_score,
            "status": event.get('status', {}).get('type', {}).get('detail'),
            "tv": ", ".join(tv_names), "winProb": win_prob, "state": status_type
        }

        if status_type == 'in': live_games.append(game_data)
        elif status_type == 'pre': scheduled_games.append(game_data)
        else: final_games.append(game_data)

    live_games.sort(key=lambda x: abs(x['winProb'] - 0.5))
    all_filtered = live_games + scheduled_games + final_games
    
    json_data = {"lastUpdated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "games": all_filtered}
    md_output = f"# 🏀 NCAAB Scoreboard\n*Updated: {json_data['lastUpdated']}*\n\n| Matchup | Score | Status | TV |\n| :--- | :--- | :--- | :--- |\n"
    for g in all_filtered:
        md_output += f"| {g['awayTeam']} @ {g['homeTeam']} | {g['awayScore']} - {g['homeScore']} | {g['status']} | {g['tv']} |\n"
    
    return md_output, json_data

if __name__ == '__main__':
    # Today's target list from Pat
    current_list = [
        "Virginia", "Duke", "Missouri", "Mississippi St.", "Vanderbilt", "Kentucky",
        "Louisville", "Clemson", "San Diego St.", "New Mexico", "UCLA", "Minnesota",
        "Oklahoma St.", "Cincinnati", "Texas", "Texas A&M", "Texas Tech", "Iowa St.",
        "Nebraska", "USC", "Kansas", "Arizona", "BYU", "West Virginia",
        "Providence", "Creighton", "Alabama", "Tennessee", "SMU", "Stanford",
        "Villanova", "St. John's", "Baylor", "UCF", "Arkansas", "Florida",
        "Virginia Tech", "North Carolina", "Gonzaga", "Saint Mary's"
    ]
    
    all_today, matched_events = fetch_scores(current_list)
    md, js = format_output(matched_events)
    
    if md:
        with open('SCOREBOARD.md', 'w') as f: f.write(md)
        with open('scores.json', 'w') as f: json.dump(js, f, indent=4)
        print("Updated Scoreboard files.")
