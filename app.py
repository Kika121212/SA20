import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

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
    df['is_two'] = df['runs_off_bat'].isin([2]).astype(int)
    # Count wickets (excluding non-bowler dismissals like run outs for bowling stats)
    bowler_wickets = ['bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket']
    df['is_bowler_wicket'] = df['wicket_type'].isin(bowler_wickets).astype(int)
    df['is_dismissal'] = df['player_dismissed'].notna().astype(int)
    
    return df

# Graph Functions
def create_run_worm_graph(data):
    """Create Run Worm graph - Cumulative runs over balls"""
    data_sorted = data.sort_values('ball')
    data_sorted['cumulative_runs'] = data_sorted['total_runs'].cumsum()
    
    fig = go.Figure()
    
    for team in data_sorted['batting_team'].unique():
        team_data = data_sorted[data_sorted['batting_team'] == team]
        fig.add_trace(go.Scatter(
            x=team_data['ball'],
            y=team_data['cumulative_runs'],
            mode='lines',
            name=team,
            line=dict(width=3)
        ))
    
    fig.update_layout(
        title='<b>Run Worm Graph - Cumulative Runs Progression</b>',
        xaxis_title='Ball Number',
        yaxis_title='Cumulative Runs',
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='rgba(17, 17, 17, 0.8)',
        paper_bgcolor='rgba(17, 17, 17, 0.9)',
        font=dict(size=12, color='white'),
        height=600
    )
    return fig

def create_manhattan_graph(data):
    """Create Manhattan graph - Run distribution"""
    run_dist = data['runs_off_bat'].value_counts().sort_index()
    
    fig = go.Figure(data=[go.Bar(
        x=run_dist.index,
        y=run_dist.values,
        marker=dict(
            color=run_dist.values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Frequency")
        ),
        text=run_dist.values,
        textposition='auto'
    )])
    
    fig.update_layout(
        title='<b>Manhattan Graph - Run Distribution</b>',
        xaxis_title='Runs Per Ball',
        yaxis_title='Frequency',
        template='plotly_dark',
        plot_bgcolor='rgba(17, 17, 17, 0.8)',
        paper_bgcolor='rgba(17, 17, 17, 0.9)',
        font=dict(size=12, color='white'),
        height=600
    )
    return fig

def create_run_rate_graph(data):
    """Create Run Rate graph - Runs per over"""
    data_sorted = data.sort_values('ball')
    data_sorted['over'] = (data_sorted['ball'] / 6).astype(int)
    
    run_rate_data = data_sorted.groupby(['over', 'batting_team'])['total_runs'].sum().reset_index()
    
    fig = go.Figure()
    
    for team in run_rate_data['batting_team'].unique():
        team_data = run_rate_data[run_rate_data['batting_team'] == team]
        fig.add_trace(go.Scatter(
            x=team_data['over'],
            y=team_data['total_runs'],
            mode='lines+markers',
            name=team,
            line=dict(width=3),
            fill='tozeroy'
        ))
    
    fig.update_layout(
        title='<b>Run Rate Graph - Runs Per Over</b>',
        xaxis_title='Over Number',
        yaxis_title='Runs Scored',
        hovermode='x unified',
        template='plotly_dark',
        plot_bgcolor='rgba(17, 17, 17, 0.8)',
        paper_bgcolor='rgba(17, 17, 17, 0.9)',
        font=dict(size=12, color='white'),
        height=600
    )
    return fig

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
    selected_venue = st.sidebar.multiselect("Select venue", options=df['venue'].unique(), default=df['venue'].unique())
    selected_phase = st.sidebar.multiselect("Select Phase", options=['Powerplay', 'Middle Overs', 'Death Overs'], default=['Powerplay', 'Middle Overs', 'Death Overs'])
    
    # Filter Data
    mask = df['season'].isin(selected_season) & df['venue'].isin(selected_venue) & df['phase'].isin(selected_phase) 
    f_df = df[mask]

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Batting", "Bowling", "Team", "Venue", "📊 Graphs"]) 

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
            Runs_Conceded=('runs_off_bat', 'sum'),
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
            Bndries=('is_boundary', 'sum'),
            twos=('is_two', 'sum')
        ).reset_index() 
        
        venue_stats['Runs_Per_Wicket'] = round(venue_stats['Runs_Scored'] / venue_stats['Wickets_Lost'].replace(0, 1), 2)
        venue_stats['Dot%'] = round((venue_stats['Dots'] / venue_stats['Balls_Played']) * 100, 2)
        venue_stats['Balls_Per_Bndry'] = round(venue_stats['Balls_Played'] / venue_stats['Bndries'].replace(0, 1), 2)
        
        st.dataframe(venue_stats, use_container_width=True)

    # --- GRAPH STATS ---
    with tab5:
        st.header("🎨 Advanced Graph Analysis")
        st.write("---")
        
        # Graph selection
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🐛 Run Worm Graph", use_container_width=True, key="btn_run_worm"):
                st.session_state.graph_type = "run_worm"
        
        with col2:
            if st.button("🏙️ Manhattan Graph", use_container_width=True, key="btn_manhattan"):
                st.session_state.graph_type = "manhattan"
        
        with col3:
            if st.button("📈 Run Rate Graph", use_container_width=True, key="btn_run_rate"):
                st.session_state.graph_type = "run_rate"
        
        st.write("---")
        
        # Display selected graph
        if 'graph_type' in st.session_state:
            graph_type = st.session_state.graph_type
            
            if graph_type == "run_worm":
                st.subheader("🐛 Run Worm Graph")
                fig = create_run_worm_graph(f_df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Download button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download as PNG"):
                        img_bytes = fig.to_image(format="png")
                        st.download_button(
                            label="Download PNG",
                            data=img_bytes,
                            file_name="run_worm_graph.png",
                            mime="image/png"
                        )
                with col2:
                    if st.button("📥 Download as SVG"):
                        svg_bytes = fig.to_image(format="svg")
                        st.download_button(
                            label="Download SVG",
                            data=svg_bytes,
                            file_name="run_worm_graph.svg",
                            mime="image/svg+xml"
                        )
            
            elif graph_type == "manhattan":
                st.subheader("🏙️ Manhattan Graph")
                fig = create_manhattan_graph(f_df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Download button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download as PNG", key="download_manhattan_png"):
                        img_bytes = fig.to_image(format="png")
                        st.download_button(
                            label="Download PNG",
                            data=img_bytes,
                            file_name="manhattan_graph.png",
                            mime="image/png",
                            key="manhattan_png"
                        )
                with col2:
                    if st.button("📥 Download as SVG", key="download_manhattan_svg"):
                        svg_bytes = fig.to_image(format="svg")
                        st.download_button(
                            label="Download SVG",
                            data=svg_bytes,
                            file_name="manhattan_graph.svg",
                            mime="image/svg+xml",
                            key="manhattan_svg"
                        )
            
            elif graph_type == "run_rate":
                st.subheader("📈 Run Rate Graph")
                fig = create_run_rate_graph(f_df)
                st.plotly_chart(fig, use_container_width=True)
                
                # Download button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download as PNG", key="download_runrate_png"):
                        img_bytes = fig.to_image(format="png")
                        st.download_button(
                            label="Download PNG",
                            data=img_bytes,
                            file_name="run_rate_graph.png",
                            mime="image/png",
                            key="runrate_png"
                        )
                with col2:
                    if st.button("📥 Download as SVG", key="download_runrate_svg"):
                        svg_bytes = fig.to_image(format="svg")
                        st.download_button(
                            label="Download SVG",
                            data=svg_bytes,
                            file_name="run_rate_graph.svg",
                            mime="image/svg+xml",
                            key="runrate_svg"
                        )
        else:
            st.info("👈 Select a graph type from the options above to visualize the data!")

else:
    st.info("Please upload the CSV file to begin.")
