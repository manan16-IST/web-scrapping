from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

CSV_FILE = 'scrapping_results.csv'
data = []

# Load data using standard CSV (Lighter than Pandas)
try:
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    print(f"Loaded {len(data)} rows.")
except Exception as e:
    print(f"Error loading CSV: {e}")

def clean_claps(clap_str):
    if not clap_str: return 0
    s = str(clap_str).strip().upper()
    if 'K' in s: return int(float(s.replace('K', '')) * 1000)
    if 'M' in s: return int(float(s.replace('M', '')) * 1000000)
    try: return int(s)
    except: return 0

@app.route('/')
def home():
    return "API Running! Use /search?query=example"

@app.route('/search')
def search():
    query = request.args.get('query', '').lower()
    if not query: return jsonify({'error': 'No query provided'})

    results = []
    for row in data:
        # Check Title, Keywords, and Text
        content = (str(row.get('Title', '')) + " " + 
                   str(row.get('Keywords', '')) + " " + 
                   str(row.get('Text', ''))).lower()
        
        if query in content:
            row['claps_num'] = clean_claps(row.get('Claps', '0'))
            results.append(row)

    # Sort by claps and take top 10
    results.sort(key=lambda x: x['claps_num'], reverse=True)
    top_10 = results[:10]

    # Format output
    final_output = [{'Title': r.get('Title'), 'URL': r.get('URL')} for r in top_10]
    
    return jsonify({'count': len(final_output), 'results': final_output})

if __name__ == '__main__':
    app.run(debug=True)
