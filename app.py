from flask import Flask, render_template, request, redirect, url_for, session
import datetime

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'  # Oturum yönetimi için

# Eğitim içeriği (örneğin video URL'si veya metin)
egitim_icerigi = {
    "baslik": "Python Eğitimi - Temel Kavramlar",
    "aciklama": "Bu eğitimde Python programlama dilinin temellerini, sözdizimini ve bazı örnek uygulamaları öğreneceksiniz.",
    "video_url": "https://www.youtube.com/embed/_uQrJ0TkZlc"  # Gerçek bir YouTube video linki
}


# Test soruları
test_sorulari = [
    {
        "soru": "Python nedir?",
        "secenekler": ["Programlama dili", "Veritabanı", "Web sunucusu", "İşletim sistemi"],
        "dogru": "Programlama dili"
    },
    {
        "soru": "Flask nedir?",
        "secenekler": ["Bir Python framework'ü", "Bir veritabanı", "Bir sunucu", "Bir IDE"],
        "dogru": "Bir Python framework'ü"
    }
]


@app.route('/')
def ana_sayfa():
    # Kullanıcı eğitim içeriğini görüntüleyecek
    # Oturum başlangıç zamanını kaydediyoruz (eğitime başladığı zaman)
    session['egitim_baslangic'] = datetime.datetime.now().isoformat()
    return render_template('egitim.html', icerik=egitim_icerigi)

@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        # Kullanıcı cevaplarını alıp kontrol ediyoruz
        cevaplar = request.form
        skor = 0
        for i, soru in enumerate(test_sorulari):
            kullanici_cevap = cevaplar.get(f"soru_{i}")
            if kullanici_cevap == soru["dogru"]:
                skor += 1
        # Eğitim bitiş zamanını kaydet
        egitim_bitis = datetime.datetime.now()
        egitim_baslangic = datetime.datetime.fromisoformat(session.get('egitim_baslangic'))
        gecen_sure = (egitim_bitis - egitim_baslangic).total_seconds()
        # Sonuçları sonuç sayfasına yönlendiriyoruz
        return redirect(url_for('sonuc', skor=skor, sure=gecen_sure))
    return render_template('test.html', sorular=test_sorulari)

@app.route('/sonuc')
def sonuc():
    skor = request.args.get('skor')
    sure = request.args.get('sure')
    return render_template('sonuc.html', skor=skor, sure=sure)

if __name__ == '__main__':
    app.run(debug=True)
