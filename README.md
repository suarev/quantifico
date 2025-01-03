# Quantifico

Quantifico (Quant + Magnifico) is your go-to dashboard for finding your team's next magnifico through data! Born from the idea that every football team is searching for their game-changing player, this analytics platform transforms complex player statistics into clear, interactive insights all in a single unified view.

### Preview
![image](https://github.com/user-attachments/assets/6284d8e6-df1a-4728-8f97-64aee61892ad)


## Overview
Quantifico is a full-stack web application that combines five core components of player analysis into a single, dynamic dashboard. Currently focused on Premier League 2023/24 season data, this comprehensive toolkit includes a radar chart for performance metrics comparison, a parallel coordinates plot for team-wide analysis, a biplot leveraging PCA for performance distribution, a detailed heatmap showcasing positional tendencies, and a responsive player profile display. Built with React for the frontend and Flask powering the backend, the application integrates data from multiple sources including FBref, StatsBomb, and Sofascore to provide a complete analytical view of player performance. The modular architecture is designed to accommodate future league expansions and additional seasons.
## Technical Implementation

### Frontend Architecture
Our React-based frontend leverages modern web technologies:
- **React.js**: Powers our component architecture with hooks for efficient state management
- **D3.js**: Drives our complex data visualizations 
- **Tailwind CSS**: Ensures a sleek, responsive design
- **Axios**: Handles API communications with our backend

### Backend Infrastructure
Built with a robust Python stack:
- **Flask**: Powers our RESTful API endpoints
- **PostgreSQL/Excel**: Flexible database solutions (see Database Evolution section)
- **pandas & scikit-learn**: Handles complex statistical analysis
- **Data Integration Layer**:
  - SofaScore API: Real-time match and positional data
  - FBref & StatsBomb: Comprehensive player statistics and performance metrics
  - Google Custom Search API: Dynamic player image retrieval

## Core Features & Technical Deep Dive

### 1. Dynamic Radar Chart System
- Visualizes multiple performance metrics simultaneously on a radial plot
- Enables dynamic metric selection from an extensive database of statistics
- Calculates and displays performance percentiles relative to league averages
- Features interactive tooltips showing exact values and league comparisons
- Allows for intuitive performance gap analysis through area comparison

### 2. Advanced Parallel Coordinates Plot
- Visualizes and compares entire teams across multiple performance metrics
- Provides dynamic axis reordering for customized analysis
- Features interactive player highlighting with detailed statistics
- Enables real-time metric selection and comparison
- Shows clear performance distributions across different statistical categories

### 3. Performance Distribution Biplot
- Reduces complex multi-dimensional data into interpretable 2D visualization
- Separates attacking and defensive contributions through principal component analysis
- Shows player clustering and positioning in performance space
- Enables identification of similar players based on statistical profiles
- Features variance explained metrics for both attacking and defensive components
- Provides interactive tooltips with detailed component breakdowns

### 4. Position Heat Map System
- Transforms raw positional data from Sofascore API into intuitive heat maps
- Features precise football pitch rendering with accurate dimensions and markings
- Implements sophisticated kernel density estimation for position intensity calculation
- Provides custom color gradients for intuitive position frequency visualization
- Includes dynamic scaling and viewport adjustments
- Shows accumulated positional tendencies across multiple matches

## Database Evolution

### Initial Excel Implementation (app.py)
- Data stored in structured Excel format
- Quick prototyping and development
- Simple data access patterns
- Perfect for initial development and testing

### PostgreSQL Migration (app_postgresql.py)
- Enhanced data normalization
- Improved query performance
- Better data integrity
- Scalable architecture
- Proper relationship management


## Setup Guide

### Prerequisites
- Node.js (v14 or later)
- Python 3.8+
- npm (Node Package Manager)
- PostgreSQL (optional, for PostgreSQL version)

### Project Structure
```
quantifico/
├── client/          # React frontend
├── server/          # Flask backend
│   └── data/        # Contains data files
│       ├── premier_league_merged_stats_labeled_2324_fbref.xlsx
│       └── statisman_db.sql
```

---

### Backend Setup

#### Option 1: Excel Version (Recommended for Quick Start)
1. Navigate to the server directory:
    ```bash
    cd server
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask server:
    ```bash
    python app.py  # Uses Excel data source
    ```

---

#### Option 2: PostgreSQL Version
1. Ensure PostgreSQL is installed and running.

2. Create the database:
    ```sql
    CREATE DATABASE statisman;
    ```

3. Import the database dump:
    ```bash
    psql -U your_username quantifico < data/statisman_db.sql
    ```

4. Navigate to the server directory and create a virtual environment:
    ```bash
    cd server
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

5. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

6. Run the PostgreSQL version of the Flask server:
    ```bash
    python app_postgresql.py
    ```

---

### Frontend Setup

1. Navigate to the client directory:
    ```bash
    cd client
    ```

2. Install npm packages:
    ```bash
    npm install
    ```

3. Create a `.env` file in the client directory with the following contents:
    ```
    REACT_APP_GOOGLE_API_KEY=your_google_api_key
    REACT_APP_GOOGLE_CX=your_google_custom_search_cx
    ```

4. Start the React development server:
    ```bash
    npm start
    ```

---

### Environment Variables

#### Frontend (`.env`)
```plaintext
REACT_APP_GOOGLE_API_KEY=your_google_api_key
REACT_APP_GOOGLE_CX=your_google_custom_search_cx
```

#### Backend (`.env`)
```plaintext
DB_HOST=localhost
DB_NAME=statisman
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=5432
```

---

### Accessing the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)  
- **Backend API**: [http://localhost:8000](http://localhost:8000) (Excel) or [http://localhost:8001](http://localhost:8001) (PostgreSQL)


## Data Attribution
- Player statistics: FBref.com and StatsBomb
- Match and positional data: Sofascore
- Player images: Google Custom Search API

## Author
Developed by Saurav Sharma as part of academic research.
