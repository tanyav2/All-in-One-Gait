import os
import tempfile
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import sys

# Add the necessary paths
sys.path.append(os.path.abspath('.'))
from demo.libs.main import main

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = './demo/output/InputVideos/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limit to 100MB upload

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/process', methods=['POST'])
def process_videos():
    # Check if the post request has files
    if 'gallery' not in request.files:
        return jsonify({"error": "No gallery file uploaded"}), 400
    
    # Get threshold parameter (default to 11.5 if not provided)
    threshold = request.form.get('threshold', 11.5, type=float)
    
    # Get gallery video
    gallery_file = request.files['gallery']
    if gallery_file.filename == '':
        return jsonify({"error": "No gallery file selected"}), 400
    
    # Create a temporary directory for uploaded files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save gallery file
        gallery_filename = secure_filename(gallery_file.filename)
        gallery_path = os.path.join(temp_dir, gallery_filename)
        gallery_file.save(gallery_path)
        
        # Get probe videos
        probe_files = request.files.getlist('probe')
        probe_paths = []
        
        if not probe_files or all(f.filename == '' for f in probe_files):
            return jsonify({"error": "No probe files uploaded"}), 400
        
        # Save probe files
        for probe_file in probe_files:
            if probe_file.filename != '':
                probe_filename = secure_filename(probe_file.filename)
                probe_path = os.path.join(temp_dir, probe_filename)
                probe_file.save(probe_path)
                probe_paths.append(probe_path)
        
        try:
            # Process the videos using the main function
            results = main(
                gallery_path=gallery_path,
                probe_paths=probe_paths,
                threshold=threshold
            )
            
            # Format the results
            formatted_results = []
            for result in results:
                probe_name = os.path.basename(result['path'])
                formatted_result = {
                    "probe_name": probe_name,
                    "match_result": result['result'] is not None,
                    "match_details": result['result'] if result['result'] is not None else "No match found"
                }
                formatted_results.append(formatted_result)
            
            return jsonify({
                "success": True,
                "threshold": threshold,
                "results": formatted_results,
                "output_location": "./demo/output/OutputVideos/" 
            }), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route('/docs', methods=['GET'])
def api_docs():
    return jsonify({
        "endpoints": [
            {
                "path": "/health",
                "method": "GET",
                "description": "Health check endpoint"
            },
            {
                "path": "/process",
                "method": "POST",
                "description": "Process gait videos",
                "parameters": {
                    "gallery": "Required. The gallery video file to use as reference",
                    "probe": "Required. One or more probe video files to compare against the gallery",
                    "threshold": "Optional. Threshold value for matching (default: 11.5)"
                },
                "example_curl": "curl -X POST -F 'gallery=@path/to/gallery.mp4' -F 'probe=@path/to/probe1.mp4' -F 'probe=@path/to/probe2.mp4' -F 'threshold=10.0' http://localhost:8080/process"
            }
        ]
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False) 