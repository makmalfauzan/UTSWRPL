import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime

# --- Load data ---
@st.cache_data
def load_events():
    return pd.read_csv('data/events.csv')

@st.cache_data
def load_orders():
    try:
        return pd.read_csv('data/orders.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['order_id','user_name','event_id','quantity','total_price','status','timestamp'])
        df.to_csv('data/orders.csv', index=False)
        return df

events_df = load_events()
orders_df = load_orders()

# --- Sidebar Menu ---
st.sidebar.image('assets/logo.png', use_column_width=True)
menu = st.sidebar.radio("Menu", ["Home","Search Event","Order Tiket","My Orders"])

st.title("Eventura – Hybrid Event Platform")

# --- Home ---
if menu == "Home":
    st.markdown("## Selamat datang di Eventura!")
    st.write("Pilih menu di sidebar untuk mulai.")

# --- Search Event ---
elif menu == "Search Event":
    st.header("🔍 Search Event")
    keyword = st.text_input("Masukkan kata kunci (title / category)")
    if keyword:
        results = events_df[
            events_df['title'].str.contains(keyword, case=False, na=False) |
            events_df['category'].str.contains(keyword, case=False, na=False)
        ]
    else:
        results = events_df
    st.write(f"### Ditemukan {len(results)} event")
    for _, row in results.iterrows():
        st.subheader(row['title'])
        st.write(f"- Kategori: {row['category']}")
        st.write(f"- Waktu: {row['datetime']}")
        st.write(f"- Lokasi: {row['location']} ({row['mode']})")
        st.write(f"- Harga: Rp{row['price']:.0f}")
        st.markdown("---")

# --- Order Tiket ---
elif menu == "Order Tiket":
    st.header("🎫 Order Tiket")
    user_name = st.text_input("Nama Anda")
    event_id = st.selectbox("Pilih Event", events_df['event_id'])
    qty = st.number_input("Jumlah Tiket", min_value=1, max_value=10, value=1)
    if st.button("Pesan & Bayar"):
        ev = events_df[events_df['event_id']==event_id].iloc[0]
        total = qty * ev['price']
        new_id = orders_df['order_id'].max() + 1 if not orders_df.empty else 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        orders_df.loc[len(orders_df)] = [new_id, user_name, event_id, qty, total, 'paid', timestamp]
        orders_df.to_csv('data/orders.csv', index=False)
        st.success(f"Order #{new_id} sukses! Total bayar Rp{total:.0f}")
        # Generate QR
        qr = qrcode.make(f"ORDER:{new_id}|USER:{user_name}|EVENT:{event_id}")
        buf = BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf)

# --- My Orders / Konfirmasi ---
elif menu == "My Orders":
    st.header("📂 My Orders")
    name = st.text_input("Masukkan Nama Anda untuk lihat order")
    if name:
        my = orders_df[orders_df['user_name']==name]
        if my.empty:
            st.warning("Belum ada order untuk nama ini.")
        else:
            st.table(my)
