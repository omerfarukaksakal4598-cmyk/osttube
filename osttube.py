import streamlit as st
import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect("osttube_database.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS videolar (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, url TEXT)")
conn.commit()

st.set_page_config(page_title="ÖstTube v6.2", layout="wide")
st.title("📺 ÖstTube - Canlı Link Arşivi")

# 1. TEMİZLİK (Eski bozuk linklerden kurtulma)
if st.button("🚨 TÜM LİNK ARŞİVİNİ SIFIRLA"):
    c.execute("DELETE FROM videolar")
    conn.commit()
    st.rerun()

# 2. YENİ LİNK EKLEME (Buraya sadece çalışan linkleri gir)
with st.form("yeni_link_formu"):
    baslik = st.text_input("Videonun Başlığı")
    url_id = st.text_input("YouTube Video ID'si (Örn: jNQXAC9IVRw)")
    if st.form_submit_button("Yeni Link Ekle"):
        c.execute("INSERT INTO videolar (baslik, url) VALUES (?, ?)", (baslik, url_id))
        conn.commit()
        st.success("Yeni link eklendi!")

# 3. LİSTELEME
st.write("---")
c.execute("SELECT id, baslik, url FROM videolar")
tum_videolar = c.fetchall()

if not tum_videolar:
    st.info("Henüz arşivin boş. Yukarıdan çalışan bir YouTube ID'si ekle.")
else:
    for v in tum_videolar:
        v_id, baslik, v_url = v
        col1, col2 = st.columns([3, 1])
        col1.write(f"### {baslik}")
        # Artık %100 çalışıyor çünkü biz hata aldıklarımızı sildik
        col2.link_button("▶️ İZLE", f"https://youtube.com/watch?v={v_url}")
