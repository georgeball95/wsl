# simulate 24/25 using elo ratings

import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt

from elo import calculate_expected_win_percentage

df = pd.read_csv("data/results_elo_ratings.csv")

df['match_date'] = pd.to_datetime(df['match_date'])
df = df.sort_values(by=['match_date'], ascending=False)

# for later on, calc draw rate

draw_percentage = df['home_result'].tolist().count("D")/len(df)

# get latest ratings

current_teams = ['Manchester City', 'Chelsea', 'Liverpool',
              'Arsenal', 'Everton', 'Tottenham', 'Brighton',
              'West Ham','Manchester Utd', 'Aston Villa',
              'Leicester City', 'Crystal Palace']


latest_ratings = {}

# loop over all (except newly promoted Crystal Palace)

for team in current_teams[:-1]:

    last_match = df[(df["home_team"] == team)|(df["away_team"] == team)].head(1)
    
    if last_match.iloc[0]['home_team'] == team:
        
        latest_ratings[team] = last_match.iloc[0]['home_rating_post']
        
    else:
        
        latest_ratings[team] = last_match.iloc[0]['away_rating_post']

# add Crystal Palace

latest_ratings["Crystal Palace"] = 800.0

# adjustment to give hypothetical improvement to worst teams

# latest_ratings["Crystal Palace"] = 800 * 1.1
# latest_ratings["Leicester City"] = 859.3 *1.1
# latest_ratings["West Ham"] = 869.29 * 1.1
# latest_ratings["Brighton"] = 869.73 * 1.1

# for all 2024/25 matches get win probs from initial elo

home_teams, away_teams = [], []

h, d, a = [], [], []

for team in current_teams:
    
    for opponent in current_teams:
        
        # get ratings
        
        team_rating = latest_ratings[team]
        opponent_rating = latest_ratings[opponent]
        
        # get win percentages from elo formula
        
        home_win = calculate_expected_win_percentage(team_rating, opponent_rating)
        away_win = calculate_expected_win_percentage(opponent_rating, team_rating)
        
        # draws occur 17% of the time in WSL
        # assign 17% draw probability for match, proportionally reducing home/away win %
        
        home_win = home_win - (home_win*0.17)
        away_win = away_win - (away_win*0.17)
        draw = 0.17
        
        # save probabilities to list
        
        home_teams.append(team)
        away_teams.append(opponent)
        
        h.append(home_win)
        d.append(draw)
        a.append(away_win)
        

expected_results = pd.DataFrame({"home":home_teams, 
                                 "away":away_teams,
                                 "home_win":h,
                                 "draw":d,
                                 "away_win":a})    

# filter out where teams play themselves!

expected_results = expected_results[expected_results["home"] !=\
                                    expected_results["away"]]
    
# function to get results for a given match

def get_result (home, draw, away, random, home_away):
    
    # given match probabilities and random no, assign points
    
    if random <= home:
        
        home_result, away_result = 3,0
    
    elif (random > home) and (random <= (home+draw)):
        
        home_result, away_result = 1,1
        
    else:
        
        home_result, away_result = 0,3
        
    if home_away == "home":
        result = home_result
    else:
        result = away_result
        
    return result

# do monte carlo sim of results

num_sims = 1000

sim_results = {}

for sim in range(num_sims):

    # create column of random no.s

    expected_results['random'] = [random.random() for i in range(len(expected_results))]
    
    # get match by match results
    
    expected_results['home_result'] = expected_results.\
        apply(lambda row: get_result(row['home_win'],
                                     row['draw'],
                                     row['away_win'],
                                     row['random'],
                                     "home"), axis=1)
    
    expected_results['away_result'] = expected_results.\
        apply(lambda row: get_result(row['home_win'],
                                     row['draw'],
                                     row['away_win'],
                                     row['random'],
                                     "away"), axis=1)
    
    def season_points(expected_results, team):
        
        team_results = expected_results[(expected_results["home"] == team)|
                         (expected_results["away"] == team)]
        
        team_results['team_points'] = np.where(team_results['home'] == team,
                                               team_results['home_result'],
                                               team_results['away_result'])
        
        total_pts = team_results['team_points'].sum()
        
        return total_pts

    points_by_team = dict(zip(current_teams, [season_points(expected_results, team) for team in current_teams]))
    
    sim_results[sim] = points_by_team

    
output = pd.DataFrame(sim_results)

# calc chelsea win percentage

winners = []

for i in range(num_sims):
    
    # sort by points, get winner

    winner = output[i].sort_values(ascending=False).index.tolist()[0]
    
    winners.append(winner)

chelsea_perc = winners.count("Chelsea")/num_sims

# plot

percentages = []

for winning_team in list(set(winners)):
    
    percentages.append(winners.count(winning_team)/num_sims)
    
winning_teams = pd.DataFrame({"team":list(set(winners)),
                              "percentage_wins":percentages})

# get sim stats

average_points, max_points, min_points = [], [], []

for team in current_teams:
    
    team_points_values = output.T[team]
    
    average_points.append(np.mean(team_points_values))
    min_points.append(np.percentile(team_points_values,75))
    max_points.append(np.percentile(team_points_values,25))
    
sim_summary = pd.DataFrame({"team":current_teams,
                            "average": average_points,
                            "min": min_points,
                            "max": max_points}).sort_values(by=['average'],
                                                            ascending=True)
# plot

fix, ax = plt.subplots(figsize=(10,8))

plt.rcParams["font.family"] = "Arial"

plt.hlines(y=range(1,len(sim_summary)+1),
           xmin=sim_summary['min'],
           xmax=sim_summary['max'], lw=5, color='grey', alpha=0.4, zorder=1)

plt.scatter(sim_summary['average'], range(1,len(sim_summary)+1),
            s=60,
            color='darkblue', alpha=0.9 , label='value2')


plt.title("Forecast Points Range - 2024/25 WSL", fontsize=20)
plt.yticks(range(1,len(sim_summary)+1), sim_summary['team'], fontsize=18)
plt.xlabel('Points', fontsize=18)
plt.xticks(fontsize=18)
plt.xlim(0,60)

# tidy plot

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

ax.tick_params(axis=u'both', which=u'both',length=0)

plt.tight_layout()
plt.savefig("images/points_range.png", dpi=200)

plt.show()



