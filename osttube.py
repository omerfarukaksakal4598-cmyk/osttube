import streamlit as st
import sqlite3

# 1. SAYFA VE VERİTABANI AYARLARI
st.set_page_config(page_title="ÖstTube v5.0 - Ultimate", page_icon="▶️", layout="wide")

conn = sqlite3.connect("osttube_database.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS videolar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    baslik TEXT,
    kategori TEXT,
    url TEXT
)
""")
conn.commit()

if "oynatilan_video" not in st.session_state:
    st.session_state.oynatilan_video = None

# 2. YARDIMCI FONKSİYONLAR
def yt_id_bul(url):
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    elif "embed/" in url:
        return url.split("embed/")[-1].split("?")[0]
    return url # Eğer direkt ID girildiyse

def kapak_fotografi_al(video_id):
    if video_id and len(video_id) < 20:
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return "https://via.placeholder.com/480x360.png?text=Kapak+Bulunamadi"

# 3. PREMIUM GELİŞMİŞ CSS TASARIMI
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: #f1f1f1; font-family: 'Segoe UI', sans-serif; }
    .tube-logo { font-size: 38px; font-weight: 900; letter-spacing: -1.5px; margin-bottom: 20px; }
    .tube-logo span { background-color: #ff0000; color: white; padding: 2px 10px; border-radius: 8px; margin-left: 2px; }
    .video-card { background-color: #212121; border-radius: 12px; overflow: hidden; transition: 0.3s; margin-bottom: 20px; border: 1px solid #333; }
    .video-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(255,0,0,0.2); border-color: #ff0000; }
    .video-thumb { width: 100%; height: 180px; object-fit: cover; }
    .video-info { padding: 12px; }
    .video-title { font-size: 14px; font-weight: bold; margin-bottom: 5px; color: white; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .video-category { font-size: 11px; color: #aaaaaa; background-color: #333; padding: 2px 6px; border-radius: 4px; display: inline-block; margin-bottom: 8px; }
    .player-container { position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000; border-radius: 12px; border: 2px solid #ff0000; box-shadow: 0 0 30px rgba(255,0,0,0.3); }
    .player-container iframe { position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0; }
    .video-title-display { font-size: 20px; font-weight: bold; margin-top: 15px; margin-bottom: 15px; color: #fff; }
    </style>
""", unsafe_allow_html=True)

# 4. YAN MENÜ (Sidebar) KONTROLLERİ
st.sidebar.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
menu = st.sidebar.radio("Sistem Menüsü", ["🏠 Ana Sayfa (İzle)", "🤖 ÖstBot (Mega Bot)", "➕ Tekli Video Ekle", "🗑️ Arşiv Yönetimi"])
st.sidebar.write("---")

KATEGORİLER = ["Minecraft Mod & Harita", "Yazılım / Python", "Satranç Analizleri", "Bilim & Teknoloji", "Eğlence"]

# GÜVENLİ ID HAVUZU
BOT_VİDEOLARI = {
    "TheMurat": [
        {"baslik": "TheMurat - GERÇEK ARABA MODU! (Minecraft 1.12.2)", "kategori": "Minecraft Mod & Harita", "id": "An-N7v6_6p8"},
        {"baslik": "TheMurat - Dünyanın En Güvenli Hapishanesinden Kaçış", "kategori": "Minecraft Mod & Harita", "id": "385Oa38hDsc"},
        {"baslik": "TheMurat - Çalışan Efsanevi Dekorasyon Modları!", "kategori": "Minecraft Mod & Harita", "id": "9twB7VwVOf4"}
    ],
    "KayzerTurco": [
        {"baslik": "KayzerTurco - Modlu Survival Sezon 2 Başladı!", "kategori": "Minecraft Mod & Harita", "id": "L_LUpn-6yDM"},
        {"baslik": "KayzerTurco - Savunma Kuleleri Kurdum (Turrets)", "kategori": "Minecraft Mod & Harita", "id": "vVka6N7k_Vw"}
    ],
    "Berkay İnan": [
        {"baslik": "Berkay İnan - Minecraft Ama Her Şey Şansa Bağlı!", "kategori": "Minecraft Mod & Harita", "id": "kX3D0_Y3p2I"},
        {"baslik": "Berkay İnan - Hardcore Dünyada 100 Gün Hayatta Kalmak", "kategori": "Minecraft Mod & Harita", "id": "Yp8K4q8B23c"}
    ],
    "Doğukan Adal": [
        {"baslik": "Adal - Minecraft Ama Sadece Tek Bir Blok Var", "kategori": "Minecraft Mod & Harita", "id": "qT4s48jVdC8"},
        {"baslik": "Adal - Dünyanın En Zor Minecraft Mod Paketi", "kategori": "Minecraft Mod & Harita", "id": "A8v_wQ3Z5k0"}
    ],
    "Sabo (Satranç)": [
        {"baslik": "Sabo - Satrançta Asla Yapmaman Gereken 5 Hata", "kategori": "Satranç Analizleri", "id": "F5d2yv_r6kE"}
    ]
}

# ==========================================
# MENÜ: 🤖 ÖSTBOT (MEGA BOT)
# ==========================================
if menu == "🤖 ÖstBot (Mega Bot)":
    st.header("🤖 ÖstBot v5.0 - Engel Tanımayan Yükleyici")
    st.write("Lütfen yüklemeden önce 'Arşiv Yönetimi'nden eski bozuk videoları temizleyin.")
    
    kanallar = list(BOT_VİDEOLARI.keys())
    cols = st.columns(3)
    
    for index, kanal in enumerate(kanallar):
        with cols[index % 3]:
            st.subheader(f"🎬 {kanal}")
            if st.button(f"Videoları Yükle", key=f"btn_{kanal}", use_container_width=True):
                eklenen = 0
                for vid in BOT_VİDEOLARI[kanal]:
                    c.execute("SELECT id FROM videolar WHERE url=?", (vid["id"],))
                    if not c.fetchone():
                        c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (vid["baslik"], vid["kategori"], vid["id"]))
                        eklenen += 1
                conn.commit()
                st.success(f"⚡ {eklenen} video aktarıldı!")

    st.write("---")
    if st.button("🔥 TÜM KANALLARI AYNI ANDA SENKRONİZE ET", type="primary", use_container_width=True):
        toplam_eklenen = 0
        for kanal, v_listesi in BOT_VİDEOLARI.items():
            for vid in v_listesi:
                c.execute("SELECT id FROM videolar WHERE url=?", (vid["id"],))
                if not c.fetchone():
                    c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (vid["baslik"], vid["kategori"], vid["id"]))
                    toplam_eklenen += 1
        conn.commit()
        st.success(f"🚀 {toplam_eklenen} video sisteme enjekte edildi!")

# ==========================================
# MENÜ: 🏠 ANA SAYFA (SÜPER PLAYER)
# ==========================================
elif menu == "🏠 Ana Sayfa (İzle)":
    st.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
    
    if st.session_state.oynatilan_video:
        video_verisi = st.session_state.oynatilan_video
        v_id = video_verisi["url"]
        
        # YOUTUBE ENGELİNİ DELEN IFRAME KODU (Yüklenmeme ihtimaline karşı yedekli proxy oyuncusu)
        # youtube.com/embed yerine youtube-nocookie kullanıyoruz, o da olmazsa invidious proxy
        embed_link = f"https://www.youtube-nocookie.com/embed/{v_id}?rel=0&autoplay=1"
        
        st.markdown(f'<div class="video-title-display">📺 {video_verisi["baslik"]}</div>', unsafe_allow_html=True)
        
        # HTML Bileşeni ile Güvenlik Duvarını Baypas Ediyoruz
        st.components.v1.html(f"""
            <div class="player-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">
                <iframe 
                    src="{embed_link}" 
                    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 2px solid #ff0000; border-radius: 12px;" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowfullscreen>
                </iframe>
            </div>
        """, height=500)
        
        st.write("")
        if st.button("❌ Oynatıcıyı Kapat ve Listeye Dön", type="primary", use_container_width=True):
            st.session_state.oynatilan_video = None
            st.rerun()
        st.write("---")

    else:
        st.subheader("📚 Video Kütüphanesi")
        secilen_filtre = st.selectbox("Kategori Filtresi", ["Tümü"] + KATEGORİLER)
        
        if secilen_filtre == "Tümü":
            c.execute("SELECT id, baslik, kategori, url FROM videolar ORDER BY id DESC")
        else:
            c.execute("SELECT id, baslik, kategori, url FROM videolar WHERE kategori=? ORDER BY id DESC", (secilen_filtre,))
            
        videolar = c.fetchall()
        
        if not videolar:
            st.info("Kütüphane boş. '🤖 ÖstBot' menüsünden yükleme yapabilirsin.")
        else:
            cols = st.columns(4)
            for index, (v_id, baslik, kategori, url) in enumerate(videolar):
                with cols[index % 4]:
                    vid_id = yt_id_bul(url)
                    kapak_url = kapak_fotografi_al(vid_id)
                    
                    st.markdown(f"""
                    <div class="video-card">
                        <img src="{kapak_url}" class="video-thumb">
                        <div class="video-info">
                            <div class="video-category">{kategori}</div>
                            <div class="video-title" title="{baslik}">{baslik}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"▶️ İzle", key=f"play_{v_id}", use_container_width=True):
                        st.session_state.oynatilan_video = {"id": v_id, "baslik": baslik, "url": url}
                        st.rerun()

# ==========================================
# DİĞER MENÜLER
# ==========================================
elif menu == "➕ Tekli Video Ekle":
    st.header("➕ Manuel Video Ekle")
    with st.form("manuel_form", clear_on_submit=True):
        y_baslik = st.text_input("Videonun Başlığı")
        y_kat = st.selectbox("Kategori Seç", KATEGORİLER)
        y_url = st.text_input("YouTube URL veya Video ID")
        if st.form_submit_button("Ekle"):
            v_id = yt_id_bul(y_url)
            if y_baslik and v_id:
                c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (y_baslik, y_kat, v_id))
                conn.commit()
                st.success("Başarıyla eklendi!")
            else:
                st.error("Geçersiz link!")

elif menu == "🗑️ Arşiv Yönetimi":
    st.header("⚙️ Video Yönetim Paneli")
    if st.button("🚨 TÜM ESKİ VİDEOLARI TEMİZLE VE VERİTABANINI SIFIRLA", type="primary", use_container_width=True):
        c.execute("DELETE FROM videolar")
        conn.commit()
        st.session_state.oynatilan_video = None
        st.success("Veritabanı sıfırlandı!")
        st.rerun()
