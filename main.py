import flet as ft
import json

def main(page: ft.Page):
    page.title = "Cep Barmeni"
    page.theme_mode = "dark"
    
    # Varsayılan Kokteyller
    varsayilanlar = [
        {"isim": "Mojito", "malzeme": "Rom, Nane, Limon, Soda", "tarif": "Naneyi ez, karıştır."},
        {"isim": "Whiskey Sour", "malzeme": "Viski, Limon, Şeker", "tarif": "Çalkala ve süz."}
    ]

    # VERİ YÖNETİMİ (Android Client Storage)
    # Bu yöntem dosyalarla uğraşmadan veriyi telefonun hafızasına gömer.
    def verileri_yukle():
        veriler = page.client_storage.get("kokteyl_verisi")
        if veriler:
            return json.loads(veriler)
        return varsayilanlar

    def verileri_kaydet(liste):
        page.client_storage.set("kokteyl_verisi", json.dumps(liste))

    kokteyl_listesi = verileri_yukle()

    # --- ANA SAYFA ---
    def git_ana_sayfa():
        page.controls.clear()
        
        liste_kutusu = ft.Column(spacing=5, scroll="auto", expand=True)

        def listeyi_guncelle(aranan=""):
            liste_kutusu.controls.clear()
            kokteyl_listesi.sort(key=lambda x: x["isim"])
            for k in kokteyl_listesi:
                if aranan.lower() in k["isim"].lower():
                    liste_kutusu.controls.append(
                        ft.Card(
                            content=ft.ListTile(
                                leading=ft.Icon("local_bar", color="amber"),
                                title=ft.Text(k["isim"], weight="bold"),
                                on_click=lambda e, x=k: git_detay(x)
                            )
                        )
                    )
            page.update()

        header = ft.Container(
            content=ft.Column([
                ft.Text("Kokteyl Rehberi", size=28, weight="bold"),
                ft.TextField(label="Ara...", on_change=lambda e: listeyi_guncelle(e.control.value))
            ]),
            padding=20
        )

        page.add(
            header, 
            ft.Container(content=liste_kutusu, padding=10, expand=True)
        )
        page.floating_action_button = ft.FloatingActionButton(
            icon="add", bgcolor="green", on_click=lambda _: git_form()
        )
        listeyi_guncelle()

    # --- DETAY SAYFASI ---
    def git_detay(kokteyl):
        page.controls.clear()
        page.floating_action_button = None
        
        def sil(e):
            kokteyl_listesi.remove(kokteyl)
            verileri_kaydet(kokteyl_listesi)
            git_ana_sayfa()

        page.add(
            ft.AppBar(leading=ft.IconButton("arrow_back", on_click=lambda _: git_ana_sayfa()), title=ft.Text("Detay")),
            ft.Column([
                ft.Text(kokteyl["isim"], size=30, weight="bold", color="amber"),
                ft.Text("MALZEMELER:", color="blue"),
                ft.Text(kokteyl["malzeme"]),
                ft.Text("TARİF:", color="green"),
                ft.Text(kokteyl["tarif"]),
                ft.Row([
                    ft.ElevatedButton("Düzenle", on_click=lambda _: git_form(kokteyl)),
                    ft.ElevatedButton("Sil", color="red", on_click=sil)
                ])
            ], scroll="auto", padding=20)
        )
        page.update()

    # --- FORM SAYFASI ---
    def git_form(kokteyl=None):
        page.controls.clear()
        page.floating_action_button = None
        
        t_isim = ft.TextField(label="İsim", value=kokteyl["isim"] if kokteyl else "")
        t_malz = ft.TextField(label="Malzeme", value=kokteyl["malzeme"] if kokteyl else "", multiline=True)
        t_tar = ft.TextField(label="Tarif", value=kokteyl["tarif"] if kokteyl else "", multiline=True)

        def kaydet(e):
            if not t_isim.value: return
            yeni = {"isim": t_isim.value, "malzeme": t_malz.value, "tarif": t_tar.value}
            
            if kokteyl:
                idx = kokteyl_listesi.index(kokteyl)
                kokteyl_listesi[idx] = yeni
            else:
                kokteyl_listesi.append(yeni)
            
            verileri_kaydet(kokteyl_listesi)
            git_ana_sayfa()

        page.add(
            ft.AppBar(leading=ft.IconButton("close", on_click=lambda _: git_ana_sayfa()), title=ft.Text("Ekle/Düzenle")),
            ft.Column([t_isim, t_malz, t_tar, ft.ElevatedButton("Kaydet", on_click=kaydet)], padding=20)
        )
        page.update()

    git_ana_sayfa()

ft.app(target=main)
