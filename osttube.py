import streamlit as st
import sqlite3

# Veritabanı kurulumu
conn = sqlite3.connect("osttube_database.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS videolar (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, url TEXT)")
conn.commit()

st.set_page_config(page_title="ÖstTube - Sağlam Linkler", layout="wide")
st.title("📺 Çalışan Videolar Arşivi")

# Önemli: Yeni ve gerçekten aktif olan linkleri buraya güncellemen lazım!
# "Video kullanılamıyor" diyorsa o video zaten ölmüştür, onu listeden çıkarman gerekir.
BOT_VİDEOLARI = [
    ("TheMurat - Efsane Mod", "An-N7v6_6p8"), 
    ("Berkay İnan - Yeni Seri", "Yp8K4q8B23c")
]

if st.button("🔄 Güncel Listeyi Yükle"):
    for v in BOT_VİDEOLARI:
        c.execute("INSERT OR IGNORE INTO videolar (baslik, url) VALUES (?, ?)", (v[0], v[1]))
    conn.commit()
    st.success("Çalışan videolar yüklendi!")

# Listeleme
c.execute("SELECT id, baslik, url FROM videolar")
tum_videolar = c.fetchall()

if not tum_videolar:
    st.info("Henüz video yok, butona basarak yükle.")
else:
    for v in tum_videolar:
        v_id, baslik, v_url = v
        # Buradaki linki doğrudan YouTube'da açıyoruz. Eğer burada da hata veriyorsa o video gerçekten ölüdür.
        st.markdown(f"**{baslik}**")
        st.link_button("▶️ YouTube'da İzle", f"https://www.youtube.com/watch?v={v_url}")
        
        if st.button(f"🗑️ Sil ({baslik})", key=f"del_{v_id}"):
            c.execute("DELETE FROM videolar WHERE id=?", (v_id,))
            conn.commit()
            st.rerun()
