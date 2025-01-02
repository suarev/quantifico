from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import json
import traceback
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Arc
from ScraperFC import Sofascore
from tqdm import tqdm
from dotenv import load_dotenv
load_dotenv()
import os

app = Flask(__name__)
CORS(app)

# Database connection details
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", 5432))
}

def get_db_connection():
    """Establish and return a database connection."""
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

@app.route('/api/player/<player_name>', methods=['GET'])
def get_player_info(player_name):
    """
    Fetch player information from the database for the PlayerProfile component.
    """
    try:
        # Connect to the database
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Failed to connect to the database"}), 500

        # Query to fetch player details
        query = """
        SELECT 
            p.player AS name,
            p.nation_ AS nationality,
            p.team,
            p.pos_ AS position,
            p.age_ AS age,
            p.value AS value,
            pt.matches_played AS matches_played
        FROM players_info p
        LEFT JOIN playing_time_stats pt ON p.player_id = pt.player_id
        WHERE p.player ILIKE %s
        """

        # Execute the query
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (player_name,))
            result = cursor.fetchone()  # Fetch a single result

        # Close the connection
        connection.close()

        if not result:
            return jsonify({"error": "Player not found"}), 404

        # Return the player's data as JSON
        return jsonify(result)

    except Exception as e:
        print(f"Error fetching player info: {e}")
        return jsonify({"error": str(e)}), 500


def normalize_value(value, min_val, max_val):
    """
    Normalize a value to a percentile (0-100) based on min and max values.
    If max_val == min_val, return 50 to handle cases with no variation.
    """
    try:
        value = float(value)
        min_val = float(min_val)
        max_val = float(max_val)
    except (ValueError, TypeError):
        return 0  # Return 0 if conversion fails

    if max_val == min_val:
        return 50  # Default to the middle percentile
    return ((value - min_val) / (max_val - min_val)) * 100

def convert_value_to_millions(value_str):
    """
    Convert value string (e.g., '€900k', '€70.00m') to float in millions.
    """
    try:
        value_str = str(value_str).replace('€', '').strip()

        if 'm' in value_str.lower():
            return float(value_str.lower().replace('m', ''))
        elif 'k' in value_str.lower():
            return float(value_str.lower().replace('k', '')) / 1000
        else:
            return float(value_str) / 1000000
    except Exception as e:
        print(f"Error converting value: {value_str}, {str(e)}")
        return 0.0


@app.route('/api/radar/<player_name>', methods=['GET'])
def get_radar_data(player_name):
    """
    Fetch radar chart data for a player based on metrics from the unified dataset.
    """
    try:
        # Connect to the database
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Failed to connect to the database"}), 500

        # Parse metrics parameter
        metrics_param = request.args.get('metrics')
        if metrics_param:
            metrics = json.loads(metrics_param)  # Expected: { "display_name": "column_name" }
        else:
            # Default metrics (from all available columns)
            metrics = {
                'Shot Creating Actions': 'sca',
                'Key Passes': 'key_passes',
                'Prog. Carries': 'progressive_carries',
                'Prog. Passes': 'progressive_passes',
                'xAG': 'xag',
                'npxG': 'npxg',
                'Tackles+Interceptions': 'tackles_interceptions',
                'Take-ons Succ.': 'dribbles_completed_pct',
                'Recoveries': 'passes_received'
            }

        # Build query for the unified dataset
        query = """
        SELECT
            players_info.player AS name,
            creation_stats.*,
            defensive_stats.*,
            passing_stats.*,
            performance_stats.*,
            playing_time_stats.*,
            possession_stats.*,
            shooting_stats.*
        FROM players_info
        LEFT JOIN creation_stats ON players_info.player_id = creation_stats.player_id
        LEFT JOIN defensive_stats ON players_info.player_id = defensive_stats.player_id
        LEFT JOIN passing_stats ON players_info.player_id = passing_stats.player_id
        LEFT JOIN performance_stats ON players_info.player_id = performance_stats.player_id
        LEFT JOIN playing_time_stats ON players_info.player_id = playing_time_stats.player_id
        LEFT JOIN possession_stats ON players_info.player_id = possession_stats.player_id
        LEFT JOIN shooting_stats ON players_info.player_id = shooting_stats.player_id
        WHERE players_info.player ILIKE %s
        """

        league_query = """
        SELECT
            creation_stats.*,
            defensive_stats.*,
            passing_stats.*,
            performance_stats.*,
            playing_time_stats.*,
            possession_stats.*,
            shooting_stats.*
        FROM players_info
        LEFT JOIN creation_stats ON players_info.player_id = creation_stats.player_id
        LEFT JOIN defensive_stats ON players_info.player_id = defensive_stats.player_id
        LEFT JOIN passing_stats ON players_info.player_id = passing_stats.player_id
        LEFT JOIN performance_stats ON players_info.player_id = performance_stats.player_id
        LEFT JOIN playing_time_stats ON players_info.player_id = playing_time_stats.player_id
        LEFT JOIN possession_stats ON players_info.player_id = possession_stats.player_id
        LEFT JOIN shooting_stats ON players_info.player_id = shooting_stats.player_id
        """

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Fetch player data
            cursor.execute(query, (player_name,))
            player_data = cursor.fetchone()
            if not player_data:
                return jsonify({"error": "Player not found"}), 404

            # Fetch league data
            cursor.execute(league_query)
            league_data = cursor.fetchall()

        # Close the connection
        connection.close()

        # Prepare response data
        player_values = {}
        league_averages = {}
        raw_values = {}

        for display_name, column in metrics.items():
            # Extract player value
            player_value = player_data.get(column)

            # Extract league values for the metric
            league_values = [row[column] for row in league_data if row[column] is not None]

            # Skip if no league values are found
            if not league_values:
                continue

            # Calculate min, max, and average for the league
            min_val = min(league_values)
            max_val = max(league_values)
            avg_val = sum(league_values) / len(league_values)

            # Normalize player and league values to percentiles
            player_percentile = normalize_value(player_value, min_val, max_val)
            league_avg_percentile = normalize_value(avg_val, min_val, max_val)

            # Populate response data
            raw_values[display_name] = {
                'player': player_value,
                'league_avg': avg_val,
                'max': max_val
            }
            player_values[display_name] = player_percentile
            league_averages[display_name] = league_avg_percentile

        # Return JSON response
        return jsonify({
            'player': player_values,
            'league_average': league_averages,
            'raw_values': raw_values,
            'metrics': list(metrics.keys())
        })

    except Exception as e:
        print(f"Error processing radar data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/available-metrics', methods=['GET'])
def get_available_metrics():
    """
    Fetch all column names from the relevant tables (excluding players_info) for dropdown menus.
    """
    try:
        # List of column names extracted from the CSV
        columns = [
            'stat_id', 'player_id', 'season', 'value','league','team','nation_','pos_','age_','born_', 'sca', 'sca_per90', 'sca_passes_live',
            'sca_passes_dead', 'sca_take_ons', 'sca_shots', 'sca_fouls', 'sca_defense',
            'gca', 'gca_per90', 'gca_passes_live', 'gca_passes_dead', 'gca_take_ons',
            'gca_shots', 'gca_fouls', 'gca_defense', 'tackles', 'tackles_won',
            'tackles_def_3rd', 'tackles_mid_3rd', 'tackles_att_3rd', 'challenge_tackles',
            'challenges', 'challenge_tackles_pct', 'challenges_lost', 'blocks',
            'blocked_shots', 'blocked_passes', 'interceptions', 'tackles_interceptions',
            'clearances', 'errors', 'passes_total', 'passes_live', 'passes_dead',
            'passes_free_kicks', 'through_balls', 'switches', 'crosses', 'throw_ins',
            'corner_kicks', 'corner_kicks_in', 'corner_kicks_out', 'corner_kicks_straight',
            'passes_completed', 'passes_offsides', 'passes_blocked', 'passes_attempted',
            'passes_completed_pct', 'total_distance', 'progressive_distance',
            'short_completed', 'short_attempted', 'short_completed_pct', 'medium_completed',
            'medium_attempted', 'medium_completed_pct', 'long_completed', 'long_attempted',
            'long_completed_pct', 'assists', 'xag', 'xa', 'key_passes',
            'passes_into_final_third', 'passes_into_penalty_area', 'crosses_into_penalty_area',
            'progressive_passes', 'goals', 'goals_assists', 'goals_pens', 'pens_made',
            'pens_att', 'cards_yellow', 'cards_red', 'xg', 'npxg', 'npxg_xag',
            'matches_played', 'matches_started', 'minutes_played', 'minutes_90s', 'touches',
            'touches_def_pen', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd',
            'touches_att_pen', 'touches_live', 'dribbles_attempted', 'dribbles_completed',
            'dribbles_completed_pct', 'carries', 'carry_distance',
            'carry_progressive_distance', 'progressive_carries', 'carries_into_final_third',
            'carries_into_penalty_area', 'miscontrols', 'dispossessed', 'passes_received',
            'progressive_passes_received', 'shots', 'shots_on_target', 'shots_on_target_pct',
            'shots_per90', 'shots_on_target_per90', 'goals_per_shot',
            'goals_per_shot_on_target', 'average_shot_distance', 'shots_free_kicks',
            'shots_penalties', 'shots_penalties_att'
        ]

        # Prepare response data
        metrics = [{'value': col, 'label': col} for col in columns]
        return jsonify({'metrics': metrics})

    except Exception as e:
        print(f"Error getting metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/scatter/<player_name>', methods=['GET'])
def get_scatter_data(player_name):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Failed to connect to the database"}), 500

        # Get all midfielders with their stats
        query = """
        SELECT 
            pi.player,
            pi.team,
            cs.sca,                -- SCA
            pass.key_passes,             -- Key passes
            poss.progressive_carries,     -- Progressive carries
            pass.progressive_passes,      -- Progressive passes
            ps.xag,                      -- xAG/90
            ps.npxg,                     -- npxG/90
            poss.dribbles_completed_pct,  -- Take ons success rate
            ds.challenge_tackles_pct,              -- Defensive challenges tackled
            ds.blocks,                   -- Defensive blocks
            ds.interceptions,            -- Defensive interceptions
            ds.tackles                   -- tackles
        FROM players_info pi
        LEFT JOIN creation_stats cs ON pi.player_id = cs.player_id
        LEFT JOIN passing_stats pass ON pi.player_id = pass.player_id
        LEFT JOIN possession_stats poss ON pi.player_id = poss.player_id
        LEFT JOIN performance_stats ps ON pi.player_id = ps.player_id
        LEFT JOIN defensive_stats ds ON pi.player_id = ds.player_id
        WHERE pi.pos_ LIKE '%MF%'
        """

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query)
            midfielders_data = cursor.fetchall()

        connection.close()

        if not midfielders_data:
            return jsonify({"error": "No midfielder data found"}), 404

        # Convert to DataFrame for PCA calculation
        df = pd.DataFrame(midfielders_data)

        # Define attacking and defensive metrics based on available columns
        attacking_metrics = [
            'sca',              # SCA
            'key_passes',             # Key passes
            'progressive_carries',     # Progressive carries
            'progressive_passes',      # Progressive passes
            'xag',                    # xAG/90
            'npxg',                   # npxG/90
            'dribbles_completed_pct'  # Take ons success rate
        ]
        
        defensive_metrics = [
            'challenge_tackles_pct',           # Tackles percentage
            'blocks',                # Defensive blocks
            'interceptions',         # Defensive interceptions
            'tackles'  
        ]

        # Function to calculate PCA
        def calculate_pca(metrics):
            X = df[metrics].fillna(0)
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            pca = PCA(n_components=1)
            principal_components = pca.fit_transform(X_scaled)
            
            return principal_components.flatten(), pca.explained_variance_ratio_[0]

        # Calculate PCA components
        attacking_pca, att_variance = calculate_pca(attacking_metrics)
        defensive_pca, def_variance = calculate_pca(defensive_metrics)

        # Prepare response data
        result = {
            'players': df['player'].tolist(),
            'data': [],
            'selected_player': player_name,
            'variance_explained': {
                'attacking': round(att_variance * 100, 2),
                'defensive': round(def_variance * 100, 2)
            }
        }

        # Create the data points
        for i, player in enumerate(df['player']):
            result['data'].append({
                'player': player,
                'attacking': float(attacking_pca[i]),
                'defensive': float(defensive_pca[i]),
                'team': df.iloc[i]['team']
            })

        return jsonify(result)

    except Exception as e:
        print(f"Error processing scatter plot data: {e}")
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

def get_primary_position(pos_str):
    """Extract primary position from position string"""
    if pos_str is None or not pos_str:
        return 'NA'

    first_pos = str(pos_str).split(',')[0].split('/')[0].strip().upper()
    
    if 'GK' in first_pos:
        return 'GK'
    elif 'DF' in first_pos:
        return 'DF'
    elif 'MF' in first_pos:
        return 'MF'
    elif 'FW' in first_pos:
        return 'FW'
    return 'NA'

@app.route('/api/parallel/<player_name>', methods=['GET'])
def get_parallel_data(player_name):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Failed to connect to the database"}), 500

        # Parse metrics parameter
        metrics_param = request.args.get('metrics')
        if metrics_param:
            metrics = json.loads(metrics_param)
        else:
            # Default metrics mapping with explicit metric name -> column mapping
            metrics = {
                'Position': 'pi.pos_',
                'Minutes': 'pts.minutes_played',
                'Age': 'pi.age_',
                'Value': 'pi.value',
                'Goals': 'ps.goals',
                'Assists': 'ps.assists',
                'SCA': 'cs.sca',
                'Key Passes': 'pass.key_passes',
                'Tackles + Int': 'ds.tackles_interceptions',
                'Prog Carries': 'poss.progressive_carries',
                'Prog Passes': 'pass.progressive_passes'
            }

        # First get the player's team
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT team 
                FROM players_info 
                WHERE player ILIKE %s
            """, (player_name,))
            
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": "Player not found"}), 404
            
            player_team = result[0]

        # Build SELECT clause with properly quoted column aliases
        metric_columns = []
        for display_name, column_path in metrics.items():
            # Properly quote both the alias and the column reference
            metric_columns.append(f'{column_path} as "{display_name}"')
        
        select_clause = ', '.join(['pi.player'] + metric_columns)

        # Construct the main query
        query = f"""
            SELECT {select_clause}
            FROM players_info pi
            LEFT JOIN playing_time_stats pts ON pi.player_id = pts.player_id
            LEFT JOIN performance_stats ps ON pi.player_id = ps.player_id
            LEFT JOIN creation_stats cs ON pi.player_id = cs.player_id
            LEFT JOIN passing_stats pass ON pi.player_id = pass.player_id
            LEFT JOIN defensive_stats ds ON pi.player_id = ds.player_id
            LEFT JOIN possession_stats poss ON pi.player_id = poss.player_id
            WHERE pi.team = %s
        """

        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (player_team,))
            team_data = cursor.fetchall()

        connection.close()

        if not team_data:
            return jsonify({"error": "No data found"}), 404

        response_data = {
            'players': [row['player'] for row in team_data],
            'metrics': list(metrics.keys()),
            'data': [],
            'domains': {
                'Position': ['GK', 'DF', 'MF', 'FW']
            }
        }

        # Transform the data
        for row in team_data:
            player_data = {
                'player': row['player'],
                'values': {}
            }

            for metric_name in metrics.keys():
                try:
                    value = row[metric_name]
                    
                    # Special handling for Position
                    if metric_name == 'Position':
                        value = get_primary_position(value)
                    # Special handling for Value
                    elif metric_name == 'Value':
                        value = convert_value_to_millions(value)
                    
                    player_data['values'][metric_name] = value

                except KeyError as e:
                    player_data['values'][metric_name] = None

            response_data['data'].append(player_data)

        return jsonify(response_data)

    except Exception as e:
        print(f"Error processing parallel data: {e}")
        return jsonify({"error": str(e)}), 500
    
HEATMAP_PARAMS = {
    'bw_adjust': 0.7,     # ADJUST THIS: Lower (0.5-0.8) for more distinct spots, Higher for more blur
    'levels': 90,        # ADJUST THIS: Lower (20-50) for more distinct levels, Higher for smoother gradient
    'thresh': 0.08,       # ADJUST THIS: Higher (0.1-0.2) for less spread, Lower for more spread
}

# Coordinate scaling and positioning
SCALING = {
    'x_scale': 1.29,      # ADJUST THIS: Changes horizontal stretch/compression
    'y_scale': 0.9,       # ADJUST THIS: Changes vertical stretch/compression
    'x_offset': 0,        # ADJUST THIS: Shifts entire heatmap left (-) or right (+)
    'y_offset': 0         # ADJUST THIS: Shifts entire heatmap up (+) or down (-)
}

def create_soccer_field(ax):
    # White background
    ax.set_facecolor('white')
    
    # Black lines for the pitch
    line_color = 'black'
    line_width = 1
    
    # Pitch outline and center line
    plt.plot([0, 0], [0, 90], color=line_color, linewidth=line_width)
    plt.plot([0, 130], [90, 90], color=line_color, linewidth=line_width)
    plt.plot([130, 130], [90, 0], color=line_color, linewidth=line_width)
    plt.plot([130, 0], [0, 0], color=line_color, linewidth=line_width)
    plt.plot([65, 65], [0, 90], color=line_color, linewidth=line_width)

    # Left penalty area
    plt.plot([16.5, 16.5], [65, 25], color=line_color, linewidth=line_width)
    plt.plot([0, 16.5], [65, 65], color=line_color, linewidth=line_width)
    plt.plot([16.5, 0], [25, 25], color=line_color, linewidth=line_width)

    # Right penalty area
    plt.plot([130, 113.5], [65, 65], color=line_color, linewidth=line_width)
    plt.plot([113.5, 113.5], [65, 25], color=line_color, linewidth=line_width)
    plt.plot([113.5, 130], [25, 25], color=line_color, linewidth=line_width)

    # Left 6-yard box
    plt.plot([0, 5.5], [54, 54], color=line_color, linewidth=line_width)
    plt.plot([5.5, 5.5], [54, 36], color=line_color, linewidth=line_width)
    plt.plot([5.5, 0], [36, 36], color=line_color, linewidth=line_width)

    # Right 6-yard box
    plt.plot([130, 124.5], [54, 54], color=line_color, linewidth=line_width)
    plt.plot([124.5, 124.5], [54, 36], color=line_color, linewidth=line_width)
    plt.plot([124.5, 130], [36, 36], color=line_color, linewidth=line_width)

    # Center circle
    center_circle = plt.Circle((65, 45), 9.15, color=line_color, fill=False, linewidth=line_width)
    ax.add_patch(center_circle)
    
    # Penalty spots and center spot
    plt.scatter([11, 65, 119], [45, 45, 45], color=line_color, s=20)

    # Penalty arcs
    left_arc = Arc((11, 45), height=18.3, width=18.3, angle=0, theta1=310, theta2=50, 
                   color=line_color, linewidth=line_width)
    right_arc = Arc((119, 45), height=18.3, width=18.3, angle=0, theta1=130, theta2=230, 
                    color=line_color, linewidth=line_width)
    ax.add_patch(left_arc)
    ax.add_patch(right_arc)

def get_season_heatmap_data(year="2023/2024", league="EPL", player_name="Bruno Fernandes", team_name="Manchester United"):
    """Collect heatmap data from all matches in a season for a specific player"""
    ss = Sofascore()
    
    # Get all matches from the season
    print(f"Fetching {league} matches for {year} season...")
    matches = ss.get_match_dicts(year, league)
    
    # Filter for team's matches
    team_matches = [
        match for match in matches 
        if team_name in match['homeTeam']['name'] or team_name in match['awayTeam']['name']
    ]
    
    print(f"Found {len(team_matches)} matches for {team_name}")
    
    # Collect coordinates from all matches
    all_coordinates = []
    skipped_matches = 0
    
    for match in tqdm(team_matches, desc="Processing matches"):
        try:
            match_id = match['id']
            heatmap_data = ss.scrape_heatmaps(match_id)
            
            # Find player data
            player_data = None
            for player_id, data in heatmap_data.items():
                if player_name.lower() in player_id.lower():
                    player_data = data
                    break
            
            if player_data and player_data['heatmap']:
                all_coordinates.extend(player_data['heatmap'])
        except Exception as e:
            print(f"Skipped match {match_id} due to error: {str(e)}")
            skipped_matches += 1
    
    print(f"Processed {len(team_matches) - skipped_matches} matches successfully")
    print(f"Total coordinates collected: {len(all_coordinates)}")
    
    return all_coordinates


def create_season_heatmap(year="2023/2024", league="EPL", player_name="Bruno Fernandes", team_name="Manchester United"):
    """Create a heatmap visualization for an entire season"""
    # Get the combined coordinates
    coordinates = get_season_heatmap_data(year, league, player_name, team_name)
    
    if not coordinates:
        raise ValueError("No heatmap data found for the specified parameters")
    
    # Convert to DataFrame
    coords_df = pd.DataFrame(coordinates, columns=['x', 'y'])
    
    # Apply scaling
    coords_df['x'] = coords_df['x'] * SCALING['x_scale'] + SCALING['x_offset']
    coords_df['y'] = coords_df['y'] * SCALING['y_scale'] + SCALING['y_offset']
    
    # Create figure
    plt.figure(figsize=(13, 8))
    ax = plt.gca()
    
    # Create pitch
    create_soccer_field(ax)
    
    # Create heatmap
    sns.kdeplot(
        data=coords_df, 
        x='x', 
        y='y', 
        cmap='YlOrRd',
        fill=True,
        alpha=1.0,
        levels=HEATMAP_PARAMS['levels'],
        bw_adjust=HEATMAP_PARAMS['bw_adjust'],
        clip=((0, 130), (0, 90)),
        thresh=HEATMAP_PARAMS['thresh']
    )
    
    # Styling
    plt.title(f"{player_name} - {year} Season Heatmap", pad=20, color='black')
    plt.axis('off')
    
    # Set figure background to white
    fig = plt.gcf()
    fig.patch.set_facecolor('white')
    
    return fig


@app.route('/api/heatmap/<player_name>')
def get_heatmap(player_name):
    try:
        coordinates = get_season_heatmap_data(
            year="23/24", 
            league="EPL", 
            player_name=player_name, 
            team_name="Manchester United"
        )
        scaled_coordinates = [
            {
                'x': coord[0] * SCALING['x_scale'] + SCALING['x_offset'],
                'y': coord[1] * SCALING['y_scale'] + SCALING['y_offset']
            }
            for coord in coordinates
        ]
        
        return jsonify({
            'coordinates': scaled_coordinates,
            'pitch_dimensions': {
                'width': 130,
                'height': 90
            }
        })
        
    except Exception as e:
        print(f"Error processing heatmap data: {e}")
        return jsonify({'error': str(e)}), 500
  
if __name__ == '__main__':
    app.run(debug=True, port=8001)
