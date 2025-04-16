from flask import Flask, request, jsonify, send_from_directory
import os
import requests
import base64
import qrcode
import time
from werkzeug.middleware.proxy_fix import ProxyFix
from PIL import Image
import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


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
@app.route('/sorted-images')
def sorted_images():
    metric = request.args.get('metric', 'luminance')
    category = request.args.get('category', '')
    data_folder = 'data'
    image_scores = []

    for filename in os.listdir(data_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')) and category in filename:
            try:
                with Image.open(os.path.join(data_folder, filename)) as img:
                    img = img.convert('RGB')
                    np_img = np.array(img)

                    if np_img.ndim != 3:
                        continue

                    avg_color = np_img.mean(axis=(0, 1))

                    if metric == 'r':
                        score = avg_color[0]
                    elif metric == 'g':
                        score = avg_color[1]
                    elif metric == 'b':
                        score = avg_color[2]
                    else:
                        score = 0.2126 * avg_color[0] + 0.7152 * avg_color[1] + 0.0722 * avg_color[2]

                    image_scores.append((filename, score))
            except Exception as e:
                app.logger.warning(f"⚠️ Skipped {filename} due to error: {e}")

    sorted_filenames = [fname for fname, _ in sorted(image_scores, key=lambda x: x[1], reverse=True)]
    return jsonify(sorted_filenames)

@app.route('/generate-qr', methods=['POST'])
def generate_qr():
    try:
        image_data = request.form.get('image_data')
        if not image_data:
            app.logger.warning('⚠️ No image data received in request.')
            return jsonify({'success': False, 'error': 'No image data provided'})

        if 'data:image/' in image_data:
            image_data = image_data.split(',')[1]  # Strip data URL header

        timestamp = int(time.time())
        image_filename = f'image_{timestamp}.png'
        qr_filename = f'image_{timestamp}_qr.png'
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)

        image_bytes = base64.b64decode(image_data)
        with open(image_path, 'wb') as f:
            f.write(image_bytes)

        # Debugging logs
        if not os.path.exists(image_path):
            app.logger.error(f'❌ Image file {image_path} was not saved!')
            return jsonify({'success': False, 'error': 'Image not saved'})

        image_size = os.path.getsize(image_path)
        app.logger.info(f'✅ Image saved: {image_path} ({image_size} bytes)')

        if image_size < 100:
            app.logger.warning('⚠️ Image size is suspiciously small — may be blank.')
            return jsonify({'success': False, 'error': 'Saved image is too small or blank'})

        # Upload to ImgBB
        with open(image_path, 'rb') as f:
            files = {'image': f}
            imgbb_response = requests.post(
                'https://api.imgbb.com/1/upload?key=a827f127d1a994df55b303b9ade745ad',
                files=files
            )

        imgbb_data = imgbb_response.json()
        if not imgbb_data.get('success'):
            app.logger.error(f'❌ ImgBB upload failed: {imgbb_data}')
            return jsonify({'success': False, 'error': 'Upload to ImgBB failed'})

        image_url = imgbb_data['data']['image']['url']
        app.logger.info(f'🌐 Image uploaded to ImgBB: {image_url}')

        # Generate QR code
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

        if os.path.exists(qr_path):
            app.logger.info(f'✅ QR code saved at: {qr_path}')
        else:
            app.logger.error(f'❌ QR code was not saved properly at {qr_path}')

        return jsonify({
            'success': True,
            'qr_code': f'/static/qrcodes/{qr_filename}',
            'original_image': image_url
        })

    except Exception as e:
        app.logger.exception('🔥 Exception during QR generation:')
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5502)  # or any other unused port

