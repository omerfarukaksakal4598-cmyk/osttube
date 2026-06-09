import streamlit as st
import sqlite3

# Veritabanı bağlantısı
conn = sqlite3.connect("osttube_database.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS videolar (id INTEGER PRIMARY KEY AUTOINCREMENT, baslik TEXT, url TEXT)")
conn.commit()

st.set_page_config(page_title="ÖstTube Arşiv", layout="wide")
st.title("ÖstTube Video Arşivi")

# Bot Yükleme
if st.button("🤖 Bot: Kanal Videolarını Yükle"):
    # Örnek linkler
    videolar = [("TheMurat - Araba Modu", "An-N7v6_6p8"), ("KayzerTurco - Modlu Survival", "L_LUpn-6yDM")]
    for v in videolar:
        c.execute("INSERT OR IGNORE INTO videolar (baslik, url) VALUES (?, ?)", (v[0], v[1]))
    conn.commit()
    st.success("Yüklendi!")

# Listeleme ve YouTube'a Yönlendirme
c.execute("SELECT * FROM videolar")
for v in c.fetchall():
    v_id, baslik, v_url = v
    # Oynatıcı yerine linke git butonu
    if st.button(f"📺 İZLE: {baslik}", key=f"btn_{v_id}"):
        st.markdown(f'<meta http-equiv="refresh" content="0; url=https://youtube.com/watch?v={v_url}">', unsafe_allow_html=True)

if st.button("🚨 Sıfırla"):
    c.execute("DELETE FROM videolar")
    conn.commit()
    st.rerun()
