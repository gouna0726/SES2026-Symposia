import os
import re
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), 'sessions')

# Your Track configuration based on the Excel data
TRACKS = {
    "1": "Medalist Symposia and Special Symposia",
    "2": "Biomechanics and Biomaterials",
    "3": "Composites, Advanced Manufacturing, and Intelligent Materials",
    "4": "Advanced Materials",
    "5": "Instability, Fracture, and Fatigue",
    "6": "Fluid Mechanics, Granular and Porous Media, and Complex Fluids",
    "7": "New Frontiers in Mechanics"
}

@app.route('/')
def index():
    """Renders the main 3-pane interface."""
    return render_template('index.html', tracks=TRACKS)

@app.route('/get_sessions/<track_id>')
def get_sessions(track_id):
    """
    Scans the /sessions folder for files matching the track,
    extracts the first line of each for the title, and returns a sorted list.
    """
    session_list = []
    directory = 'sessions'
    
    if not os.path.exists(directory):
        return jsonify([])

    # 1. Filter files that start with the specific track (e.g., t1_s)
    files = [f for f in os.listdir(directory) if f.startswith(f"t{track_id}_s")]
    
    # 2. Sort naturally (1.1, 1.2, ... 1.10)
    files.sort(key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', x)])

    # 3. Extract Titles from the first line of each file
    for filename in files:
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                # Remove prefix "SYMPOSIUM: "
                clean_title = first_line.replace('SYMPOSIUM:', '').strip()
                
                # --- CHANGE IS HERE ---
                # .title() ensures every word starts with a capital letter
                formatted_title = clean_title
                
                session_list.append({
                    "id": filename.replace('.txt', ''),
                    "title": formatted_title
                })
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
            
    return jsonify(session_list)

@app.route('/get_content/<session_id>')
def get_content(session_id):
    file_path = os.path.join(SESSIONS_DIR, f"{session_id}.txt")
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # This removes the prefix but leaves the text exactly as it is in the .txt
        title = lines[0].replace('SYMPOSIUM:', '').strip()
        organizers = lines[1].replace('ORGANIZERS:', '').strip()
        description = "".join(lines[2:])
        
        # Return the raw text
        formatted_text = f"SYMPOSIUM: {title}\nORGANIZERS: {organizers}\n{description}"
        return jsonify({"content": formatted_text})
            
    return jsonify({"content": "Error: Session file not found."}), 404
if __name__ == '__main__':
    # Running in debug mode for easy testing
    app.run(debug=True, port=5000)