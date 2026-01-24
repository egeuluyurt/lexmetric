# 🏆 LexMetric Mühendislik Zaferleri ve Teknik Güç Raporu

> **Amaç:** Bu belge, LexMetric projesinde aştığımız "çözülmesi zor" teknik engelleri ve kullandığımız "yıkıcı" teknolojileri belgeler. Sıradan bir CRUD uygulaması ile bu proje arasındaki mühendislik farkını ortaya koyar.

---

## 1. Hibrit Zeka Mimarisi (Hybrid Intelligence)
*Sektördeki en büyük sorun olan "LLM Halüsinasyonu"nu nasıl yendik?*

*   **Sorun:** ChatGPT veya Gemini'ye "Bu banka dökümünde toplam ceza ne kadar?" diye sorarsanız, matematiksel işlem hatası yapar (Hallucinated Math). Hukukta %1 hata payı bile kabul edilemez.
*   **Çözümümüz:** Beyni ikiye böldük.
    *   **Sağ Beyin (Gemini 1.5 Flash):** Sadece *anlamı* çözer ("Zelle to Grandson" bir hediyedir). Asla sayıları toplamaz.
    *   **Sol Beyin (Pandas/Python):** Sadece *matematiği* yapar. Cezayı, 60 aylık geriye dönük taramayı ve faizleri hesaplar.
*   **Neden Güçlü?** Bu mimari sayesinde **%100 Matematiksel Kesinlik** ile **Yapay Zeka Yorumlama Gücünü** birleştirdik. Rakiplerin çoğu bunu yapamayıp sadece LLM'e güvenerek hata yapıyor.

## 2. IBM Docling ile "Görülemeyeni Görmek"
*PDF okuma cehennemini nasıl aştık?*

*   **Sorun:** Banka dekontları (Statement) düz yazı değildir. Çok sütunlu, tabloların iç içe geçtiği, görsel gürültülü (logo, reklam) belgelerdir. Standart kütüphaneler (PyPDF2) bunları "çorba" gibi okur.
*   **Çözümümüz:** **IBM Docling**.
    *   Bu teknoloji, sayfayı bir "resim" olarak görür ve yapay zeka ile tablonun sınırlarını çizer.
    *   Sütunlar birbirine girse bile Docling, hücre hücre ayırır.
*   **Zafer:** İnsan gözüyle bile zor okunan karışık banka dökümlerini, sanki Excel dosyasıymış gibi temiz bir DataFrame'e dönüştürdük.

## 3. "Hunter-Seeker" Excel Motoru
*Her müşterinin farklı Excel formatı yollaması sorununu nasıl çözdük?*

*   **Sorun:** Avukatlar Excel yollar ama başlık satırı (Header) bazen 1. satırda, bazen 5. satırda olur. Bazen "Amount" yazar, bazen "Debit/Credit", bazen "Withdrawal".
*   **Çözümümüz (`excel_processor.py`):**
    *   Geliştirdiğimiz algoritma, Excel dosyasını tarar ve içinde "Date" ve "Description" geçen satırı **otomatik avlar (Hunter)**.
    *   Ardından sütun isimlerini **normalize eder (Seeker)**. "Trx Date", "Posting Date", "Date" -> Hepsi sistemde "Date" olur.
*   **Zafer:** Kullanıcı dosyasını düzenlemek zorunda kalmaz. Sistem "ne atarsan at" mantığıyla çalışır (Robustness).

## 4. Adli Anomali Dedektifi (Forensic Engine)
*Yapay Zeka'nın göremediği "yapısal" hileleri nasıl yakaladık?*

*   **Sorun:** Bir transferin açıklamasında "Gift" yazmıyorsa AI bunu kaçırabilir. Ancak dolandırıcılar "yapısal" izler bırakır.
*   **Çözümümüz (`anomaly_detection.py`):**
    *   **Round Number Detection:** İnsanlar faturaları küsüratlı öder ($124.53). Eğer $10,000.00 gibi tam sayı transferler varsa, bu büyük ihtimalle "elden borç verme" veya "hediye"dir.
    *   **Frequency Pattern:** Aynı kişiye 5 kere para gittiyse, tek tek bakınca küçük olabilir ama toplamda büyük bir servet transferidir.
*   **Zafer:** Sadece metni değil, **sayıların psikolojisini** analiz eden bir katman ekledik.

## 5. Sıfır-İz Politikası (Zero-Persistence)
*Gizlilik paranoyasını nasıl avantaja çevirdik?*

*   **Sorun:** Medicaid verileri (yaşlıların mali durumu) çok hassastır (PII). Bu verileri veritabanında saklamak büyük yasal yük (HIPAA) getirir.
*   **Çözümümüz:** **RAM-Only Architecture.**
    *   Yüklenen dosya işlenir, analiz edilir, rapor üretilir.
    *   Sayfa kapatıldığı an **her şey RAM'den silinir**. Diske asla kayıt düşülmez.
*   **Zafer:** "Verilerim çalınır mı?" korkusunu teknik mimari ile **imkansız** hale getirdik. Veri yoksa, çalınacak bir şey de yoktur.

---

## Özet: Neden Güçlüyüz?

| Teknoloji | Rakipler | Biz (LexMetric) |
| :--- | :--- | :--- |
| **PDF Okuma** | Regex / PyPDF (Kırılgan) | **IBM Docling (Görsel Zeka)** |
| **Analiz** | Sadece LLM (Hata Yapar) | **Hybrid (LLM + Pandas)** |
| **Veri Girişi** | Şablon Zorunlu | **Format-Agnostik (Her şeyi yutar)** |
| **Gizlilik** | Veritabanı | **RAM-Only (Sıfır İz)** |

Bu proje, bir "Web Sitesi" değil, bir **"Adli Hesaplama Motoru"dur (Forensic Computational Engine)**. Gücü de buradan gelir.
