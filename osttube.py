import streamlit as st
import sqlite3
import os

# 1. VERİTABANI GÜVENLİK SIFIRLAMASI
# Eğer veritabanı sütun hatası verirse, dosyayı silip yeniden başlatır
db_file = "osttube_database.db"
try:
    conn = sqlite3.connect(db_file, check_same_thread=False)
    c = conn.cursor()
    # Eğer tablo 3 sütundan azsa eski olduğunu anlar ve sıfırlar
    c.execute("PRAGMA table_info(videolar)")
    columns = c.fetchall()
    if len(columns) != 3: 
        conn.close()
        os.remove(db_file)
        conn = sqlite3.connect(db_file, check_same_thread=False)
        c = conn.cursor()
except:
    pass

c.execute("CREATE TABLE IF NOT EXISTS videolar (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, url TEXT)")
conn.commit()

# 2. ARAYÜZ
st.set_page_config(page_title="ÖstTube v6.1", layout="wide")
st.title("📺 ÖstTube - Sorunsuz Arşiv")

# BOT
if st.button("🤖 Bot: Kanal Videolarını Yükle"):
    videolar = [("TheMurat - Araba Modu", "An-N7v6_6p8"), ("KayzerTurco - Modlu Survival", "L_LUpn-6yDM")]
    for v in videolar:
        c.execute("INSERT OR IGNORE INTO videolar (baslik, url) VALUES (?, ?)", (v[0], v[1]))
    conn.commit()
    st.rerun()

# LİSTELEME
c.execute("SELECT id, baslik, url FROM videolar")
for v in c.fetchall():
    v_id, baslik, v_url = v
    # Videoyu sitemizde oynatmıyoruz, YouTube'a gönderiyoruz (En kesin çözüm!)
    st.markdown(f"### {baslik}")
    if st.button(f"▶️ YOUTUBE'DA İZLE", key=f"btn_{v_id}"):
        st.link_button("Videoya Git", f"https://youtube.com/watch?v={v_url}")

# SIFIRLAMA
if st.button("🚨 Veritabanını Temizle"):
    c.execute("DELETE FROM videolar")
    conn.commit()
    st.rerun()
