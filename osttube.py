import streamlit as st
import sqlite3

# 1. SAYFA VE VERİTABANI AYARLARI
st.set_page_config(page_title="ÖstTube v4.0", page_icon="▶️", layout="wide")

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

# 2. YARDIMCI FONKSiyonLAR (LİNK TEMİZLEYİCİ)
def yt_id_bul(url):
    """Link ne olursa olsun içindeki saf video ID'sini söker alır."""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    elif "embed/" in url:
        return url.split("embed/")[-1].split("?")[0]
    return None

def kapak_fotografi_al(video_id):
    if video_id:
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
    .player-box { background-color: #000; padding: 20px; border-radius: 15px; border: 2px solid #ff0000; margin-bottom: 10px; box-shadow: 0 0 30px rgba(255,0,0,0.2); }
    .player-title { font-size: 22px; font-weight: bold; color: white; }
    </style>
""", unsafe_allow_html=True)

# 4. YAN MENÜ (Sidebar) KONTROLLERİ
st.sidebar.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
menu = st.sidebar.radio("Sistem Menüsü", ["🏠 Ana Sayfa (İzle)", "🤖 ÖstBot (Mega Bot)", "➕ Tekli Video Ekle", "🗑️ Arşiv Yönetimi"])
st.sidebar.write("---")

KATEGORİLER = ["Minecraft Mod & Harita", "Yazılım / Python", "Satranç Analizleri", "Bilim & Teknoloji", "Eğlence"]

# ==========================================
# SAF VİDEO ID'LERİ İLE DEV BOT HAVUZU
# ==========================================
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
        {"baslik": "Sabo - Satrançta Asla Yapmaman Gereken 5 Hata", "kategori": "Satranç Analizleri", "id": "F5d2yv_r6kE"},
        {"baslik": "Sabo - Taktik Çözmenin Sırları", "kategori": "Satranç Analizleri", "id": "8mG_7gE_xXo"}
    ],
    "Barış Özcan": [
        {"baslik": "Barış Özcan - Yapay Zeka Bizi Nasıl Değiştirecek?", "kategori": "Bilim & Teknoloji", "id": "zHnK516nI2I"},
        {"baslik": "Barış Özcan - Geleceğin En İyi Meslekleri", "kategori": "Bilim & Teknoloji", "id": "GjY_n3qZ6q4"}
    ]
}

# ==========================================
# MENÜ: 🤖 ÖSTBOT (MEGA BOT)
# ==========================================
if menu == "🤖 ÖstBot (Mega Bot)":
    st.header("🤖 ÖstBot v4.0 - Güvenli Video Yükleyici")
    st.write("Kanalları yüklemeden önce eski bozuk videoları temizlemek için 'Arşiv Yönetimi'nden sistemi sıfırlamanız önerilir.")
    
    kanallar = list(BOT_VİDEOLARI.keys())
    cols = st.columns(3)
    
    for index, kanal in enumerate(kanallar):
        with cols[index % 3]:
            st.subheader(f"🎬 {kanal}")
            if st.button(f"Videoları Yükle", key=f"btn_{kanal}", use_container_width=True):
                eklenen = 0
                for vid in BOT_VİDEOLARI[kanal]:
                    temiz_url = f"https://youtu.be/{vid['id']}"
                    c.execute("SELECT id FROM videolar WHERE url=?", (temiz_url,))
                    if not c.fetchone():
                        c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (vid["baslik"], vid["kategori"], temiz_url))
                        eklenen += 1
                conn.commit()
                st.success(f"⚡ {eklenen} video eklendi!")

    st.write("---")
    if st.button("🔥 TÜM KANALLARI AYNI ANDA SENKRONİZE ET", type="primary", use_container_width=True):
        toplam_eklenen = 0
        for kanal, v_listesi in BOT_VİDEOLARI.items():
            for vid in v_listesi:
                temiz_url = f"https://youtu.be/{vid['id']}"
                c.execute("SELECT id FROM videolar WHERE url=?", (temiz_url,))
                if not c.fetchone():
                    c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (vid["baslik"], vid["kategori"], temiz_url))
                    toplam_eklenen += 1
        conn.commit()
        st.success(f"🚀 Toplam {toplam_eklenen} video kusursuz formatta ana sayfaya eklendi.")

# ==========================================
# MENÜ: 🏠 ANA SAYFA (İZLE)
# ==========================================
elif menu == "🏠 Ana Sayfa (İzle)":
    st.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
    
    if st.session_state.oynatilan_video:
        video_verisi = st.session_state.oynatilan_video
        st.markdown(f'<div class="player-box"><div class="player-title">📺 {video_verisi["baslik"]}</div></div>', unsafe_allow_html=True)
        
        # Kesin çözüm temiz oynatıcı linki
        st.video(video_verisi['url'])
        
        if st.button("❌ Oynatıcıyı Kapat ve Listeye Dön", type="primary"):
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
# MENÜ: MANUEL EKLEME
# ==========================================
elif menu == "➕ Tekli Video Ekle":
    st.header("➕ Manuel Video Ekle")
    with st.form("manuel_form", clear_on_submit=True):
        y_baslik = st.text_input("Videonun Başlığı")
        y_kat = st.selectbox("Kategori Seç", KATEGORİLER)
        y_url = st.text_input("YouTube URL")
        if st.form_submit_button("Ekle"):
            v_id = yt_id_bul(y_url)
            if y_baslik and v_id:
                temiz_url = f"https://youtu.be/{v_id}"
                c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (y_baslik, y_kat, temiz_url))
                conn.commit()
                st.success("Başarıyla eklendi!")
            else:
                st.error("Geçersiz YouTube linki!")

# ==========================================
# MENÜ: ARŞİV YÖNETİMİ (SIFIRLAMA)
# ==========================================
elif menu == "🗑️ Arşiv Yönetimi":
    st.header("⚙️ Video Yönetim Paneli")
    
    # Eski bozuk linkli verileri silmek için bu buton çok önemli
    if st.button("🚨 TÜM ESKİ VİDEOLARI TEMİZLE VE VERİTABANINI SIFIRLA", type="primary", use_container_width=True):
        c.execute("DELETE FROM videolar")
        conn.commit()
        st.session_state.oynatilan_video = None
        st.success("Tüm kütüphane başarıyla sıfırlandı! Artık yeni botu güvenle yükleyebilirsin.")
        st.rerun()
        
    st.write("---")
    c.execute("SELECT id, baslik, kategori FROM videolar ORDER BY id DESC")
    tum_videolar = c.fetchall()
    if tum_videolar:
        silinecek = st.selectbox("Tek bir videoyu silin:", [f"[{v[2]}] {v[1]}" for v in tum_videolar])
        secili_id = next(v[0] for v in tum_videolar if f"[{v[2]}] {v[1]}" == silinecek)
        if st.button("🗑️ Seçileni Kalıcı Olarak Sil"):
            c.execute("DELETE FROM videolar WHERE id=?", (secili_id,))
            conn.commit()
            st.success("Silindi!")
            st.rerun()
