from flask import Flask, Response, render_template
import subprocess

app = Flask(__name__)

video_files = ["wallpaper/ffv76cb.mp4"]


@app.route('/live')
def index():
    return render_template('index.html')


@app.route('/live/stream')
def live_stream():
    def generate():
        while True:
            for video_file in video_files:
                command = ["ffmpeg", "-re", "-i", video_file, "-f", "mpegts", "-codec:v",
                           "mpeg1video", "-s", "640x480", "-b:v", "800k", "-r", "30", "-"]
                process = subprocess.Popen(command, stdout=subprocess.PIPE)
                while True:
                    data = process.stdout.read(1024)
                    if not data:
                        break
                    yield data

    return Response(generate(), mimetype='video/mp2t')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)
