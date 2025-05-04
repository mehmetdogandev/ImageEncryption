# ImageCription - Görüntü Şifreleme Sistemi

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3.3-green.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.8.0-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

<p align="center">
  <img src="static/images/logo.png" alt="ImageCription Logo" width="200"/>
</p>

## 📹 Tanıtım Videosu

Bu projenin tanıtım ve kurulum videosunu izlemek için aşağıdaki bağlantıya tıklayabilirsiniz:

[![ImageCription Tanıtım Videosu](https://youtu.be/sONvWO89beE)](https://www.youtube.com/@md-kare)

## 📑 İçindekiler

- [Proje Hakkında](#-proje-hakkında)
- [Özellikler](#-özellikler)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [Algoritma Detayları](#-algoritma-detayları)
- [Güvenlik Analizi](#-güvenlik-analizi)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [İletişim](#-i̇letişim)
- [Lisans](#-lisans)

## 🔒 Proje Hakkında

ImageCription, görüntü dosyalarını güvenli bir şekilde şifrelemek ve deşifrelemek için geliştirilmiş modern bir görüntü güvenlik sistemidir. İki aşamalı şifreleme algoritması (Piksel Karıştırma + XOR) ile güçlü bir koruma sağlar ve web tabanlı arayüzü sayesinde kullanımı oldukça kolaydır.

Bu proje, kişisel görüntülerin güvenliğini sağlamak, hassas tıbbi görüntüleri korumak veya dijital içerik telif haklarını korumak için idealdır. Sistem, güvenli bir şekilde görüntüleri şifreler, deşifreler ve yönetir.

## ✨ Özellikler

- **İki Aşamalı Şifreleme**: 
  - Piksel Karıştırma (Pixel Shuffle): Görüntü piksellerini rastgele karıştırma
  - XOR Şifreleme: Bit düzeyinde XOR işlemi ile şifreleme

- **Kullanıcı Dostu Arayüz**:
  - Sürükle-bırak dosya yükleme
  - Web kamerası ile canlı şifreleme
  - Şifrelenmiş görüntü galerisi

- **Güvenlik Özellikleri**:
  - Kişiselleştirilmiş şifreleme anahtarı
  - Dijital imza (gizli watermark) özelliği
  - Veritabanı ile şifreleme indeksi güvenliği

- **Sistem Özellikleri**:
  - Flask tabanlı web uygulaması
  - SQLite veritabanı entegrasyonu
  - OpenCV ile gelişmiş görüntü işleme

## 💻 Sistem Gereksinimleri

- Python 3.8 veya üzeri
- Tarayıcı: Chrome, Firefox, Edge (son sürümler)
- İnternet bağlantısı (yerel kurulum için)
- Web kamerası (canlı şifreleme özelliği için)

## 🚀 Kurulum

### 1. Repoyu Klonlayın

```bash
git clone https://github.com/mehmetdogandev/imagecription.git
cd imagecription
```

### 2. Sanal Ortam Oluşturun ve Aktive Edin

#### Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt
```

### 4. Uygulamayı Başlatın

```bash
python app.py
```

### 5. Web Tarayıcınızda Açın

```
http://127.0.0.1:5000
```

## 📱 Kullanım

### Görüntü Şifreleme

1. Ana sayfaya gidin (`http://127.0.0.1:5000`)
2. "Görüntü Seç" butonuna tıklayın veya bir görüntüyü alana sürükleyip bırakın
3. "Şifrele" butonuna tıklayın
4. Şifrelenen görüntü ve orijinal görüntü yan yana gösterilecektir
5. "Kaydet" butonuna tıklayarak şifrelenmiş görüntüyü sistemde saklayabilirsiniz

### Canlı Kamera ile Şifreleme

1. Ana sayfada "Kamera Moduna Geç" butonuna tıklayın
2. Kamera izni isteğini onaylayın
3. Görüntünüz canlı olarak şifrelenecektir
4. "Yakala" butonuna tıklayarak o anki şifrelenmiş görüntüyü kaydedebilirsiniz

### Görüntü Galerisi

1. "Galeri" sekmesine tıklayın
2. Daha önce şifrelediğiniz görüntüleri görebilirsiniz
3. Her görüntü için şu işlemleri yapabilirsiniz:
   - Görüntüle: Şifrelenmiş görüntüyü tam boyutta görüntüler
   - Deşifrele: Şifrelenmiş görüntüyü orijinal haline döndürür
   - Sil: Görüntüyü sistemden kaldırır

## 🔐 Algoritma Detayları

ImageCription, iki aşamalı bir şifreleme algoritması kullanır:

### 1. Piksel Karıştırma (Pixel Shuffle)

Bu aşamada, görüntünün pikselleri rastgele bir düzende yeniden sıralanır:

```python
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
```

### 2. XOR Şifreleme

Karıştırılmış piksellere bir XOR işlemi uygulanır ve dijital imza eklenir:

```python
def xor_encrypt(image, key=None):
    # MEHMET DOĞAN isminden anahtar üretelim
    if key is None:
        name = "MEHMET DOĞAN"
        key = sum(ord(char) for char in name) % 256  # 0-255 arasında bir değer
    
    # Kişisel imza uygula
    signed_image = apply_signature(image.copy())
    
    return cv2.bitwise_xor(signed_image, key).astype(np.uint8)
```

### 3. Deşifreleme İşlemi

Deşifreleme, şifreleme adımlarının tersini uygular:

```python
def xor_decrypt(image, key=None):
    # MEHMET DOĞAN isminden anahtar üretelim
    if key is None:
        name = "MEHMET DOĞAN"
        key = sum(ord(char) for char in name) % 256
    
    # XOR işlemi ile çözelim
    return cv2.bitwise_xor(image, key).astype(np.uint8)

def pixel_shuffle_decrypt(image, idx):
    flat = image.reshape(-1, image.shape[2])
    original = np.zeros_like(flat)
    original[idx] = flat
    return original.reshape(image.shape)
```

## 🛡️ Güvenlik Analizi

### Güçlü Yönler

- **İki Katmanlı Şifreleme**: Piksel karıştırma ve XOR şifreleme kombinasyonu güçlü bir koruma sağlar
- **Kişiselleştirilmiş Anahtar**: Her kullanıcı için özel anahtar oluşturulabilir
- **Dijital İmza**: Şifrelenmiş görüntülerde gizli bir dijital imza bulunur
- **Şifreleme İndeksi**: Karıştırma indeksi güvenli bir şekilde veritabanında saklanır

### Dikkat Edilmesi Gerekenler

- **XOR Anahtarı Sınırlaması**: Anahtar değeri 0-255 arasında sınırlıdır
- **İndeks Güvenliği**: Karıştırma indeksi güvenliği kritik önemdedir
- **Sabit Seed**: Aynı seed ile şifrelenen görüntüler benzer karıştırma düzenine sahip olabilir

## 🤝 Katkıda Bulunma

Projeye katkıda bulunmak isterseniz, aşağıdaki adımları izleyebilirsiniz:

1. Projeyi fork edin
2. Özellik dalı oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik: Harika özellik'`)
4. Dalınıza push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Mehmet DOĞAN - [mehmetdogan.dev@gmail.com](mailto:mehmetdogan.dev@gmail.com)

Proje Bağlantısı: [https://github.com/mehmetdogandev/imagecription](https://github.com/mehmetdogandev/imagecription)

### Sosyal Medya & Web

- **Website**: [mehmetdogan.com](https://mehmetdogan.com)
- **LinkedIn**: [linkedin.com/in/mehmetdogandev](https://www.linkedin.com/in/mehmetdogandev/)
- **YouTube**: [youtube.com/@md-kare](https://www.youtube.com/@md-kare)

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakınız.

---

<p align="center">
  <img src="static/images/footer-logo.png" alt="ImageCription Footer Logo" width="150"/>
  <br>
  <strong>Güvenli Görüntü Şifreleme</strong>
</p>