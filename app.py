import os
import csv
import datetime
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'gizli_anahtar'

CSV_DOSYASI = "sonuclar.csv"

# Eğer CSV dosyası yoksa başlıkları ekle
if not os.path.exists(CSV_DOSYASI):
    with open(CSV_DOSYASI, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Sicil No", "İsim", "Soyisim", "Eğitim Başlangıç", "Eğitim Bitiş",
                         "Geçen Süre (s)", "Doğru Cevap", "Toplam Soru", "Başarı Yüzdesi"])

# Eğitim içeriği
egitim_icerigi = {
    "baslik": "Nezaket Kuralları Eğitimi",
    "aciklama": "Bu eğitimde toplumsal hayatta uyulması gereken temel nezaket kurallarını öğreneceksiniz.",
    "video_url": "https://www.youtube.com/watch?v=CMvZ9UWLQ7Q"  # Gerçek bir video linki ekleyebilirsin
}

# Test soruları
test_sorulari = [
    {
        "soru": "Bir toplantıya girerken ne yapmalısınız?",
        "secenekler": ["Hiçbir şey yapmadan oturmalıyım", "Önce selam vermeliyim", "Direkt konuşmaya başlamalıyım",
                       "Herkesi yok saymalıyım"],
        "dogru": "Önce selam vermeliyim"
    },
    {
        "soru": "Birisi size teşekkür ettiğinde nasıl yanıt vermelisiniz?",
        "secenekler": ["Evet", "Ne demek", "Önemli değil", "Rica ederim"],
        "dogru": "Rica ederim"
    },
    {
        "soru": "Telefonla konuşurken nelere dikkat etmelisiniz?",
        "secenekler": ["Bağırarak konuşmalıyım", "Karşı tarafın sözünü kesmemeliyim",
                       "Sürekli argo kelimeler kullanmalıyım", "Hiç selam vermeden konuşmaya başlamalıyım"],
        "dogru": "Karşı tarafın sözünü kesmemeliyim"
    },
    {
        "soru": "Toplu taşıma araçlarında nasıl davranmalıyız?",
        "secenekler": ["Yaşlılara ve hamilelere yer vermeliyiz", "Yüksek sesle konuşmalıyız",
                       "İnsanlara çarpsak bile özür dilememeliyiz", "Ayaklarımızı koltuklara uzatmalıyız"],
        "dogru": "Yaşlılara ve hamilelere yer vermeliyiz"
    }
]


@app.route('/', methods=['GET', 'POST'])
def giris():
    if request.method == 'POST':
        sicil_no = request.form.get('sicil', '').strip()
        isim = request.form.get('isim', '').strip()
        soyisim = request.form.get('soyisim', '').strip()

        if not sicil_no or not isim or not soyisim:
            return "Lütfen tüm alanları doldurun!", 400

        session['sicil_no'] = sicil_no
        session['isim'] = isim
        session['soyisim'] = soyisim
        session['egitim_baslangic'] = datetime.datetime.now().isoformat()

        return redirect(url_for('egitim'))

    return render_template('giris.html')


@app.route('/egitim')
def egitim():
    return render_template('egitim.html', icerik=egitim_icerigi)


@app.route('/test', methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        cevaplar = request.form
        skor = sum(1 for i, soru in enumerate(test_sorulari) if cevaplar.get(f"soru_{i}") == soru["dogru"])

        egitim_bitis = datetime.datetime.now()
        egitim_baslangic = datetime.datetime.fromisoformat(session.get('egitim_baslangic', egitim_bitis.isoformat()))
        gecen_sure = (egitim_bitis - egitim_baslangic).total_seconds()

        sicil_no = session.get('sicil_no', "Bilinmiyor")
        isim = session.get('isim', "Bilinmiyor")
        soyisim = session.get('soyisim', "Bilinmiyor")

        with open(CSV_DOSYASI, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([sicil_no, isim, soyisim, egitim_baslangic.strftime("%Y-%m-%d %H:%M:%S"),
                             egitim_bitis.strftime("%Y-%m-%d %H:%M:%S"), int(gecen_sure), skor, len(test_sorulari),
                             (skor / len(test_sorulari)) * 100])

        return redirect(url_for('sonuc', skor=skor, sure=int(gecen_sure)))

    # Eğitim içeriği ve test soruları ile birlikte şablona veri gönderiliyor
    return render_template('test.html', sorular=test_sorulari, icerik=egitim_icerigi)


@app.route('/sonuc')
def sonuc():
    try:
        skor = int(request.args.get('skor', 0))
        sure = int(request.args.get('sure', 0))
    except ValueError:
        return "Geçersiz skor veya süre verisi!", 400

    return render_template('sonuc.html', skor=skor, sure=sure)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
