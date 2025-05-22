from flask import Flask, request, jsonify
import os
import json
import tempfile
import logging
from Audio_Server.audio_analysis import analyze_audio_metrics
import subprocess

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename="audio_analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def audio_analysis_main(transcription_file, audio_file):
    try:
        logging.info("Received request for audio analysis.")
        

        with tempfile.TemporaryDirectory() as temp_dir:
            # # Save transcription file
            # transcription_path = os.path.join(temp_dir, transcription_file.filename)
            # transcription_file.save(transcription_path)

            # # Save audio file
            # audio_path = os.path.join(temp_dir, audio_file.filename)
            # audio_file.save(audio_path)

            # logging.info(f"Files saved successfully: {transcription_file.filename}, {audio_file.filename}")
            
            # Pass the temporary file paths to your function
            analysis_results = analyze_audio_metrics(audio_file, transcription_file)
            print("Analysis Results " , analysis_results)
            logging.info("Audio analysis completed successfully.")
            
            with open("json/audio.json", "w") as json_file:
                json.dump(analysis_results, json_file)
                logging.info(f"Analysis results saved to json/audio.json")

        return analysis_results 

    except Exception as e:
        logging.error(f"Error in audio analysis: {str(e)}", exc_info=True)


# if __name__ == "__main__":
#     audio_analysis("json/transcription_output.json", "audio/audio.wav")