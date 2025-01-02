# Quantifico

Quantifico (Quant + Magnifico) is your go-to dashboard for finding your team's next magnifico through data! Born from the idea that every football team is searching for their game-changing player, this analytics platform transforms complex player statistics into clear, interactive insights all in a single unified view.

## Overview
Quantifico is a full-stack web application that combines five core components of player analysis into a single, dynamic dashboard. This comprehensive toolkit includes a radar chart for performance metrics comparison, a parallel coordinates plot for team-wide analysis, a biplot leveraging PCA for performance distribution, a detailed heatmap showcasing positional tendencies, and a responsive player profile display. Built with React for the frontend and Flask powering the backend, the application seamlessly integrates data from multiple sources including FBref, StatsBomb, and Sofascore to provide a complete analytical view of player performance.
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
- **SofaScore API Integration**: Real-time match data collection

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
- Node.js 
- Python 3.8+
- PostgreSQL (for postgresql version)

### Environment Setup

1. Frontend Configuration:
```bash
cd client
npm install

# Create .env file:
REACT_APP_GOOGLE_API_KEY=your_key
REACT_APP_GOOGLE_CX=your_cx
```

2. Backend Configuration:
```bash
cd server
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Create .env file:
DB_HOST=localhost
DB_NAME=quantifico
DB_USER=your_db_user
DB_PASSWORD=your_password
DB_PORT=5432
```

### Running the Application

#### For Excel Version:
```bash
python app.py
```

#### For PostgreSQL Version:
1. Setup Database:
```sql
CREATE DATABASE quantifico;
```

2. Start Backend:
```bash
python app_postgresql.py
```

3. Launch Frontend:
```bash
cd client
npm start
```

Access the dashboard at `http://localhost:3000`

## Data Attribution
- Player statistics: FBref.com and StatsBomb
- Match and positional data: Sofascore
- Player images: Google Custom Search API

## Author
Developed by Saurav Sharma as part of academic research.
