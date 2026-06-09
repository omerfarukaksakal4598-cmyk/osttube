import streamlit as st
import sqlite3

# 1. AYARLAR
st.set_page_config(page_title="ÖstTube v6.0 - Final", page_icon="▶️", layout="wide")

conn = sqlite3.connect("osttube_database.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS videolar (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, kategori TEXT, url TEXT)")
conn.commit()

if "oynatilan_video" not in st.session_state:
    st.session_state.oynatilan_video = None

# 2. YARDIMCI FONKSİYONLAR
def yt_id_bul(url):
    if "youtu.be" in url: return url.split("/")[-1].split("?")[0]
    if "watch?v=" in url: return url.split("watch?v=")[1].split("&")[0]
    return url

# 3. TASARIM (CSS)
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: #f1f1f1; }
    .tube-logo { font-size: 40px; font-weight: 900; }
    .tube-logo span { background-color: #ff0000; padding: 0 10px; border-radius: 8px; }
    .v-card { background: #1e1e1e; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# 4. BOT VERİSİ
BOT_VİDEOLARI = {
    "TheMurat": [{"baslik": "GERÇEK ARABA MODU", "id": "An-N7v6_6p8"}, {"baslik": "Güvenli Hapishane", "id": "385Oa38hDsc"}],
    "KayzerTurco": [{"baslik": "Modlu Survival", "id": "L_LUpn-6yDM"}, {"baslik": "Savunma Kuleleri", "id": "vVka6N7k_Vw"}],
    "Berkay İnan": [{"baslik": "Her Şey Şans", "id": "kX3D0_Y3p2I"}, {"baslik": "100 Gün Hardcore", "id": "Yp8K4q8B23c"}]
}

# 5. MENÜLER
menu = st.sidebar.radio("Menü", ["🏠 Ana Sayfa", "🤖 Bot", "⚙️ Yönetim"])

if menu == "🤖 Bot":
    st.header("🤖 ÖstBot Mega Yükleyici")
    for kanal, videolar in BOT_VİDEOLARI.items():
        if st.button(f"{kanal} videolarını yükle"):
            for v in videolar:
                c.execute("INSERT OR IGNORE INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (v['baslik'], kanal, v['id']))
            conn.commit()
            st.success(f"{kanal} yüklendi!")

elif menu == "🏠 Ana Sayfa":
    st.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
    c.execute("SELECT * FROM videolar")
    for v in c.fetchall():
        v_id, baslik, kat, v_url = v
        with st.container():
            col1, col2 = st.columns([1, 3])
            col1.image(f"https://img.youtube.com/vi/{v_url}/hqdefault.jpg")
            col2.subheader(baslik)
            if col2.button("▶️ İZLE", key=f"btn_{v_id}"):
                st.session_state.oynatilan_video = v
                st.rerun()

    if st.session_state.oynatilan_video:
        v_id, baslik, kat, v_url = st.session_state.oynatilan_video
        st.write("---")
        st.subheader(f"Şu an izleniyor: {baslik}")
        # Hata korumalı oynatıcı:
        st.video(f"https://www.youtube.com/watch?v={v_url}")
        st.link_button("Eğer video açılmazsa YOUTUBE'DA AÇ", f"https://www.youtube.com/watch?v={v_url}")
        if st.button("KAPAT"):
            st.session_state.oynatilan_video = None
            st.rerun()

elif menu == "⚙️ Yönetim":
    if st.button("🚨 TÜMÜNÜ SİL"):
        c.execute("DELETE FROM videolar")
        conn.commit()
        st.rerun()
