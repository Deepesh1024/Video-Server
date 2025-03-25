from flask import Flask, request, send_file, jsonify
import os
import tempfile
from pathlib import Path
from yt_video import download_youtube_video
from VideoEvaluation import VideoAnalyzer

app = Flask(__name__)

@app.route("/download_video", methods=["POST"])
def download_video():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({"error": "URL is required"}), 400

        youtube_url = data.get("url")
        
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as temp_file:
            save_path = temp_file.name
            print(f"Using temporary file: {save_path}")
            download_youtube_video(youtube_url, save_path)
            
            if not os.path.exists(save_path):
                return jsonify({"error": "Download failed"}), 500

            return send_file(save_path, as_attachment=True, mimetype='video/mp4')

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/video_analyzer", methods=["POST"])
def video_analyzer():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        print(f"Received file: {file.filename}")

        # Ensure .mp4 extension since it's an mp4 file
        file_extension = os.path.splitext(file.filename)[1] or ".mp4"
        
        # Create a temporary file with .mp4 suffix
        with tempfile.NamedTemporaryFile(suffix=file_extension, delete=True) as temp_file:
            print(f"Created temp file: {temp_file.name}")
            
            # Write the uploaded mp4 file to the temp file
            file_content = file.read()
            if not file_content:
                return jsonify({"error": "Uploaded MP4 file is empty"}), 400
            
            temp_file.write(file_content)
            temp_file.flush()  # Ensure data is written
            temp_file.seek(0)  # Reset pointer for reading
            print(f"MP4 file size: {os.path.getsize(temp_file.name)} bytes")

            # Try passing the file object first
            try:
                print("Trying VideoAnalyzer with file object...")
                analyzer = VideoAnalyzer(temp_file)
                analysis_output = analyzer.analyze_video()
            except TypeError as te:
                # If file object fails, try the file path
                print(f"TypeError with file object: {str(te)}, trying file path...")
                analyzer = VideoAnalyzer(temp_file.name)
                analysis_output = analyzer.analyze_video()

            print(f"Analysis output: {analysis_output}")
            return jsonify(analysis_output), 200

    except Exception as e:
        print(f"Error in video_analyzer: {str(e)}")
        return jsonify({"error": str(e)}), 500

# @app.route("/video_analyzer", methods=["POST"])
# def video_analyzer():
#     file_path = None  
#     try:
#         if 'file' not in request.files:
#             return jsonify({"error": "No file provided"}), 400

#         file = request.files['file']
#         file_path = os.path.join("temp", file.filename)  
#         os.makedirs("temp", exist_ok=True)
#         file.save(file_path)

#         with open(file_path, 'rb') as f:
#             analyzer = VideoAnalyzer(f)
#             analysis_output = analyzer.analyze_video()

#         if file_path and os.path.exists(file_path):
#             os.remove(file_path)
#         return jsonify(analysis_output), 200
    

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=8001, host="0.0.0.0", debug=False)
