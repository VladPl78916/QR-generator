from flask import Flask, render_template, request, send_from_directory
import qrcode
import os
import json
from datetime import datetime
from pyzbar.pyzbar import decode
from PIL import Image

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app = Flask(__name__, 
            static_folder=resource_path('static'),
            template_folder=resource_path('templates'))

app.config['UPLOAD_FOLDER'] = resource_path('static/qrcodes')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = {
        'city': request.form['city'],
        'name': request.form['name'],
        'date': request.form['date'],
        'place1': request.form['place1'],
        'place2': request.form['place2'],
        'place3': request.form['place3'],
        'url': request.form['url']
    }
    
    json_data = json.dumps(data, ensure_ascii=False)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"qr_{timestamp}.png"
    img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return render_template('result.html', 
                           qr_filename=filename, 
                           data=data)

@app.route('/decode', methods=['GET', 'POST'])
def decode_qr():
    if request.method == 'POST':
        file = request.files['qr_file']
        if file:
            img = Image.open(file.stream)
            decoded_objects = decode(img)
            
            if decoded_objects:
                data = json.loads(decoded_objects[0].data)
                return render_template('decode.html', data=data)
            return "QR-код не распознан"
    return render_template('decode.html')

@app.route('/static/qrcodes/<path:filename>')
def serve_qr(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)