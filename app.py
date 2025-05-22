from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import tempfile
from drive_video_download import download_drive_url
import json
from LLM_Server.newtranscriber import VideoTranscriber
from LLM_Server.Overall_Analysis import overall_analyser 
from LLM_Server.Qualitative_Analyser import infer_algorithm_from_trace
from LLM_Server.score_analyser import score_analyser
from Audio_Server.audio_main import audio_analysis_main
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
load_dotenv()
import logging  
app = Flask(__name__)
CORS(app)

@app.route("/download_video", methods=["POST"])
def download_video():
    try:
        temp_path = None
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        print(f"Using temporary file: {temp_path}")
        
        if 'video_file' in request.files:
            file = request.files['video_file']
            print(f"Received file: {file.filename}")
            file_extension = os.path.splitext(file.filename)[1].lower() or ".mp4"
            temp_path = tempfile.NamedTemporaryFile(suffix=file_extension, delete=False).name
            file.save(temp_path)
            # with open("json/presentation.json" , "w") as fp:
            #     json.dump({"presentation_mode" , request.files['presentation_mode']})
            print(f"Saved uploaded video to: {temp_path}, size: {os.path.getsize(temp_path)} bytes")
        elif 'drive_url' in request.form:
            drive_url = request.form['drive_url']
            print(f"Received Google Drive URL: {drive_url}")
            result, status = download_drive_url(drive_url, save_path=temp_path)
            # with open("json/presentation.json" , "w") as fp:
                # json.dump({"presentation_mode" , request.files['presentation_mode']})
            if status != 200:
                return jsonify({"error": {"code": "DOWNLOAD_FAILED", "message": result["error"]}}), status
            print(f"Downloaded video to: {temp_path}, size: {os.path.getsize(temp_path)} bytes")
        else:
            return jsonify({"error": {"code": "NO_INPUT", "message": "No video file or URL provided"}}), 400

        # Validate file
        if not os.path.exists(temp_path):
            return jsonify({"error": {"code": "FILE_NOT_FOUND", "message": "Video file not found"}}), 400
        file_size = os.path.getsize(temp_path)
        if file_size == 0:
            return jsonify({"error": {"code": "EMPTY_FILE", "message": "Video file is empty"}}), 400
        valid_extensions = {".mp4", ".avi", ".mkv", ".mov"}
        file_extension = os.path.splitext(temp_path)[1].lower()
        if file_extension not in valid_extensions:
            return jsonify({"error": {"code": "INVALID_FORMAT", "message": f"Invalid file extension: {file_extension}. Expected: {', '.join(valid_extensions)}"}}), 400
        print(f"Validated video file: {temp_path}, extension: {file_extension}, size: {file_size} bytes")

        # Optional: Validate with moviepy
        try:
            from moviepy.editor import VideoFileClip
            with VideoFileClip(temp_path) as clip:
                duration = clip.duration
                if duration <= 0:
                    return jsonify({"error": {"code": "INVALID_VIDEO", "message": "Video has invalid or zero duration"}}), 400
                print(f"Moviepy validation: duration={duration} seconds")
        except Exception as e:
            print(f"Moviepy validation failed (continuing): {str(e)}")

        # Analyze the video
        try:
            
            from VideoEvaluation import VideoAnalyzer
            # Open file in binary mode for VideoAnalyzer
            with open(temp_path, 'rb') as video_file:
                analyzer = VideoAnalyzer(video_file)
                print(f"Starting video analysis for: {temp_path}")
                analysis_output = analyzer.analyze_video()
                print(f"Analysis output: {analysis_output}")
                convert_video_to_audio(temp_path , "audio/audio.wav") 
                transcriber = VideoTranscriber("video.mp4" , "audio/audio.wav" , "json/transcription_output.json")
                transcript = transcriber.transcribe()
                overall_analysers = overall_analyser(transcript, analysis_output)
                audio_analysers = audio_analysis_main("json/transcription_output.json" , "audio/audio.wav")
                print("Audio analysis output: ", audio_analysers)
                qualitative_analyser_out = infer_algorithm_from_trace(transcript, audio_analysers , overall_analysers)
                print(f"Overall analysis output: {overall_analysers}")
                print("Qualitative analysis output: ", qualitative_analyser_out)
                answer = overall_analysers
                model_name = "gpt-4o"
                llm = ChatOpenAI(model=model_name, api_key=os.getenv("OPENAI_API_KEY"))
                prompt_template2 = ChatPromptTemplate.from_messages([
                    ("system", """Map these Questions and Answers together and return in the json format
                     Questions are : 
                     "1. Did the Speaker Speak with Confidence?",
  "2. Was the content interesting and as per the guidelines provided?",
  "3. Who are you and what are your skills, expertise, and personality traits?",
  "4. Why are you the best person to fit this role?",
  "5. How are you different from others?",
  "6. What value do you bring to the role?",
  "7. Did the speech have a structure of Opening, Body, and Conclusion?",
  "8. Did the speaker vary their tone, speed, and volume while delivering the speech/presentation?",
  "9. How was the quality of research for the topic? Did the speech demonstrate good depth and proper citations?",
  "10. How convinced were you with the overall speech on the topic? Was it persuasive? Will you consider them for the job/opportunity?"""),
                    ("user", "{answer}")
                ])
                output_parser = JsonOutputParser()
                chain2 = prompt_template2 | llm | output_parser
                evaluation = chain2.invoke({
                    "answer": str(answer)
                })
                with open("json/evaluation.json", "w") as file:
                    json.dump(evaluation, file, indent=4)
                score = score_analyser(transcript, audio_analysers ,overall_analysers , evaluation)
                print(f"Score analysis output: {score}")
                form_data = {"transcript" : transcript , "audio" : audio_analysers , "video" : overall_analysers , "score" : score}
                print("Types --------> " , type(transcript) , type(audio_analysers) , type(overall_analysers) , type(score))
                response = requests.post(
                    "http://localhost:8004/create_report",
                    data=form_data,
                    timeout=300
                )
                print(f"Report creation response: {response.status_code}, {response.text}")
                
        except Exception as e:
            print(f"VideoAnalyzer error: {str(e)}")
            return jsonify({"error": {"code": "ANALYSIS_FAILED", "message": f"Video analysis failed: {str(e)}"}}), 400
        
        # Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Deleted temp file: {temp_path}")
        with open('json/output.json' , 'w') as fp:
            json.dump(analysis_output, fp)
            print(f"Saved analysis output to json/output.json")
            
        return jsonify({"message": "Video downloaded and analyzed successfully", "data": analysis_output}), 200

    except Exception as e:
        print(f"Error in download_video: {str(e)}")
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"Deleted temp file: {temp_path}")
        return jsonify({"error": {"code": "SERVER_ERROR", "message": f"Processing error: {str(e)}"}}), 500


from moviepy.editor import VideoFileClip
import os

def convert_video_to_audio(video_path, audio_path):
    """
    Convert a video file to an audio file using moviepy.
    
    Args:
        video_path (str): Path to the input video file (e.g., MP4).
        audio_path (str): Path where the output audio file (e.g., WAV) will be saved.
    
    Returns:
        bool: True if conversion is successful, False otherwise.
    """
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Check if the video has an audio track
        if video.audio is None:
            raise Exception("Video has no audio track")
        
        # Extract and save the audio
        video.audio.write_audiofile(audio_path)
        
        # Close resources
        video.audio.close()
        video.close()
        
        # Verify the audio file was created
        if not os.path.exists(audio_path):
            raise Exception("Audio file was not created")
        
        return True
    except Exception as e:
        print(f"Error converting video to audio: {str(e)}")
        return False
if __name__ == "__main__":
    app.run(port=8001, host="0.0.0.0", debug=True)