from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# --- LOAD DATA ONCE ---
# Make sure 'scrapping_results.csv' is in the same folder as this script
CSV_FILE = 'scrapping_results.csv'

def clean_claps(clap_str):
    """
    Converts Medium clap strings (e.g., '1.5K', '500', '') into integers.
    """
    if pd.isna(clap_str) or clap_str == '':
        return 0
    
    clap_str = str(clap_str).strip().upper()
    
    if 'K' in clap_str:
        return int(float(clap_str.replace('K', '')) * 1000)
    elif 'M' in clap_str:
        return int(float(clap_str.replace('M', '')) * 1000000)
    
    try:
        return int(clap_str)
    except:
        return 0

try:
    df = pd.read_csv(CSV_FILE)
    # Pre-process claps column to integers for sorting later
    df['Claps_Num'] = df['Claps'].apply(clean_claps)
    # Fill NaN values to avoid errors
    df.fillna('', inplace=True)
    print("Data loaded successfully.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

@app.route('/')
def home():
    return "Medium Search API is Running. Use /search?query=your_keyword"

@app.route('/search', methods=['GET'])
def search_articles():
    query = request.args.get('query', '').lower()
    
    if not query:
        return jsonify({"error": "Please provide a query parameter"}), 400

    if df.empty:
        return jsonify({"error": "Data not loaded"}), 500

    # 1. FILTER: Search for query in Title or Keywords
    # We use string contains logic.
    mask = (
        df['Title'].str.lower().str.contains(query, na=False) | 
        df['Keywords'].str.lower().str.contains(query, na=False) |
        df['Text'].str.lower().str.contains(query, na=False)
    )
    filtered_df = df[mask]

    # 2. SORT: By Claps (Highest first)
    sorted_df = filtered_df.sort_values(by='Claps_Num', ascending=False)

    # 3. SLICE: Top 10
    top_10 = sorted_df.head(10)

    # 4. FORMAT: Return only Title and URL as requested
    results = []
    for _, row in top_10.iterrows():
        results.append({
            "Title": row['Title'],
            "URL": row['URL'],
            "Claps": row['Claps'] # Added for verification, optional
        })

    return jsonify({
        "query": query,
        "count": len(results),
        "results": results
    })

if __name__ == '__main__':
    app.run(debug=True)
