from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import cv2
import numpy as np
import sqlite3
import os
import base64
from datetime import datetime
import uuid
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Session için gizli anahtar
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Klasör yoksa oluştur
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Veritabanı kurulumu
def setup_database():
    conn = sqlite3.connect('encrypted_images.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        original_path TEXT,
        encrypted_path TEXT,
        shuffle_index BLOB
    )
    ''')
    conn.commit()
    conn.close()

# Uygulama başlangıcında veritabanını kur
setup_database()

# Ana sayfa
@app.route('/')
def index():
    return render_template('index.html', active_page='home')

# Şifreli görseller sayfası
@app.route('/gallery')
def gallery():
    conn = sqlite3.connect('encrypted_images.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp FROM images ORDER BY id DESC")
    images = cursor.fetchall()
    conn.close()
    return render_template('gallery.html', images=images, active_page='gallery')

# Resim yakalama ve şifreleme
@app.route('/capture', methods=['POST'])
def capture():
    if 'image' in request.files:
        file = request.files['image']
        if file.filename != '':
            # Dosya adları oluştur
            orig_filename = f"original_{uuid.uuid4().hex}.png"
            enc_filename = f"encrypted_{uuid.uuid4().hex}.png"
            
            # Dosya yolları
            orig_path = os.path.join(app.config['UPLOAD_FOLDER'], orig_filename)
            enc_path = os.path.join(app.config['UPLOAD_FOLDER'], enc_filename)
            
            # Orijinal dosyayı kaydet
            file.save(orig_path)
            
            # OpenCV ile dosyayı oku
            img = cv2.imread(orig_path)
            
            # Şifreleme işlemi - Mehmet DOĞAN'ın imzasını ekledik
            encrypted, idx = pixel_shuffle_encrypt(img.copy())
            fully_encrypted = xor_encrypt(encrypted.copy())
            
            # Şifrelenmiş görüntüyü kaydet
            cv2.imwrite(enc_path, fully_encrypted)
            
            # Veritabanına kaydet
            shuffle_index_bytes = idx.astype(np.int32).tobytes()
            conn = sqlite3.connect('encrypted_images.db')
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO images (timestamp, original_path, encrypted_path, shuffle_index) 
            VALUES (?, ?, ?, ?)
            ''', (datetime.now().isoformat(), orig_filename, enc_filename, shuffle_index_bytes))
            conn.commit()
            image_id = cursor.lastrowid
            conn.close()
            
            return jsonify({
                'status': 'success',
                'message': 'Görüntü şifrelendi ve kaydedildi',
                'original': orig_filename,
                'encrypted': enc_filename,
                'id': image_id
            })
    
    return jsonify({'status': 'error', 'message': 'Görüntü yüklenemedi'})

# Mevcut import'ların altına ekleyin
import base64

# Diğer route'ların arasına ekleyin
@app.route('/live-encrypt', methods=['POST'])
def live_encrypt():
    if 'image' in request.files:
        file = request.files['image']
        
        # Read the image
        img_array = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        # Apply encryption - Mehmet DOĞAN'ın imzasını ekledik
        encrypted, idx = pixel_shuffle_encrypt(img.copy())
        fully_encrypted = xor_encrypt(encrypted.copy())
        
        # Convert back to base64 for sending
        _, buffer = cv2.imencode('.png', fully_encrypted)
        encrypted_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'status': 'success',
            'encrypted_image': encrypted_base64,
            'shuffle_index': idx.tolist()  # Convert to list for JSON serialization
        })
    
    return jsonify({'status': 'error', 'message': 'No image received'})

@app.route('/delete-multiple', methods=['POST'])
def delete_multiple_images():
    data = request.get_json()
    image_ids = data.get('image_ids', [])
    
    if not image_ids:
        return jsonify({'status': 'error', 'message': 'No images selected'})
    
    conn = sqlite3.connect('encrypted_images.db')
    cursor = conn.cursor()
    
    try:
        # Veritabanından görüntüleri sil
        for image_id in image_ids:
            cursor.execute("SELECT original_path, encrypted_path FROM images WHERE id=?", (image_id,))
            row = cursor.fetchone()
            
            if row:
                original_path = row[0]
                encrypted_path = row[1]
                
                # Dosyaları sil
                try:
                    orig_file = os.path.join(app.config['UPLOAD_FOLDER'], original_path)
                    enc_file = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_path)
                    
                    if os.path.exists(orig_file):
                        os.remove(orig_file)
                    if os.path.exists(enc_file):
                        os.remove(enc_file)
                except Exception as e:
                    print(f"Dosya silme hatası: {e}")
                
                # Veritabanından kaydı sil
                cursor.execute("DELETE FROM images WHERE id=?", (image_id,))
        
        conn.commit()
        return jsonify({'status': 'success', 'message': f'{len(image_ids)} images deleted'})
    
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        conn.close()

# Görüntü yükleme
@app.route('/load/<int:image_id>')
def load_image(image_id):
    conn = sqlite3.connect('encrypted_images.db')
    cursor = conn.cursor()
    cursor.execute("SELECT original_path, encrypted_path FROM images WHERE id=?", (image_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        original_path = row[0]
        encrypted_path = row[1]
        
        return jsonify({
            'status': 'success',
            'original': original_path,
            'encrypted': encrypted_path
        })
    
    return jsonify({'status': 'error', 'message': 'Görüntü bulunamadı'})

# Deşifreleme
@app.route('/decrypt/<int:image_id>')
def decrypt_image(image_id):
    conn = sqlite3.connect('encrypted_images.db')
    cursor = conn.cursor()
    cursor.execute("SELECT encrypted_path, shuffle_index FROM images WHERE id=?", (image_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        encrypted_path = row[0]
        shuffle_index = np.frombuffer(row[1], np.int32)
        
        # Şifrelenmiş görüntüyü yükle
        encrypted_img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], encrypted_path))
        
        if encrypted_img is None:
            return jsonify({'status': 'error', 'message': 'Şifreli görüntü okunamadı'})
            
        try:
            # Deşifreleme işlemi - Mehmet DOĞAN'ın anahtarıyla deşifreleme
            xor_decrypted = xor_decrypt(encrypted_img.copy())
            decrypted = pixel_shuffle_decrypt(xor_decrypted, shuffle_index)
            
            # Deşifrelenmiş görüntüyü kaydet
            decrypted_filename = f"decrypted_{uuid.uuid4().hex}.png"
            decrypted_path = os.path.join(app.config['UPLOAD_FOLDER'], decrypted_filename)
            cv2.imwrite(decrypted_path, decrypted)
            
            return jsonify({
                'status': 'success',
                'decrypted': decrypted_filename
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': f'Deşifreleme hatası: {str(e)}'})
    
    return jsonify({'status': 'error', 'message': 'Görüntü bulunamadı'})
@app.route('/algoritma')
def algoritma():
    return render_template('algoritma.html', active_page='algoritma')
# Görüntü silme
@app.route('/delete/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    conn = sqlite3.connect('encrypted_images.db')
    cursor = conn.cursor()
    cursor.execute("SELECT original_path, encrypted_path FROM images WHERE id=?", (image_id,))
    row = cursor.fetchone()
    
    if row:
        original_path = row[0]
        encrypted_path = row[1]
        
        # Veritabanından sil
        cursor.execute("DELETE FROM images WHERE id=?", (image_id,))
        conn.commit()
        conn.close()
        
        # Dosyaları sil
        try:
            orig_path = os.path.join(app.config['UPLOAD_FOLDER'], original_path)
            enc_path = os.path.join(app.config['UPLOAD_FOLDER'], encrypted_path)
            
            if os.path.exists(orig_path):
                os.remove(orig_path)
            if os.path.exists(enc_path):
                os.remove(enc_path)
        except Exception as e:
            print(f"Dosya silme hatası: {e}")
        
        return jsonify({'status': 'success', 'message': 'Görüntü silindi'})
    
    conn.close()
    return jsonify({'status': 'error', 'message': 'Görüntü bulunamadı'})

# Şifreleme fonksiyonları - Mehmet DOĞAN'a özel olarak güncellendi
def pixel_shuffle_encrypt(image, seed=None):
    # MEHMET DOĞAN ismini kullanarak bir seed oluşturalım
    if seed is None:
        # İsimden bir sayı üretme (ASCII değerleri toplamı)
        name = "MEHMET DOĞAN"
        seed = sum(ord(char) for char in name)
    
    np.random.seed(seed)
    flat = image.reshape(-1, image.shape[2])
    idx = np.arange(flat.shape[0])
    np.random.shuffle(idx)
    return flat[idx].reshape(image.shape), idx

def pixel_shuffle_decrypt(image, idx):
    flat = image.reshape(-1, image.shape[2])
    original = np.zeros_like(flat)
    original[idx] = flat
    return original.reshape(image.shape)

def xor_encrypt(image, key=None):
    # MEHMET DOĞAN isminden anahtar üretelim
    if key is None:
        name = "MEHMET DOĞAN"
        key = sum(ord(char) for char in name) % 256  # 0-255 arasında bir değer
    
    # Kişisel imza uygula
    signed_image = apply_signature(image.copy())
    
    return cv2.bitwise_xor(signed_image, key).astype(np.uint8)

def xor_decrypt(image, key=None):
    # MEHMET DOĞAN isminden anahtar üretelim
    if key is None:
        name = "MEHMET DOĞAN"
        key = sum(ord(char) for char in name) % 256  # 0-255 arasında bir değer
    
    # XOR işlemi ile çözelim
    return cv2.bitwise_xor(image, key).astype(np.uint8)

# Görüntü üzerine imza uygulama fonksiyonu
def apply_signature(image):
    # Görüntünün alt kısmına küçük bir imza ekleyelim
    height, width = image.shape[:2]
    signature = "MD"  # Mehmet DOĞAN'ın baş harfleri
    
    # Köşeye bir imza ekleyelim (sadece birkaç piksel)
    for i in range(len(signature)):
        x = width - 10 - (i * 10)
        y = height - 10
        # İmzanın ASCII değerlerini görüntüye gizleyelim
        if x >= 0 and y >= 0:
            pixel_value = ord(signature[i])
            image[y, x, 0] = pixel_value  # Kırmızı kanalında imza
    
    return image

if __name__ == '__main__':
    app.run(debug=True)