import flet as ft
import json
import os

def main(page: ft.Page):
    # --- AYARLAR ---
    page.title = "Cep Barmeni"
    page.theme_mode = "dark" 
    page.padding = 0 
    
    # DİKKAT: window_prevent_close gibi PC kodlarını sildik.
    # Android'de bunlar hataya sebep olur.

    # --- DOSYA YOLU AYARI ---
    # Android'de güvenli kayıt yeri bulmaya çalışır, bulamazsa geçici hafızayı kullanır.
    def dosya_yolu_getir():
        try:
            data_dir = os.getenv('FLET_APP_STORAGE_DATA_DIR')
            if data_dir:
                return os.path.join(data_dir, 'kokteyller.json')
            else:
                return 'kokteyller.json'
        except:
            return 'kokteyller.json'

    DOSYA_ADI = dosya_yolu_getir()

    VARSAYILANLAR = [
        {"isim": "Mojito", "malzeme": "Rom, Nane, Limon, Soda", "tarif": "Naneyi ez, karıştır."},
        {"isim": "Whiskey Sour", "malzeme": "Viski, Limon, Şeker", "tarif": "Çalkala ve süz."}
    ]

    # --- VERİ İŞLEMLERİ ---
    def verileri_cek():
        # Dosya yoksa veya bozuksa varsayılanları getir (Çökme koruması)
        if os.path.exists(DOSYA_ADI):
            try:
                with open(DOSYA_ADI, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return VARSAYILANLAR.copy()
        return VARSAYILANLAR.copy()

    def verileri_yaz(liste):
        try:
            with open(DOSYA_ADI, "w", encoding="utf-8") as f:
                json.dump(liste, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Kayıt hatası: {e}") # Hatayı gizli tut, ekrana yansıtma

    # Uygulama hafızasındaki liste
    kokteyl_listesi = verileri_cek()

    # ================= SAYFALAR =================

    # 1. ANA SAYFA (LİSTE)
    def git_ana_sayfa():
        page.clean()
        
        # Scroll 'auto' diyerek taşmaları engelliyoruz
        liste_kutusu = ft.Column(spacing=5, scroll="auto", expand=True)

        def listeyi_guncelle(aranan_metin=""):
            liste_kutusu.controls.clear()
            aranan = aranan_metin.lower()
            kokteyl_listesi.sort(key=lambda x: x["isim"])
            
            for k in kokteyl_listesi:
                if aranan in k["isim"].lower():
                    liste_kutusu.controls.append(
                        ft.Card(
                            content=ft.ListTile(
                                leading=ft.Icon("local_bar", color="amber"),
                                title=ft.Text(k["isim"], weight="bold"),
                                subtitle=ft.Text(k["malzeme"][:25]+"..."),
                                on_click=lambda e, x=k: git_detay_sayfasi(x)
                            )
                        )
                    )
            page.update()

        def arama_tetiklendi(e):
            listeyi_guncelle(e.control.value)
        
        header = ft.Container(
            content=ft.Column([
                ft.Text("Kokteyl Rehberi", size=28, weight="bold", color="white"),
                ft.TextField(label="Ara...", prefix_icon="search", on_change=arama_tetiklendi, border_radius=15)
            ]),
            padding=20,
            bgcolor="#263238"
        )

        fab = ft.FloatingActionButton(
            icon="add", bgcolor="green", 
            on_click=lambda _: git_form_sayfasi(None)
        )

        page.add(header, ft.Container(content=liste_kutusu, padding=10, expand=True))
        page.floating_action_button = fab
        listeyi_guncelle("") 

    # 2. DETAY SAYFASI
    def git_detay_sayfasi(kokteyl):
        page.clean()
        page.floating_action_button = None
        
        def sil_ve_don(e):
            if kokteyl in kokteyl_listesi:
                kokteyl_listesi.remove(kokteyl)
                verileri_yaz(kokteyl_listesi)
            git_ana_sayfa()
            page.snack_bar = ft.SnackBar(ft.Text("Silindi!"))
            page.snack_bar.open = True
            page.update()

        icerik = ft.Column([
            ft.Container(height=20),
            ft.Text(kokteyl["isim"], size=32, weight="bold", color="amber"),
            ft.Divider(),
            ft.Text("MALZEMELER", size=14, color="grey"),
            ft.Text(kokteyl["malzeme"], size=18),
            ft.Container(height=20),
            ft.Text("HAZIRLANIŞI", size=14, color="grey"),
            ft.Text(kokteyl["tarif"], size=18),
            ft.Divider(),
            ft.Row([
                ft.ElevatedButton("Düzenle", icon="edit", on_click=lambda _: git_form_sayfasi(kokteyl)),
                ft.ElevatedButton("Sil", icon="delete", color="red", on_click=sil_ve_don),
            ], alignment="center")
        ], scroll="auto")

        app_bar = ft.AppBar(
            leading=ft.IconButton(icon="arrow_back", on_click=lambda _: git_ana_sayfa()),
            title=ft.Text("Detaylar"),
            bgcolor="#263238"
        )

        page.add(app_bar, ft.Container(content=icerik, padding=20, expand=True))

    # 3. FORM SAYFASI
    def git_form_sayfasi(duzenlenecek_veri=None):
        page.clean()
        page.floating_action_button = None

        baslik = "Kokteyl Düzenle" if duzenlenecek_veri else "Yeni Kokteyl Ekle"
        
        t_isim = ft.TextField(label="İsim", value=duzenlenecek_veri["isim"] if duzenlenecek_veri else "")
        t_malzeme = ft.TextField(label="Malzemeler", multiline=True, value=duzenlenecek_veri["malzeme"] if duzenlenecek_veri else "")
        t_tarif = ft.TextField(label="Tarif", multiline=True, value=duzenlenecek_veri["tarif"] if duzenlenecek_veri else "")

        def kaydet(e):
            if not t_isim.value: return
            
            yeni_veri = {
                "isim": t_isim.value,
                "malzeme": t_malzeme.value,
                "tarif": t_tarif.value
            }

            if duzenlenecek_veri:
                if duzenlenecek_veri in kokteyl_listesi:
                    idx = kokteyl_listesi.index(duzenlenecek_veri)
                    kokteyl_listesi[idx] = yeni_veri
                else:
                    kokteyl_listesi.append(yeni_veri)
            else:
                kokteyl_listesi.append(yeni_veri)
            
            verileri_yaz(kokteyl_listesi)
            git_ana_sayfa()
            page.snack_bar = ft.SnackBar(ft.Text("Kaydedildi"))
            page.snack_bar.open = True
            page.update()

        form_icerik = ft.Column([
            t_isim, t_malzeme, t_tarif,
            ft.Container(height=20),
            ft.ElevatedButton("KAYDET", icon="save", bgcolor="green", color="white", width=200, on_click=kaydet)
        ], horizontal_alignment="center", scroll="auto") # Form uzun olursa kaydırılabilsin

        app_bar = ft.AppBar(
            leading=ft.IconButton(icon="close", on_click=lambda _: git_ana_sayfa()),
            title=ft.Text(baslik),
            bgcolor="#263238"
        )

        page.add(app_bar, ft.Container(content=form_icerik, padding=20, expand=True))

    git_ana_sayfa()

ft.app(target=main)
