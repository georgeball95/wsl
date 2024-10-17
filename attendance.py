import pandas as pd
import numpy as np
# script to look at attendance vs team quality

import matplotlib.pyplot as plt

df = pd.read_csv("data/results_elo_ratings.csv")

df['combined_rating'] = df['home_rating_pre'] + df['away_rating_pre']

# remove covid

df = df[~df["attendance"].isna()]

# elo ratings start in 2019 as level, so only look at post covid so 
# the ratings have stabilised

df = df[df["season_end_year"] > 2021]

# df = df[df["attendance"] <= 10000]

fig,ax = plt.subplots(figsize=(8,6))

plt.rcParams["font.family"] = "Arial"

plt.scatter(df['combined_rating'], df['attendance'], s=20, alpha=0.5)

corr = np.corrcoef(df['combined_rating'], df['attendance'])

plt.title("Away Team Rating vs Attendance, 21/22 - 23/24", fontsize=20)
plt.xlabel('Attendance', fontsize=18)
plt.xlabel('Combined team rating', fontsize=18)
plt.xticks(fontsize=18)
plt.yticks(fontsize=18)

# tidy plot

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

ax.tick_params(axis=u'both', which=u'both',length=0)

plt.tight_layout()
plt.savefig("images/attendance-combined-rating_stadium_filter.png", dpi=200)

# Show the graph
plt.show()