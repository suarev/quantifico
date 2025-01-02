from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import io
import base64
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')  # Required for headless mode
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Arc
from ScraperFC import Sofascore
import numpy as np
from tqdm import tqdm  # For progress bar
from flask import Flask, jsonify, request  # Add request import
from flask import request
import json


app = Flask(__name__)
CORS(app)

def load_player_data():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, 'data', 'premier_league_merged_stats_labeled_2324_fbref.xlsx')
        print(f"Attempting to read file from: {file_path}")
        
        df = pd.read_excel(file_path, engine='openpyxl')
        print("Successfully read Excel file")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

@app.route('/api/player/<player_name>')
def get_player_info(player_name):
    try:
        df = load_player_data()
        if df is None:
            return jsonify({'error': 'Data loading failed'}), 500
            
        player = df[df['player'] == player_name].iloc[0]
        
        player_info = {
            'name': player['player'],
            'value': player['Value'],
            'team': player['team'],
            'nationality': player['nation_'],
            'position': player['pos_'],
            'age': int(player['age_']),
            'matches_played': int(player['Playing Time_MP'])
        }
        
        return jsonify(player_info)
        
    except IndexError:
        return jsonify({'error': 'Player not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/search')
def search_players():
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'players': []})
            
        df = load_player_data()
        
        matches = []
        for idx, row in df.iterrows():
            player_name = row['player'].lower()
            name_parts = player_name.split()
            if (any(part.startswith(query) for part in name_parts) or
                query in player_name):
                matches.append(row['player'])
        
        matches = sorted(list(set(matches)))[:5]
        return jsonify({'players': matches})
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500
    try:
        query = request.args.get('q', '').lower()
        if not query:
            return jsonify({'players': []})
            
        df = load_player_data()
        
        matches = []
        for player in df['player']:
            if query in player.lower():
                matches.append(player)
                
            parts = player.lower().split()
            if len(parts) > 1 and query in parts[-1]:
                matches.append(player)
                
        matches = list(set(matches))
        matches.sort()
        
        return jsonify({'players': matches})
        
    except Exception as e:
        print(f"Error in search: {e}")
        return jsonify({'error': str(e)}), 500

def normalize_value(value, min_val, max_val):
    """Normalize value to 0-100 scale"""
    if max_val == min_val:
        return 50  
    return ((value - min_val) / (max_val - min_val)) * 100




def convert_value_to_millions(value_str):
    """Convert value string (e.g., '€900k', '€70.00m') to float in millions"""
    try:
        value_str = str(value_str).replace('€', '')
        
        if 'm' in value_str:
            return float(value_str.replace('m', ''))
        elif 'k' in value_str:
            return float(value_str.replace('k', '')) / 1000
        else:
            return float(value_str) / 1000000
    except Exception as e:
        print(f"Error converting value: {value_str}, {str(e)}")
        return 0.0

def get_primary_position(pos_str):
    """Extract primary position from position string"""
    if pd.isna(pos_str) or not pos_str:
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


@app.route('/api/parallel/<player_name>')
def get_parallel_data(player_name):
    try:
        df = load_player_data()
        if df is None:
            return jsonify({'error': 'Data loading failed'}), 500
            

        metrics_param = request.args.get('metrics')
        if metrics_param:
            metrics = json.loads(metrics_param)
        else:
           
            metrics = {
                'Position': 'pos_', 
                'Minutes': 'Playing Time_Min',
                'Age': 'age_',
                'Value': 'Value',
                'Goals': 'Performance_Gls',
                'Assists': 'Performance_Ast',
                'SCA': 'goal_shot_creation_SCA_SCA',
                'Key Passes': 'passing_KP_',
                'Tackles + Int': 'defensive_Tkl+Int_',
                'Prog Carries': 'possession_Carries_PrgC',
                'Prog Passes': 'passing_PrgP_'
            }

     
        player_team = df[df['player'] == player_name]['team'].iloc[0]
    
        team_players = df[df['team'] == player_team].copy()
        
        team_players['position_category'] = team_players['pos_'].apply(get_primary_position)
        
        result = {
            'players': team_players['player'].tolist(),
            'metrics': list(metrics.keys()),
            'data': [],
            'domains': {
                'Position': ['GK', 'DF', 'MF', 'FW']
            }
        }
        
        for _, player in team_players.iterrows():
            player_data = {
                'player': player['player'],
                'values': {}
            }
            
            for metric_name, column in metrics.items():
                value = player[column]
                if metric_name == 'Position':
                    value = get_primary_position(player['pos_'])
                elif metric_name == 'Value':
                    value = convert_value_to_millions(value)
                else:
                    try:
                        value = float(value)
                    except (TypeError, ValueError):
                        value = 0.0
                
                player_data['values'][metric_name] = value
                
            result['data'].append(player_data)
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error processing parallel coordinates data: {e}")
        return jsonify({'error': str(e)}), 500
@app.route('/api/scatter/<player_name>')
def get_scatter_data(player_name):
    try:
        df = load_player_data()
        if df is None:
            return jsonify({'error': 'Data loading failed'}), 500
            
   
        midfielders = df[df['pos_'].str.contains('MF', na=False)].copy()
       
        attacking_metrics = [
            'goal_shot_creation_SCA_SCA90',  # SCA
            'passing_KP_',                    # Key passes
            'possession_Carries_PrgC',        # Progressive carries
            'passing_PrgP_',                  # Progressive passes
            'Per 90 Minutes_xAG',            # xAG/90
            'Per 90 Minutes_npxG',           # npxG/90
            'possession_Take-Ons_Succ%'      # Take ons success rate
        ]
        
        defensive_metrics = [
            'misc_Aerial Duels_Won%',        # Aerial duels won
            'defensive_Challenges_Tkl%',      # Defensive challenges tackled
            'defensive_Blocks_Blocks',        # Defensive blocks
            'defensive_Int_'                  # Defensive interceptions
        ]
        
      
        def calculate_pca(metrics):
            X = midfielders[metrics].fillna(0)
            
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            pca = PCA(n_components=1)
            principal_components = pca.fit_transform(X_scaled)
            
            return principal_components.flatten(), pca.explained_variance_ratio_[0]
        
        attacking_pca, att_variance = calculate_pca(attacking_metrics)
        defensive_pca, def_variance = calculate_pca(defensive_metrics)
        
        result = {
            'players': midfielders['player'].tolist(),
            'data': [],
            'selected_player': player_name,
            'variance_explained': {
                'attacking': round(att_variance * 100, 2),
                'defensive': round(def_variance * 100, 2)
            }
        }
        
        for i, player in enumerate(midfielders['player']):
            result['data'].append({
                'player': player,
                'attacking': float(attacking_pca[i]),
                'defensive': float(defensive_pca[i]),
                'team': midfielders.iloc[i]['team']
            })
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error processing scatter plot data: {e}")
        return jsonify({'error': str(e)}), 500
    

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
    

@app.route('/api/available-metrics')
def get_available_metrics():
    try:
        df = load_player_data()
        if df is None:
            return jsonify({'error': 'Data loading failed'}), 500
      
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
       
        if 'pos_' not in numerical_cols:
            numerical_cols.append('pos_')

   
        metrics = [
            {
                'value': col,
                'label': col  
            }
            for col in numerical_cols
        ]
        
        return jsonify({'metrics': metrics})
        
    except Exception as e:
        print(f"Error getting metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/radar/<player_name>')
def get_radar_data(player_name):
    try:
        df = load_player_data()
        if df is None:
            return jsonify({'error': 'Data loading failed'}), 500

        
        metrics_param = request.args.get('metrics')
        if metrics_param:
            metrics = json.loads(metrics_param)
        else:
           
            metrics = {
                'Shot Creating Actions': 'goal_shot_creation_SCA_SCA',
                'Key Passes': 'passing_KP_',
                'Prog. Carries': 'possession_Carries_1/3',
                'Prog. Passes': 'passing_PrgP_',
                'xAG': 'Expected_xAG',
                'npxG': 'Expected_npxG',
                'Tackles+Interceptions': 'defensive_Tkl+Int_',
                'Take-ons Succ.': 'possession_Take-Ons_Succ%',
                'Recoveries': 'misc_Performance_Recov'
            }
        
       
        midfielders = df[df['pos_'].str.contains('MF', na=False)]
        player_data = df[df['player'] == player_name].iloc[0]

        player_values = {}
        league_averages = {}
        raw_values = {}

        for display_name, column in metrics.items():
            min_val = midfielders[column].min()
            max_val = midfielders[column].max()
            avg_val = midfielders[column].mean()
            
            raw_values[display_name] = {
                'player': float(player_data[column]),
                'league_avg': float(avg_val),
                'max': float(max_val)
            }
            
            player_values[display_name] = normalize_value(player_data[column], min_val, max_val)
            league_averages[display_name] = normalize_value(avg_val, min_val, max_val)
        
        return jsonify({
            'player': player_values,
            'league_average': league_averages,
            'raw_values': raw_values,
            'metrics': list(metrics.keys())
        })
        
    except Exception as e:
        print(f"Error processing radar data: {e}")
        return jsonify({'error': str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=8000)