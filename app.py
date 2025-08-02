import os
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from stego_utils import encode_text_in_image, decode_text_from_image

app = Flask(__name__)
app.secret_key = "stegosecret"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    image = request.files['image']
    text = request.form['text']

    if not image or not text:
        flash("Image and text are required.", "error")
        return redirect(url_for('index'))

    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    output_path = os.path.join(UPLOAD_FOLDER, "stego_" + filename)
    try:
        encode_text_in_image(image_path, text, output_path)
    except Exception as e:
        flash(str(e), "error")
        return redirect(url_for('index'))

    return send_file(output_path, as_attachment=True)

@app.route('/decrypt', methods=['POST'])
def decrypt():
    image = request.files['image']
    if not image:
        flash("Stego image is required.", "error")
        return redirect(url_for('index'))

    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    try:
        hidden_text = decode_text_from_image(image_path)
        flash("Decrypted text: " + hidden_text, "success")
    except Exception as e:
        flash("Error: " + str(e), "error")

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
