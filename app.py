import pandas as pd
import streamlit as st

# Load data
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)
    # Define Phases
    def get_phase(ball):
        if ball <= 6.0: return 'Powerplay'
        elif ball <= 15.0: return 'Middle Overs'
        else: return 'Death Overs'
    
    df['phase'] = df['ball'].apply(get_phase)
    df['total_runs'] = df['runs_off_bat'] + df['extras']
    df['is_dot'] = (df['total_runs'] == 0).astype(int)
    df['is_boundary'] = df['runs_off_bat'].isin([4, 6]).astype(int)
    # Count wickets (excluding non-bowler dismissals like run outs for bowling stats)
    bowler_wickets = ['bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket']
    df['is_bowler_wicket'] = df['wicket_type'].isin(bowler_wickets).astype(int)
    df['is_dismissal'] = df['player_dismissed'].notna().astype(int)
    
    return df

# Main App
st.set_page_config(layout="wide", page_title="Cricket Analytics Dashboard")
st.title("🏏 Cricket Match Analysis Dashboard")

# Upload File
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = load_data(uploaded_file)
    
    # --- SLICERS ---
    st.sidebar.header("Filters")
    selected_season = st.sidebar.multiselect("Select Season", options=df['season'].unique(), default=df['season'].unique())
    selected_phase = st.sidebar.multiselect("Select Phase", options=['Powerplay', 'Middle Overs', 'Death Overs'], default=['Powerplay', 'Middle Overs', 'Death Overs'])
    
    # Filter Data
    mask = df['season'].isin(selected_season) & df['phase'].isin(selected_phase)
    f_df = df[mask]

    tab1, tab2, tab3, tab4 = st.tabs(["Batting", "Bowling", "Team", "Venue"])

    # --- BATTING STATS ---
    with tab1:
        bat_stats = f_df.groupby('striker').agg(
            Innings=('match_id', 'nunique'),
            Runs=('runs_off_bat', 'sum'),
            Balls=('ball', 'count'),
            Dismissals=('is_dismissal', 'sum'),
            Dots=('is_dot', 'sum'),
            Boundaries=('is_boundary', 'sum')
        ).reset_index()
        
        bat_stats['SR'] = round((bat_stats['Runs'] / bat_stats['Balls']) * 100, 2)
        bat_stats['Avg'] = round(bat_stats['Runs'] / bat_stats['Dismissals'].replace(0, 1), 2)
        bat_stats['Dot%'] = round((bat_stats['Dots'] / bat_stats['Balls']) * 100, 2)
        bat_stats['Balls_Per_Bndry'] = round(bat_stats['Balls'] / bat_stats['Boundaries'].replace(0, 1), 2)
        
        st.dataframe(bat_stats.sort_values(by='Runs', ascending=False), use_container_width=True)

    # --- BOWLING STATS ---
    with tab2:
        bowl_stats = f_df.groupby('bowler').agg(
            Innings=('match_id', 'nunique'),
            Wickets=('is_bowler_wicket', 'sum'),
            Runs_Conceded=('runs_off_bat', 'sum'), # or total_runs depending on preference
            Extras=('extras', 'sum'),
            Balls_Bowled=('ball', 'count'),
            Dots=('is_dot', 'sum'),
            Bndry_Conceded=('is_boundary', 'sum')
        ).reset_index()
        
        bowl_stats['Total_Runs'] = bowl_stats['Runs_Conceded'] + bowl_stats['Extras']
        bowl_stats['Eco'] = round((bowl_stats['Total_Runs'] / bowl_stats['Balls_Bowled']) * 6, 2)
        bowl_stats['Avg'] = round(bowl_stats['Total_Runs'] / bowl_stats['Wickets'].replace(0, 1), 2)
        bowl_stats['SR'] = round(bowl_stats['Balls_Bowled'] / bowl_stats['Wickets'].replace(0, 1), 2)
        bowl_stats['Dot%'] = round((bowl_stats['Dots'] / bowl_stats['Balls_Bowled']) * 100, 2)
        bowl_stats['Balls_Per_Bndry'] = round(bowl_stats['Balls_Bowled'] / bowl_stats['Bndry_Conceded'].replace(0, 1), 2)
        
        st.dataframe(bowl_stats.sort_values(by='Wickets', ascending=False), use_container_width=True)

    # --- TEAM STATS ---
    with tab3:
        team_bat = f_df.groupby('batting_team').agg(Runs_Scored=('total_runs', 'sum'))
        team_bowl = f_df.groupby('bowling_team').agg(
            Runs_Conceded=('total_runs', 'sum'),
            Wickets_Taken=('is_dismissal', 'sum'),
            Balls_Bowled=('ball', 'count'),
            Dots=('is_dot', 'sum'),
            Bndry=('is_boundary', 'sum')
        )
        
        team_stats = team_bat.join(team_bowl).reset_index().rename(columns={'index': 'Team'})
        team_stats['Runs_Per_Wicket'] = round(team_stats['Runs_Conceded'] / team_stats['Wickets_Taken'].replace(0, 1), 2)
        team_stats['Dot%'] = round((team_stats['Dots'] / team_stats['Balls_Bowled']) * 100, 2)
        team_stats['Balls_Per_Bndry'] = round(team_stats['Balls_Bowled'] / team_stats['Bndry'].replace(0, 1), 2)
        
        st.dataframe(team_stats, use_container_width=True)

    # --- VENUE STATS ---
    with tab4:
        venue_stats = f_df.groupby('venue').agg(
            Runs_Scored=('total_runs', 'sum'),
            Wickets_Lost=('is_dismissal', 'sum'),
            Balls_Played=('ball', 'count'),
            Dots=('is_dot', 'sum'),
            Bndries=('is_boundary', 'sum')
        ).reset_index()
        
        venue_stats['Runs_Per_Wicket'] = round(venue_stats['Runs_Scored'] / venue_stats['Wickets_Lost'].replace(0, 1), 2)
        venue_stats['Dot%'] = round((venue_stats['Dots'] / venue_stats['Balls_Played']) * 100, 2)
        venue_stats['Balls_Per_Bndry'] = round(venue_stats['Balls_Played'] / venue_stats['Bndries'].replace(0, 1), 2)
        
        st.dataframe(venue_stats, use_container_width=True)
else:
    st.info("Please upload the CSV file to begin.")
