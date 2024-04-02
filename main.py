import tkinter as tk
from tkinter import messagebox, Scrollbar
from tkcalendar import Calendar
import sqlite3
import os
import requests
import base64
from mailersend import emails


class AyarlarPenceresi:
    def __init__(self, parent, cursor, baglanti):
        self.parent = parent
        self.cursor = cursor
        self.baglanti = baglanti

        self.ayarlar_penceresi = tk.Toplevel(parent)
        self.ayarlar_penceresi.title("Ayarlar")
        self.ayarlar_penceresi.geometry("300x250")

        self.label_eski_sifre = tk.Label(self.ayarlar_penceresi, text="Mevcut Şifre:", font=("Helvetica", 11))
        self.label_eski_sifre.grid(row=0, column=0)
        self.entry_eski_sifre = tk.Entry(self.ayarlar_penceresi, show="*", font=("Helvetica", 11))
        self.entry_eski_sifre.grid(row=0, column=1)

        self.label_yeni_sifre = tk.Label(self.ayarlar_penceresi, text="Yeni Şifre:", font=("Helvetica", 11))
        self.label_yeni_sifre.grid(row=1, column=0)
        self.entry_yeni_sifre = tk.Entry(self.ayarlar_penceresi, show="*", font=("Helvetica", 11))
        self.entry_yeni_sifre.grid(row=1, column=1)

        self.buton_kaydet = tk.Button(self.ayarlar_penceresi, text="Şifre Kaydet", command=self.sifre_degistir,
                                      font=("Helvetica", 11))
        self.buton_kaydet.grid(row=2, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.ayarlar_penceresi, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=3, column=0, padx=5, pady=5)

        self.label_eposta = tk.Label(self.ayarlar_penceresi, text="E-posta Adresi:", font=("Helvetica", 11))
        self.label_eposta.grid(row=4, column=0)
        self.entry_eposta = tk.Entry(self.ayarlar_penceresi, font=("Helvetica", 11))
        self.entry_eposta.grid(row=4, column=1)

        self.buton_eposta_kaydet = tk.Button(self.ayarlar_penceresi, text="E-posta Kaydet", command=self.eposta_kaydet,
                                             font=("Helvetica", 11))
        self.buton_eposta_kaydet.grid(row=5, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.ayarlar_penceresi, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=6, column=0, padx=5, pady=5)

        self.buton_guncelle = tk.Button(self.ayarlar_penceresi, text="Uygumalamayı Güncelle",
                                        command=self.githubdan_guncelle,
                                        font=("Helvetica", 11))
        self.buton_guncelle.grid(row=7, column=0, columnspan=2)

    def sifre_degistir(self):
        eski_sifre = self.entry_eski_sifre.get()
        yeni_sifre = self.entry_yeni_sifre.get()

        dogru_sifre = self.cursor.execute("SELECT sifre FROM kullanici").fetchone()[0]

        if eski_sifre == dogru_sifre:
            self.cursor.execute("UPDATE kullanici SET sifre=?", (yeni_sifre,))
            self.baglanti.commit()
            messagebox.showinfo("Başarılı", "Şifre başarıyla değiştirildi.")
            self.ayarlar_penceresi.destroy()
        else:
            messagebox.showerror("Hata", "Mevcut şifreyi yanlış girdiniz.")

    def eposta_kaydet(self):
        eposta = self.entry_eposta.get()

        self.cursor.execute("UPDATE kullanici SET eposta=?", (eposta,))
        self.baglanti.commit()
        messagebox.showinfo("Başarılı", "E-posta başarıyla kaydedildi.")
        self.ayarlar_penceresi.destroy()

    def githubdan_guncelle(self):
        # GitHub API'si aracılığıyla kod deposundan en son sürümü almak için istek gönder
        user = "md3m1ray"  # GitHub kullanıcı adınızı buraya girin
        repo = "AjandaNotDefteriED"  # GitHub deposunun adını buraya girin
        branch = "master"  # Varsayılan olarak ana branch kullanılır, gerektiğinde değiştirin
        url = f"https://api.github.com/repos/{user}/{repo}/git/refs/heads/{branch}"
        response = requests.get(url)
        if response.status_code == 200:
            # API yanıtını analiz ederek en son commit'in SHA'sını alın
            latest_commit_sha = response.json()["object"]["sha"]

            # GitHub'dan bu commit'in ağacını alın
            url = f"https://api.github.com/repos/{user}/{repo}/git/trees/{latest_commit_sha}?recursive=1"
            response = requests.get(url)
            if response.status_code == 200:
                # API yanıtını analiz ederek dosyaları alın
                files = response.json()["tree"]
                for file in files:
                    if file["type"] == "blob":  # Sadece dosyaları alın, klasörleri yok sayın
                        # GitHub'dan dosyayı indirin
                        url = file["url"]
                        response = requests.get(url)
                        if response.status_code == 200:
                            # Dosyayı yerel olarak kaydedin
                            file_content_b64 = response.json()["content"]
                            file_content = base64.b64decode(file_content_b64)
                            file_name = file["path"]
                            file_path = os.path.join(os.getcwd(), file_name)
                            with open(file_path, "wb") as f:
                                f.write(file_content)

                        else:
                            messagebox.showerror("Hata", "Dosya indirme hatası. Daha sonra tekrar deneyiniz")

        else:
            messagebox.showerror("Hata", "En son güncelleme bilgisi alınamadı. Daha sonra tekrar deneyiniz")

        messagebox.showinfo("Güncelleme", "Uygulama başarıyla güncellendi!. Lütfen Uygulamayı Yeniden Başlatın.")


class AjandaUygulamasi:
    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("Ajanda Not Defteri")

        self.giris_penceresi = tk.Toplevel(pencere)
        self.giris_penceresi.title("Kullanıcı Girişi")
        self.giris_penceresi.geometry("250x50")

        self.label_sifre = tk.Label(self.giris_penceresi, text="Şifre:", font=("Helvetica", 11))
        self.label_sifre.grid(row=0, column=0)

        self.entry_sifre = tk.Entry(self.giris_penceresi, show="*", font=("Helvetica", 11))
        self.entry_sifre.grid(row=0, column=1)

        self.buton_giris = tk.Button(self.giris_penceresi, text="Giriş", command=self.giris_kontrol,
                                     font=("Helvetica", 11))
        self.buton_giris.grid(row=1, column=0, columnspan=2)

        self.veritabani_yolu = os.path.join(os.path.dirname(__file__), "ajanda.db")

        self.baglanti = sqlite3.connect(self.veritabani_yolu)
        self.cursor = self.baglanti.cursor()

    def giris_kontrol(self):
        giris_sifresi = self.entry_sifre.get()
        dogru_sifre = self.cursor.execute("SELECT sifre FROM kullanici").fetchone()[0]

        if giris_sifresi == dogru_sifre:
            self.giris_penceresi.destroy()
            self.uygulama_ac()
        else:
            messagebox.showerror("Hata", "Yanlış şifre! Tekrar deneyin.")

    def uygulama_ac(self):
        self.ajanda = Ajanda(self.cursor, self.baglanti)

        self.buton_ayarlar = tk.Button(self.pencere, text="Ayarlar", command=self.ayarlar_ac, font=("Helvetica", 11),
                                       fg="red")
        self.buton_ayarlar.grid(row=0, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.pencere, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=1, column=1, padx=5, pady=5)

        self.tarih_secici = Calendar(self.pencere, selectmode="day", date_pattern="yyyy-mm-dd")
        self.tarih_secici.grid(row=2, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.pencere, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=3, column=1, padx=5, pady=5)

        self.entry_not = tk.Entry(self.pencere, width=80, font=("Helvetica", 11))
        self.entry_not.grid(row=4, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.pencere, height=2, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=5, column=1, padx=5, pady=5)

        self.buton_not_ekle = tk.Button(self.pencere, text="Not Ekle", command=self.not_ekle, font=("Helvetica", 11),
                                        fg="blue")
        self.buton_not_ekle.grid(row=6, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.pencere, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=7, column=1, padx=5, pady=5)

        self.liste_notlar = tk.Listbox(self.pencere, height=15, width=80, font=("Helvetica", 11))
        self.liste_notlar.grid(row=8, column=0, columnspan=2)
        self.liste_notlar.bind('<<ListboxSelect>>', self.notlari_goruntule)

        self.scrollbar = Scrollbar(self.pencere, orient="vertical", command=self.liste_notlar.yview)
        self.scrollbar.grid(row=8, column=2, sticky='ns')
        self.liste_notlar.config(yscrollcommand=self.scrollbar.set)

        self.scrollbar_x = Scrollbar(self.pencere, orient="horizontal", command=self.liste_notlar.xview)
        self.scrollbar_x.grid(row=9, column=0, columnspan=2, sticky='ew')
        self.liste_notlar.config(xscrollcommand=self.scrollbar_x.set)

        self.cekirdek_frame = tk.Frame(self.pencere, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=10, column=1, padx=5, pady=5)

        self.buton_eposta_gonder = tk.Button(self.pencere, text="E-posta Gönder", command=self.eposta_gonder,
                                             font=("Helvetica", 11))
        self.buton_eposta_gonder.grid(row=11, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.pencere, height=10, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=12, column=1, padx=5, pady=5)

        self.label_sil_not_index = tk.Label(self.pencere, text="Silinecek Notun Numarası:", font=("Helvetica", 11))
        self.label_sil_not_index.grid(row=13, column=0, columnspan=2)

        self.entry_sil_index = tk.Entry(self.pencere, width=5)
        self.entry_sil_index.grid(row=14, column=0, columnspan=2)

        self.buton_not_sil = tk.Button(self.pencere, text="Notu Sil", command=self.not_sil, font=("Helvetica", 11),
                                       fg="red")
        self.buton_not_sil.grid(row=15, column=0, columnspan=2)

        self.cekirdek_frame = tk.Frame(self.pencere, height=15, bd=5, relief="sunken")
        self.cekirdek_frame.grid(row=16, column=1, padx=5, pady=5)

        self.label_sil_not_index = tk.Label(self.pencere, text="by M. DEMİRAY 2024 V.1.1", font=("Helvetica", 8))
        self.label_sil_not_index.grid(row=17, column=0, columnspan=2)

        # Uygulama kapatıldığında veritabanı bağlantısını kapat
        self.pencere.protocol("WM_DELETE_WINDOW", self.pencere_kapatildi)

        # Başlangıçta notları yükle
        self.notlari_goruntule()

    def pencere_kapatildi(self):
        self.baglanti.close()
        self.pencere.destroy()

    def not_ekle(self):
        tarih = self.tarih_secici.get_date()
        not_metni = self.entry_not.get()
        self.ajanda.not_ekle(tarih, not_metni)
        self.entry_not.delete(0, tk.END)
        self.notlari_goruntule()

    def notlari_goruntule(self, event=None):
        self.liste_notlar.delete(0, tk.END)
        secili_tarih = self.tarih_secici.get_date()
        if secili_tarih in self.ajanda.notlar:
            for indeks, not_metni in enumerate(self.ajanda.notlar[secili_tarih]):
                self.liste_notlar.insert(tk.END, f"{indeks}: {not_metni}")

    def not_sil(self):
        tarih = self.tarih_secici.get_date()
        not_index = int(self.entry_sil_index.get())

        # Kullanıcıya notun silinip silinmeyeceğini sormak için iletişim kutusu göster
        onay = messagebox.askyesno(title="Not Silme", message="Seçilen notu silmek istediğinizden emin misiniz?",
                                   icon='warning', default='no')
        if onay:
            self.ajanda.not_sil(tarih, not_index)
            self.entry_sil_index.delete(0, tk.END)
            self.notlari_goruntule()

    def ayarlar_ac(self):
        AyarlarPenceresi(self.pencere, self.cursor, self.baglanti)

    def eposta_gonder(self):
        tarih = self.tarih_secici.get_date()
        notlar = self.ajanda.getir_tum_notlar(tarih)
        eposta_adresi = self.cursor.execute("SELECT eposta FROM kullanici").fetchone()[0]

        if notlar:
            self.notlari_eposta_gonder(notlar, eposta_adresi)
        else:
            messagebox.showinfo("E-posta Gönderme", "Belirtilen tarihte herhangi bir not bulunamadı.")


    def notlari_eposta_gonder(self, notlar, eposta_adresi):
        tarih = self.tarih_secici.get_date()
        subject = f"Ajanda Notları - {tarih}"
        api_key = "mlsn.99270aea84ed98093d1ea7b23e036a6ef7c5e72d5fe419ad138c7a76878a2d39"
        mailer = emails.NewEmail(api_key)

        # Notların başına indeksleri ekleyerek yeni notlar listesini oluştur
        yeni_notlar = [f'<p>{indeks}: {not_metni}</p>' for indeks, not_metni in enumerate(notlar, start=0)]

        # E-posta içeriği
        body = "<br>".join(yeni_notlar)

        mail_body = {}

        # E-posta gönderme işlemi
        try:

            # E-posta oluşturma
            mail_from = {
                "name": "Ajanda Not Defteri",
                "email": "",
            }
            recipients = [
                {
                    "name": "Hocam",
                    "email": f"{eposta_adresi}",
                }
            ]

            reply_to = [
                {
                    "name": "Ajanda Not Defteri",
                    "email": "ajandanotdefteri@gmail.com",
                }
            ]

            mailer.set_mail_from(mail_from, mail_body)
            mailer.set_mail_to(recipients, mail_body)
            mailer.set_subject(f"{subject}", mail_body)
            mailer.set_html_content(f"{body}", mail_body)
            mailer.set_plaintext_content(f"{body}", mail_body)
            mailer.set_reply_to(reply_to, mail_body)

            mailer.send(mail_body)

            messagebox.showinfo("Başarılı",
                                f"Seçilen tarihin notları başarıyla {eposta_adresi} adresine gönderildi.")
        except Exception as e:
            messagebox.showerror("Hata", f"E-posta gönderme sırasında bir hata oluştu: {str(e)}")


class Ajanda:
    def __init__(self, cursor, baglanti):
        self.notlar = {}
        self.cursor = cursor
        self.baglanti = baglanti
        self.veritabanini_yukle()

    def veritabanini_yukle(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS notlar (tarih TEXT, not_metni TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS kullanici (id INTEGER PRIMARY KEY, sifre TEXT, eposta TEXT)")
        self.baglanti.commit()

        self.cursor.execute("SELECT tarih, not_metni FROM notlar")
        rows = self.cursor.fetchall()
        for row in rows:
            tarih, not_metni = row
            if tarih in self.notlar:
                self.notlar[tarih].append(not_metni)
            else:
                self.notlar[tarih] = [not_metni]

    def not_ekle(self, tarih, not_metni):
        if tarih in self.notlar:
            self.notlar[tarih].append(not_metni)
        else:
            self.notlar[tarih] = [not_metni]

        self.cursor.execute("INSERT INTO notlar (tarih, not_metni) VALUES (?, ?)", (tarih, not_metni))
        self.baglanti.commit()

    def not_sil(self, tarih, not_index):
        if tarih in self.notlar:
            if 0 <= not_index < len(self.notlar[tarih]):
                # Veritabanından notu sil
                not_id = self.cursor.execute("SELECT id FROM notlar WHERE tarih=? AND not_metni=?",
                                             (tarih, self.notlar[tarih][not_index])).fetchone()[0]
                self.cursor.execute("DELETE FROM notlar WHERE id=?", (not_id,))
                self.baglanti.commit()

                # Yerel listeden notu sil
                del self.notlar[tarih][not_index]
                print("Not başarıyla silindi.")
            else:
                print("Geçersiz not indeksi.")
        else:
            print("Belirtilen tarihte not bulunamadı.")

    def getir_tum_notlar(self, tarih):
        if tarih in self.notlar:
            return self.notlar[tarih]
        else:
            return None


# Kullanıcı bilgilerini içeren tablonun oluşturulması
def kullanici_tablosunu_olustur(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS kullanici (
                            id INTEGER PRIMARY KEY,
                            sifre TEXT,
                            eposta TEXT
                        )''')


# Kullanıcı bilgilerini tabloya ekleme
def kullanici_ekle(cursor, baglanti):
    cursor.execute("INSERT OR IGNORE INTO kullanici (id, sifre, eposta) VALUES (?, ?, ?)", (1, "12345", ""))
    baglanti.commit()


# Tkinter uygulamasını başlat
pencere = tk.Tk()
uygulama = AjandaUygulamasi(pencere)
kullanici_tablosunu_olustur(uygulama.cursor)
kullanici_ekle(uygulama.cursor, uygulama.baglanti)
pencere.mainloop()
