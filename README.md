# Nearest Places Finder - Streamlit App

This application helps you find the nearest places (food or cafe) based on your location.

## Features

- Select between food places and cafes
- Enter your location coordinates
- View nearest places on an interactive map
- See a table of nearest places with distances

## Installation

1. Clone this repository
2. Install dependencies:

```bash
conda install --yes --file requirements.txt
```

## Running the Application

```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser at http://localhost:8501.

## Data Files

The application uses two JSON files:

- `assets/food.json` - Contains information about food places
- `assets/cafe.json` - Contains information about cafes

Each place in these files should have the following properties:

- `name` - Name of the place
- `address` - Address of the place
- `latitude` - Latitude coordinate
- `longitude` - Longitude coordinate
