import os
import tempfile
import ffmpeg
from flask import Flask, request, send_file, render_template
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

@app.route('/')
def upload_form():
    return '''
    <h2>Upload Video and Audio to Merge</h2>
    <form action="/merge" method="post" enctype="multipart/form-data">
        <label>Video File:</label>
        <input type="file" name="video"><br><br>
        <label>Audio File:</label>
        <input type="file" name="audio"><br><br>
        <label>Duration (seconds, optional):</label>
        <input type="text" name="duration"><br><br>
        <input type="submit" value="Merge">
    </form>
    '''

@app.route('/merge', methods=['POST'])
def merge_files():
    if 'video' not in request.files or 'audio' not in request.files:
        return "Please upload both video and audio files."

    video = request.files['video']
    audio = request.files['audio']
    duration = request.form.get('duration')

    if video.filename == '' or audio.filename == '':
        return "No selected file."

    # Generate unique names using UUID
    video_filename = secure_filename(f"{uuid.uuid4()}_{video.filename}")
    audio_filename = secure_filename(f"{uuid.uuid4()}_{audio.filename}")

    # Create temporary file paths
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video.filename)[-1])
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[-1])
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    temp_trimmed = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")  # File for trimmed version

    video_path = temp_video.name
    audio_path = temp_audio.name
    output_path = temp_output.name
    trimmed_path = temp_trimmed.name

    # Save uploaded files temporarily
    video.save(video_path)
    audio.save(audio_path)

    try:
        # ✅ Merging (Do not change this - it's working!)
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)

        (
            ffmpeg
            .output(input_video, input_audio, output_path, vcodec='copy', acodec='aac', strict='experimental')
            .run(overwrite_output=True)
        )

        # ✅ Trimming (ONLY if duration is provided)
        if duration and duration.isdigit():
            duration = int(duration)
            (
                ffmpeg
                .input(output_path)
                .output(trimmed_path, t=duration, vcodec='copy', acodec='copy')
                .run(overwrite_output=True)
            )
            final_output = trimmed_path  # Use trimmed file
        else:
            final_output = output_path  # Use full merged video

        # ✅ Send final file to user
        return send_file(final_output, as_attachment=True, download_name="merged_video.mp4")

    except ffmpeg.Error as e:
        return f"Error processing video: {e.stderr.decode()}"

    finally:
        # ✅ Delete temp files
        os.remove(video_path)
        os.remove(audio_path)
        os.remove(output_path)
        if os.path.exists(trimmed_path):
            os.remove(trimmed_path)

if __name__ == "__main__":
    app.run(debug=True)
