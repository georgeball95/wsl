# create elo ratings 

import pandas as pd

df = pd.read_csv("data/match_results.csv")

df['score_difference'] = df['home_goals'] - df['away_goals']

def get_result(score_diff, home_away):
    
    if home_away == "home":
    
        if score_diff > 0:
            result = "W"
        elif score_diff < 0: 
            result = "L"
        else: 
            result = "D"   
            
    else:

        if score_diff > 0:
            result = "L"
        elif score_diff < 0: 
            result = "W"
        else: 
            result = "D"           
        
    return result

df['home_result'] = df.apply(lambda row: get_result(row['score_difference'], 'home'), axis=1)
df['away_result'] = df.apply(lambda row: get_result(row['score_difference'], 'away'), axis=1)

def calculate_expected_win_percentage(team_rating, opponent_rating):
    
    # gives expected win percentage from respective team ratings
    
    expected_win_percentage = 1 / (1 + 10 ** ((opponent_rating - team_rating) / 400))
    
    return expected_win_percentage

def get_new_rating(team_rating, opponent_rating, result, k=32):
    
    # given ratings of teams and result, get new rating
    
    expected_win_percentage = calculate_expected_win_percentage(team_rating, opponent_rating)
    new_rating = team_rating + k * (result - expected_win_percentage)
    
    return new_rating

# result reprsentation in elo equation

result_elo = {"W":1, "D":0.5, "L":0}

# create dict for initial ratings (1000)

ratings = dict(zip(df.home_team.unique().tolist(),
               [1000]*len(df.home_team.unique())))

home_pre_match_ratings, away_pre_match_ratings = [], []
home_post_match_ratings, away_post_match_ratings = [], []
    
# loop over df and calculate match by match team ratings

for index, row in df.iterrows():
    
    #match_up = row.iloc[0]
    
    home_team, away_team = row['home_team'], row['away_team']
    
    # get pre match ratings for home, away
    
    home_rating, away_rating = ratings[home_team], ratings[away_team]
    
    # calc expected win percentage
    
    home_win_perc = calculate_expected_win_percentage(home_rating, away_rating)
    away_win_perc = calculate_expected_win_percentage(away_rating, home_rating)
    
    # get result
    
    home_result, away_result = row['home_result'], row['away_result']
    
    # calc new ratings
    
    home_new_rating = get_new_rating(home_rating, away_rating,
                                     result_elo[home_result], k=32)
    
    away_new_rating = get_new_rating(away_rating, home_rating,
                                     result_elo[away_result], k=32)
    
    # update ratings dict
    
    ratings[home_team] = home_new_rating
    ratings[away_team] = away_new_rating
    
    # append to lists
    
    home_pre_match_ratings.append(home_rating)
    away_pre_match_ratings.append(away_rating)
    home_post_match_ratings.append(home_new_rating)
    away_post_match_ratings.append(away_new_rating)
    

# add to df
    
df['home_rating_pre'] = home_pre_match_ratings
df['away_rating_pre'] = away_pre_match_ratings
df['home_rating_post'] = home_post_match_ratings
df['away_rating_post'] = away_post_match_ratings
    
# save to csv

df.to_csv('data/results_elo_ratings.csv', index = False)






