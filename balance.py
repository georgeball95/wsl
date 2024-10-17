# script to look at competitive balance metrics

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("data/results_elo_ratings.csv")

df['score_diff'] = df['home_goals'] - df['away_goals']
df['score_diff_abs'] = df['score_diff'].abs()

df['xg_diff'] = df['home_xg'] - df['away_xg']
df['xg_diff_abs'] = df['xg_diff'].abs()

gd = []
xgd = []
draws = []
big_wins_list = []

season_ppg = {}

for season in df.season_end_year.unique():

    print(season)
    
    season_df = df[df["season_end_year"] == season]
    
    # average margin of victory
    
    print(np.mean(season_df.score_diff_abs))
    gd.append(np.mean(season_df.score_diff_abs))
    
    # prop of draws
    
    prop_draws = season_df.away_result.tolist().count("D")/len(season_df)
    draws.append(prop_draws)
    print(prop_draws)    
    
    # average xg diff
    
    print(np.mean(season_df.xg_diff_abs))
    xgd.append(np.mean(season_df.xg_diff_abs))
    
    # rate of 3+ goal wins
    
    big_wins = len([i for i in season_df.score_diff_abs.tolist() if i > 3])
    
    print(big_wins/len(season_df))
    big_wins_list.append(big_wins/len(season_df))
    
    # get ppg figures
        
    ppg_list = []
    
    for team in season_df.home_team.unique():
    
        team_df = season_df[(season_df["home_team"] == team)|(season_df["away_team"] == team)]
    
        team_df['team_points'] = np.where(team_df['home_team'] == team,
                                          team_df['home_result'],
                                          team_df['away_result'])
        
        points = team_df['team_points'].tolist().count("W")*3+\
                 team_df['team_points'].tolist().count("D")
        
        ppg = points/len(team_df)
        
        ppg_list.append(ppg)
    
    season_ppg[season] = ppg_list
    
# plot ppg dsitribution

fig,ax = plt.subplots(figsize=(8,6))

plt.rcParams["font.family"] = "Arial"
    
for season in season_ppg.keys():
    
    plt.scatter([str(season)]*12,season_ppg[season], s=80, alpha=0.3, color="darkblue")
    
    #plt.scatter([str(season)],np.mean(season_ppg[season]), marker="_", s=100, alpha=1, color="black")
    
    
plt.title("Points per game distribution", fontsize=20)
plt.xlabel('Season', fontsize=18)
plt.xlabel('Points per game', fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)
plt.ylim(0,3)

# tidy plot

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

ax.tick_params(axis=u'both', which=u'both',length=0)

plt.tight_layout()
plt.savefig("images/ppg_range.png", dpi=200)

plt.show()