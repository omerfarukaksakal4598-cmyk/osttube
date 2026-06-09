import streamlit as st
import sqlite3
import re

# 1. SAYFA VE VERİTABANI AYARLARI
st.set_page_config(page_title="ÖstTube", page_icon="▶️", layout="wide")

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

# Session State (Hangi videonun izlendiğini hafızada tutmak için)
if "oynatilan_video" not in st.session_state:
    st.session_state.oynatilan_video = None

# 2. YARDIMCI FONKSİYON: YOUTUBE LİNKİNDEN ID VE KAPAK FOTOĞRAFI ÇEKME
def yt_id_bul(url):
    """YouTube linkinden video ID'sini ayıklar."""
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    elif "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]
    return None

def kapak_fotografi_al(video_id):
    """Video ID'sini kullanarak YouTube'un gizli yüksek kaliteli kapak resmini çeker."""
    if video_id:
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
    return "https://via.placeholder.com/480x360.png?text=Kapak+Bulunamadi"

# 3. ÖSTTUBE CSS TASARIMI (Koyu Tema + Kırmızı YouTube Vurguları)
st.markdown("""
    <style>
    .stApp { background-color: #0f0f0f; color: #f1f1f1; font-family: 'Roboto', sans-serif; }
    
    /* ÖstTube Logo Tasarımı */
    .tube-logo { font-size: 38px; font-weight: 900; letter-spacing: -1.5px; margin-bottom: 20px; }
    .tube-logo span { background-color: #ff0000; color: white; padding: 2px 10px; border-radius: 8px; margin-left: 2px; }
    
    /* Video Kartları */
    .video-card { background-color: #212121; border-radius: 12px; overflow: hidden; transition: 0.3s; margin-bottom: 20px; border: 1px solid #333; }
    .video-card:hover { transform: scale(1.02); box-shadow: 0 10px 20px rgba(255,0,0,0.15); border-color: #ff0000; }
    .video-thumb { width: 100%; height: 180px; object-fit: cover; }
    .video-info { padding: 12px; }
    .video-title { font-size: 15px; font-weight: bold; margin-bottom: 5px; color: white; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
    .video-category { font-size: 12px; color: #aaaaaa; background-color: #333; padding: 3px 8px; border-radius: 4px; display: inline-block; margin-bottom: 10px; }
    
    /* Oynatıcı Alanı (Sinema Modu) */
    .player-box { background-color: #000; padding: 20px; border-radius: 15px; border: 2px solid #ff0000; margin-bottom: 30px; box-shadow: 0 0 30px rgba(255,0,0,0.2); }
    .player-title { font-size: 24px; font-weight: bold; margin-bottom: 15px; color: white; }
    </style>
""", unsafe_allow_html=True)

# 4. YAN MENÜ (Sidebar) KONTROLLERİ
st.sidebar.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigasyon", ["🏠 Ana Sayfa (İzle)", "➕ Video Ekle", "🗑️ Arşiv Yönetimi"])
st.sidebar.write("---")

KATEGORİLER = ["Minecraft Mod & Harita", "Yazılım / Python", "Satranç Analizleri", "Müzik", "Eğlence", "Diğer"]

# ==========================================
# MENÜ 1: VİDEO EKLEME EKRANI
# ==========================================
if menu == "➕ Video Ekle":
    st.header("➕ Yeni Video Ekle")
    st.write("İzlemek istediğin veya arşivlemek istediğin YouTube linkini buraya yapıştır.")
    
    with st.form("video_ekle_form", clear_on_submit=True):
        y_baslik = st.text_input("Videonun Başlığı")
        y_kat = st.selectbox("Kategori Seç", KATEGORİLER)
        y_url = st.text_input("YouTube URL (Örn: https://www.youtube.com/watch?v=...)")
        
        if st.form_submit_button("Videoyu Kütüphaneye Ekle 📥"):
            if y_baslik and y_url:
                if "youtube.com" in y_url or "youtu.be" in y_url:
                    c.execute("INSERT INTO videolar (baslik, kategori, url) VALUES (?, ?, ?)", (y_baslik, y_kat, y_url))
                    conn.commit()
                    st.success("🎉 Video başarıyla eklendi! Ana Sayfadan izleyebilirsin.")
                else:
                    st.error("❌ Lütfen geçerli bir YouTube linki girin!")
            else:
                st.error("Lütfen başlık ve URL alanlarını boş bırakmayın.")

# ==========================================
# MENÜ 2: ANA SAYFA VE SİNEMA MODU OYNATICISI
# ==========================================
elif menu == "🏠 Ana Sayfa (İzle)":
    st.markdown("<div class='tube-logo'>Öst<span>Tube</span></div>", unsafe_allow_html=True)
    
    # EĞER BİR VİDEO SEÇİLDİYSE SİNEMA MODUNDA AÇ
    if st.session_state.oynatilan_video:
        video_verisi = st.session_state.oynatilan_video
        st.markdown(f"""
        <div class="player-box">
            <div class="player-title">📺 {video_verisi['baslik']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Streamlit'in kendi süper hızlı video oynatıcısı
        st.video(video_verisi['url'])
        
        if st.button("❌ Oynatıcıyı Kapat ve Ana Sayfaya Dön", type="primary"):
            st.session_state.oynatilan_video = None
            st.rerun()
        
        st.write("---")

    # VİDEO LİSTESİ (Izgara Görünümü)
    else:
        st.subheader("📚 Video Kütüphanesi")
        
        # Kategori Filtreleme
        secilen_filtre = st.selectbox("Kategori Filtresi", ["Tümü"] + KATEGORİLER)
        
        if secilen_filtre == "Tümü":
            c.execute("SELECT id, baslik, kategori, url FROM videolar ORDER BY id DESC")
        else:
            c.execute("SELECT id, baslik, kategori, url FROM videolar WHERE kategori=? ORDER BY id DESC", (secilen_filtre,))
            
        videolar = c.fetchall()
        
        if not videolar:
            st.info("Burası bomboş! Soldaki 'Video Ekle' menüsünden hemen yeni videolar eklemeye başla.")
        else:
            # Sütunları oluştur (Her satırda 4 video kartı)
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
                    
                    # İzle Butonu
                    if st.button(f"▶️ İzle", key=f"play_{v_id}", use_container_width=True):
                        st.session_state.oynatilan_video = {"id": v_id, "baslik": baslik, "url": url}
                        st.rerun()

# ==========================================
# MENÜ 3: ARŞİV YÖNETİMİ VE SİLME İŞLEMİ
# ==========================================
elif menu == "🗑️ Arşiv Yönetimi":
    st.header("⚙️ Video Yönetim Paneli")
    st.write("Kütüphaneden kaldırmak istediğiniz videoları buradan silebilirsiniz.")
    
    c.execute("SELECT id, baslik, kategori FROM videolar ORDER BY id DESC")
    tum_videolar = c.fetchall()
    
    if tum_videolar:
        silinecek = st.selectbox("Silmek istediğiniz videoyu seçin:", [f"[{v[2]}] {v[1]}" for v in tum_videolar])
        
        # Seçilen isme göre ID'yi bulma
        secili_id = None
        for v in tum_videolar:
            if f"[{v[2]}] {v[1]}" == silinecek:
                secili_id = v[0]
                break
                
        if st.button("🗑️ Videoyu Kalıcı Olarak Sil", type="primary"):
            c.execute("DELETE FROM videolar WHERE id=?", (secili_id,))
            conn.commit()
            st.success("Video arşivden silindi!")
            
            # Eğer silinen video şu an oynatılıyorsa oynatıcıyı sıfırla
            if st.session_state.oynatilan_video and st.session_state.oynatilan_video['id'] == secili_id:
                st.session_state.oynatilan_video = None
            st.rerun()
    else:
        st.info("Sistemde silinecek video bulunmuyor.")