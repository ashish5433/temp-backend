from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from yolov4 import detect_cars
from algo import optimize_traffic

app = Flask(__name__)
CORS(app)
app.config['DEBUG'] = False
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Set upload size limit

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('videos')
    if len(files) != 4:
        return jsonify({'error': 'Please upload exactly 4 videos'}), 400

    video_paths = []
    for i, file in enumerate(files):
        video_path = os.path.join('uploads', f'video_{i}.mp4')
        file.save(video_path)
        video_paths.append(video_path)

    num_cars_list = []
    for video_file in video_paths:
        try:
            num_cars = detect_cars(video_file)
            num_cars_list.append(num_cars)
        except Exception as e:
            return jsonify({'error': f"Error detecting cars: {str(e)}"}), 500

    try:
        result = optimize_traffic(num_cars_list)
    except Exception as e:
        return jsonify({'error': f"Error optimizing traffic: {str(e)}"}), 500

    return jsonify(result)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True, host="0.0.0.0", port=5000)
