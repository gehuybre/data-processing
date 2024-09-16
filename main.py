import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Load the data
matches_df = pd.read_parquet('data_source/prod/matches.parquet')
players_df = pd.read_parquet('data_source/prod/match_players.parquet')

# Filter for player 134300
player_matches = players_df[players_df['user_id'] == 134300]

print(f"Total matches for player 134300: {len(player_matches)}")

if len(player_matches) == 0:
    print("No data found for player 134300.")
else:
    # Merge with match data
    player_matches = player_matches.merge(matches_df, on='match_id')
    
    print("\nGame type distribution:")
    print(player_matches['game_type'].value_counts())
    
    print("\nRanked vs Unranked:")
    print(player_matches['is_ranked'].value_counts())
    
    # Filter for ranked team games
    ranked_team_matches = player_matches[(player_matches['is_ranked'] == True) & (player_matches['game_type'].str.contains('Team'))]
    
    print(f"\nRanked team games played: {len(ranked_team_matches)}")
    
    if len(ranked_team_matches) > 0:
        # Sort by start time
        ranked_team_matches = ranked_team_matches.sort_values('start_time')
        
        # Calculate daily stats
        daily_stats = ranked_team_matches.groupby(ranked_team_matches['start_time'].dt.date).agg({
            'match_id': 'count',
            'new_skill': 'last',
            'old_skill': 'first'
        }).reset_index()
        
        daily_stats['skill_change'] = daily_stats['new_skill'] - daily_stats['old_skill']
        daily_stats['cumulative_matches'] = daily_stats['match_id'].cumsum()
        
        # Create subplots
        fig = make_subplots(rows=4, cols=1, 
                            shared_xaxes=True, 
                            vertical_spacing=0.1,
                            subplot_titles=('Daily Matches Played', 'Skill Level', 'Daily Skill Change', 'Overall Statistics'))
        
        # Daily Matches Played
        fig.add_trace(go.Bar(x=daily_stats['start_time'], y=daily_stats['match_id'], name='Matches Played'),
                      row=1, col=1)
        
        # Skill Level
        fig.add_trace(go.Scatter(x=daily_stats['start_time'], y=daily_stats['new_skill'], mode='lines+markers', name='Skill Level'),
                      row=2, col=1)
        
        # Daily Skill Change
        fig.add_trace(go.Bar(x=daily_stats['start_time'], y=daily_stats['skill_change'], name='Skill Change'),
                      row=3, col=1)
        
        # Overall Statistics as text
        overall_stats = [
            f"Total matches: {len(player_matches)}",
            f"Date range: {player_matches['start_time'].min().date()} to {player_matches['start_time'].max().date()}",
            f"Initial skill: {player_matches['old_skill'].iloc[0]:.2f}",
            f"Final skill: {player_matches['new_skill'].iloc[-1]:.2f}",
            f"Overall skill change: {player_matches['new_skill'].iloc[-1] - player_matches['old_skill'].iloc[0]:.2f}",
            f"Overall win rate: {(player_matches['winning_team'] == player_matches['team_id']).mean():.2%}"
        ]
        
        # Add overall stats as annotations
        for i, stat in enumerate(overall_stats):
            fig.add_annotation(
                x=0.5, y=1 - (i + 1) * 0.15,
                xref="paper", yref="paper",
                text=stat,
                showarrow=False,
                font=dict(size=12),
                align="left",
                row=4, col=1
            )
        
        # Update layout
        fig.update_layout(height=1200, width=1200, title_text="Player 134300 - Comprehensive Analysis")
        fig.update_xaxes(title_text="Date", row=3, col=1)
        fig.update_yaxes(title_text="Matches", row=1, col=1)
        fig.update_yaxes(title_text="Skill", row=2, col=1)
        fig.update_yaxes(title_text="Skill Change", row=3, col=1)
        
        # Save the plot as an interactive HTML file
        fig.write_html("player_134300_analysis.html")
        
        # Print statistics
        print(f"Date range: {ranked_team_matches['start_time'].min().date()} to {ranked_team_matches['start_time'].max().date()}")
        print(f"Initial skill: {ranked_team_matches['old_skill'].iloc[0]:.2f}")
        print(f"Final skill: {ranked_team_matches['new_skill'].iloc[-1]:.2f}")
        print(f"Overall skill change: {ranked_team_matches['new_skill'].iloc[-1] - ranked_team_matches['old_skill'].iloc[0]:.2f}")
        print(f"Average daily matches: {daily_stats['match_id'].mean():.2f}")
        print(f"Max daily matches: {daily_stats['match_id'].max()}")
        print(f"Days played: {len(daily_stats)}")
        
        # Calculate and print win rate
        ranked_team_matches['is_winner'] = ranked_team_matches['winning_team'] == ranked_team_matches['team_id']
        win_rate = ranked_team_matches['is_winner'].mean()
        print(f"Win rate: {win_rate:.2%}")
        
        # Export daily stats to CSV for further analysis if needed
        daily_stats.to_csv("player_134300_daily_stats.csv", index=False)
        
        print("\nAnalysis complete. Check player_134300_analysis.html for interactive visualizations.")
    else:
        print("No ranked team games found for player 134300.")
    
    # Print overall stats regardless of game type
    print("\nOverall stats (all game types):")
    print(f"Total matches: {len(player_matches)}")
    print(f"Date range: {player_matches['start_time'].min().date()} to {player_matches['start_time'].max().date()}")
    print(f"Initial skill: {player_matches['old_skill'].iloc[0]:.2f}")
    print(f"Final skill: {player_matches['new_skill'].iloc[-1]:.2f}")
    print(f"Overall skill change: {player_matches['new_skill'].iloc[-1] - player_matches['old_skill'].iloc[0]:.2f}")
    
    player_matches['is_winner'] = player_matches['winning_team'] == player_matches['team_id']
    overall_win_rate = player_matches['is_winner'].mean()
    print(f"Overall win rate: {overall_win_rate:.2%}")