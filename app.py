from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import base64
import qrcode
import time
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__, static_url_path='', static_folder='.')
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB upload limit

UPLOAD_FOLDER = 'uploads'
QR_FOLDER = 'static/qrcodes'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

@app.route('/data/<path:filename>')
def serve_image(filename):
    return send_from_directory('data', filename)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/data/<path:filename>')
def serve_data(filename):
    return send_from_directory('data', filename)

@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    try:
        image_data = request.form.get('image_data')
        if not image_data:
            return jsonify({'success': False, 'error': 'No image data provided'})

        if 'data:image/' in image_data:
            image_data = image_data.split(',')[1]  # Strip the data URL header

        timestamp = int(time.time())
        image_filename = f'image_{timestamp}.png'
        qr_filename = f'image_{timestamp}_qr.png'

        image_path = os.path.join(UPLOAD_FOLDER, image_filename)

        image_bytes = base64.b64decode(image_data)
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        if not os.path.exists(image_path) or os.path.getsize(image_path) < 100:
            return jsonify({'success': False, 'error': 'Saved image is invalid'})

        # Upload to ImgBB
        with open(image_path, 'rb') as f:
            files = {'image': f}
            imgbb_response = requests.post(
                'https://api.imgbb.com/1/upload?key=a827f127d1a994df55b303b9ade745ad',
                files=files
            )

        imgbb_data = imgbb_response.json()
        if not imgbb_data.get('success'):
            return jsonify({'success': False, 'error': 'Upload to ImgBB failed'})

        image_url = imgbb_data['data']['image']['url']

        # Generate QR code from URL
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(image_url)
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_path = os.path.join(QR_FOLDER, qr_filename)
        qr_img.save(qr_path)

        return jsonify({
            'success': True,
            'qr_code': f'/static/qrcodes/{qr_filename}',
            'original_image': image_url
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5500)
