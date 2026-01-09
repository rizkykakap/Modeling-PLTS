import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Solar System Pro V6.7",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. FUNGSI BACKGROUND ---
def set_background(image_filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, image_filename)

    if os.path.isfile(image_path):
        with open(image_path, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        style = f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url(data:image/jpeg;base64,{b64_encoded});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)

# PANGGIL BACKGROUND (Pastikan file ada)
set_background('1006752.png')

# --- 3. CSS CUSTOM (MODULAR CARDS & WIDGET STYLING) ---
st.markdown("""
<style>
    /* RESET CONTAINER UTAMA AGAR TRANSPARAN */
    .block-container {
        background-color: transparent !important;
        box-shadow: none !important;
        padding-top: 1rem;
        max-width: 1200px;
        margin: auto;
    }

    /* === GAYA KARTU UTAMA (UNTUK TEKS/HTML) === */
    .card {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.5);
    }

    /* === WIDGET CARDS (TABEL & GRAFIK) === */
    
    /* Membungkus DataFrame (Tabel) agar jadi kartu */
    [data-testid="stDataFrame"] {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #f0f0f0;
    }

    /* Membungkus Metric (Angka Besar) agar jadi kartu */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #f0f0f0;
    }

    /* === SIDEBAR GLASSMORPHISM (BLUR) === */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(25px) saturate(180%);
        border-right: 1px solid rgba(255, 255, 255, 0.4);
    }

    /* === TYPOGRAPHY & COLORS === */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li {
        color: #333333 !important;
    }
    
    .main-title {
        font-size: 32px; font-weight: 800; color: #1565C0 !important;
        text-align: center; margin-bottom: 5px;
    }
    .main-caption {
        font-size: 16px; color: #555 !important;
        text-align: center; margin-bottom: 20px;
    }

    /* === TAB STYLING === */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 8px;
        gap: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        background-color: transparent;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        color: #1565C0 !important;
        font-weight: bold;
    }

    /* === INFO BOXES === */
    .pros-cons-card { padding: 15px; border-radius: 10px; margin-bottom: 10px; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE LENGKAP (DIPULIHKAN)
# ==========================================
TARIF_PLN = {
    "900 VA (RTM)": 1352,
    "1300 VA - 2200 VA": 1444.70,
    "3500 VA - 5500 VA": 1444.70,
    "6600 VA Ke Atas": 1699.53,
    "Bisnis/Industri (>6600 VA)": 1444.70,
    "Manual Input": 0
}

PANEL_SPECS = {
    "Monocrystalline (Half-Cut/PERC)": {
        "min_wp": 100, "max_wp": 700, "default_wp": 550, "price_per_wp": 3200,
        "pros": ["Efisiensi tinggi (s/d 22%)", "Performa baik saat mendung", "Hemat tempat"],
        "cons": ["Harga investasi sedikit lebih tinggi"]
    },
    "Polycrystalline (Standard)": {
        "min_wp": 50, "max_wp": 360, "default_wp": 250, "price_per_wp": 2600,
        "pros": ["Harga per panel lebih ekonomis", "Tahan panas berlebih"],
        "cons": ["Butuh area atap lebih luas", "Teknologi lama"]
    }
}

BATTERY_SPECS = {
    "Lead Acid / VRLA / Gel": {
        "dod": 0.50, "default_v": 12.0, "price_per_kwh": 2500000, 
        "min_ah": 7, "max_ah": 250, "default_ah": 100,
        "pros": ["Biaya awal murah", "Mudah didapat"],
        "cons": ["Umur pendek (1-2 thn)", "Berat", "DoD rendah (50%)"]
    },
    "Lithium LiFePO4 (3.2V)": {
        "dod": 0.90, "default_v": 3.2, "price_per_kwh": 4800000, 
        "min_ah": 25, "max_ah": 320, "default_ah": 100,
        "pros": ["Umur panjang (7-10 thn)", "Aman", "DoD tinggi (90%)"],
        "cons": ["Harga awal mahal", "Perlu BMS"]
    },
    "Lithium Ion / NMC (3.7V)": {
        "dod": 0.85, "default_v": 3.7, "price_per_kwh": 4200000, 
        "min_ah": 2, "max_ah": 200, "default_ah": 50,
        "pros": ["Densitas energi tinggi", "Ringan"],
        "cons": ["Sensitif panas", "Resiko thermal"]
    },
}

SYSTEM_META = {
    "DC": {"pros": ["Efisiensi Tertinggi", "Biaya Termurah"], "cons": ["Hanya alat DC", "Kabel harus tebal"]},
    "On-Grid": {"pros": ["Termurah per Watt", "Bebas Perawatan", "ROI Cepat"], "cons": ["Mati saat PLN padam", "Wajib Izin"]},
    "Off-Grid": {"pros": ["Mandiri Energi", "Bisa di pelosok"], "cons": ["Biaya Mahal (Baterai)", "Perawatan Rutin"]},
    "Hybrid": {"pros": ["Hemat + Backup", "Fitur Lengkap"], "cons": ["Biaya Mahal", "Kompleks"]}
}

VOLTAGE_OPTIONS = [2.0, 3.2, 3.7, 12.0, 24.0, 48.0]

# ==========================================
# FUNGSI LOGIKA
# ==========================================
def format_rupiah(angka):
    return f"Rp {int(angka):,}".replace(",", ".")

def generate_rab(items):
    data = []
    total_biaya = 0
    raw_labels = []
    raw_values = []
    for i in items:
        subtotal = i['qty'] * i['price']
        total_biaya += subtotal
        data.append({
            "Uraian Pekerjaan": i['item'],
            "Volume": f"{i['qty']}",
            "Satuan": i['unit'],
            "Harga Satuan": format_rupiah(i['price']),
            "Total Harga": format_rupiah(subtotal)
        })
        # Data chart
        short_label = i['item'].split(' ')[0]
        if "Kabel" in i['item'] or "Mounting" in i['item']: short_label = "Support"
        raw_labels.append(short_label) 
        raw_values.append(subtotal)
        
    df = pd.DataFrame(data)
    if not df.empty:
        df.index = np.arange(1, len(df) + 1)
        df.index.name = 'No'
    return df, total_biaya, raw_labels, raw_values

def plot_rab_pie(labels, values):
    df_chart = pd.DataFrame({'label': labels, 'value': values})
    df_chart = df_chart.groupby('label').sum().reset_index()
    fig, ax = plt.subplots(figsize=(3, 3))
    # Warna Pie Chart
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(df_chart)))
    ax.pie(df_chart['value'], labels=df_chart['label'], autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 8, 'color': '#333333'})
    ax.axis('equal') 
    fig.patch.set_alpha(0) 
    return fig

# --- CARD COMPONENT RENDERING ---
def display_roi_analysis(total_invest, yearly_savings_potential, system_type):
    maint_percent = 0.005 if "Battery" not in system_type else 0.015 
    yearly_maintenance = total_invest * maint_percent
    net_savings = yearly_savings_potential - yearly_maintenance
    
    roi_years = 999 if net_savings <= 0 else total_invest / net_savings
    roi_text = "Tidak Balik Modal" if roi_years == 999 else f"{roi_years:.1f} Tahun"

    st.markdown(f"""
    <div class="card" style="border-left: 5px solid #2196F3;">
        <h4 style='color:#1565C0; margin:0;'>📊 Analisis Balik Modal (ROI)</h4>
        <hr style="border-color:#E3F2FD;">
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <div>
                <small>Total Investasi</small><br>
                <b style='font-size: 20px; color: #D32F2F;'>{format_rupiah(total_invest)}</b>
            </div>
            <div style='text-align: right;'>
                <small>Estimasi BEP</small><br>
                <b style='font-size: 20px; color: #2E7D32;'>{roi_text}</b>
            </div>
        </div>
        <div style="background-color:#E3F2FD; padding:10px; border-radius:8px; margin-top:10px;">
            <small>
            ➕ Hemat Listrik: {format_rupiah(yearly_savings_potential)} /thn<br>
            ➖ Perawatan (Est): {format_rupiah(yearly_maintenance)} /thn<br>
            <b>💰 Net Benefit: {format_rupiah(net_savings)} /thn</b>
            </small>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_pros_cons_system(sys_type):
    data = SYSTEM_META[sys_type]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="pros-cons-card" style="background-color: #E8F5E9; border-left: 5px solid #43A047;">
            <b style="color: #2E7D32;">✅ KELEBIHAN {sys_type.upper()}</b><br>
            {'<br>'.join(['• '+x for x in data['pros']])}
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="pros-cons-card" style="background-color: #FFEBEE; border-left: 5px solid #E53935;">
            <b style="color: #C62828;">⚠️ KEKURANGAN {sys_type.upper()}</b><br>
            {'<br>'.join(['• '+x for x in data['cons']])}
        </div>
        """, unsafe_allow_html=True)

def display_component_analysis(panel_type, bat_type=None):
    st.markdown('<div class="card"><h5>🔍 Analisis Komponen Terpilih</h5>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    p_data = PANEL_SPECS[panel_type]
    with c1:
        st.markdown(f"""
        <div style="background-color: #FFF3E0; padding: 12px; border-radius: 8px; border: 1px solid #FFE0B2;">
            <b>PANEL: {panel_type}</b><br>
            <hr style="margin:5px 0; border-color:#FFCC80">
            <span style="color:#2E7D32; font-size:13px;">+ {'<br>+ '.join(p_data['pros'])}</span><br>
            <span style="color:#C62828; font-size:13px;">- {'<br>- '.join(p_data['cons'])}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        if bat_type:
            b_data = BATTERY_SPECS[bat_type]
            html = f"""
            <div style="background-color: #FFF3E0; padding: 12px; border-radius: 8px; border: 1px solid #FFE0B2;">
                <b>BATERAI: {bat_type}</b><br>
                <hr style="margin:5px 0; border-color:#FFCC80">
                <span style="color:#2E7D32; font-size:13px;">+ {'<br>+ '.join(b_data['pros'])}</span><br>
                <span style="color:#C62828; font-size:13px;">- {'<br>- '.join(b_data['cons'])}</span>
            </div>
            """
        else:
            html = """<div style="background-color: #F5F5F5; padding: 12px; border-radius: 8px; color: #757575;"><b>BATERAI: Tidak Ada</b><br>Sistem ini tanpa baterai.</div>"""
        st.markdown(html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("🎛️ Parameter Input")

#file_musik = 'audiobg.mp3' 
#audio_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_musik)
#if os.path.isfile(audio_path):
 #   st.sidebar.markdown("### 🎵 Musik Latar")
  #  st.sidebar.audio(audio_path, format='audio/mp3', start_time=0)
   # st.sidebar.markdown("---")

st.sidebar.markdown("### 1️⃣ Profil Listrik")
metode = st.sidebar.radio("Hitung Berdasarkan:", ["Tagihan (Estimasi)", "Manual (Watt)"])
gol = st.sidebar.selectbox("Golongan Daya:", list(TARIF_PLN.keys()), index=1)
trf = st.sidebar.number_input("Tarif/kWh (Rp)", 100., 5000., 1444.7, step=50.) if gol == "Manual Input" else TARIF_PLN[gol]
st.sidebar.caption(f"⚡ Tarif: {format_rupiah(trf)} /kWh")

wh_day, est_bill = 0, 0
if metode == "Tagihan (Estimasi)":
    bill = st.sidebar.number_input("Tagihan Bulanan (Rp)", 50000, 100000000, 500000, step=50000)
    wh_day = ((bill / trf) / 30) * 1000
    est_bill = bill
else:
    watt = st.sidebar.number_input("Total Watt Alat", 1, 50000, 100)
    hours = st.sidebar.number_input("Jam Nyala/Hari", 1, 24, 12)
    wh_day = watt * hours
    est_bill = (wh_day/1000) * 30 * trf

st.sidebar.info(f"⚡ Beban Harian: **{wh_day:,.0f} Wh**")
st.sidebar.markdown("---")

st.sidebar.markdown("### 2️⃣ Komponen")
# Panel Input
p_type = st.sidebar.selectbox("Jenis Panel", list(PANEL_SPECS.keys()))
p_data = PANEL_SPECS[p_type]
wp_panel = st.sidebar.number_input("Kapasitas Panel (Wp)", min_value=p_data['min_wp'], max_value=p_data['max_wp'], value=p_data['default_wp'], step=10)

# Baterai Input
b_type = st.sidebar.selectbox("Jenis Baterai", list(BATTERY_SPECS.keys()))
b_data = BATTERY_SPECS[b_type]
idx_v = 3
try: idx_v = VOLTAGE_OPTIONS.index(b_data["default_v"])
except: pass
v_bat = st.sidebar.selectbox("Voltase Unit (V)", VOLTAGE_OPTIONS, index=idx_v)
ah_bat = st.sidebar.number_input("Kapasitas Unit (Ah)", min_value=b_data['min_ah'], max_value=b_data['max_ah'], value=b_data['default_ah'], step=5)

st.sidebar.markdown("---")
h_sun = st.sidebar.number_input("Sun Hours (Jam)", 2.0, 8.0, 3.5)
h_backup = st.sidebar.number_input("Cadangan (Hari)", 1, 5, 1)
v_sys_rec = 48 if wh_day > 5000 else 24 if wh_day > 1500 else 12
v_sys = st.sidebar.selectbox("Voltase Sistem (V)", [12, 24, 48], index=[12, 24, 48].index(v_sys_rec))

# ==========================================
# MAIN APP
# ==========================================
st.markdown("""
<div class="card" style="text-align: center; padding: 30px;">
    <h1 class="main-title">Rekomendasi PLTS Untuk Rumah</h1>
    <p class="main-caption">Simulasi PLTS Akurat dengan Analisis ROI & Detail Komponen</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["💡 DC SYSTEM", "🏠 ON-GRID", "🔋 OFF-GRID", "🔄 HYBRID"])

def calc_panel(req_wp): 
    n = int(np.ceil(req_wp / wp_panel))
    return n, n * wp_panel

def calc_bat(wh_load):
    wh_real = wh_load * h_backup / BATTERY_SPECS[b_type]['dod']
    s = int(np.ceil(v_sys / v_bat))
    p = int(np.ceil((wh_real / v_sys) / ah_bat))
    tot = s * p
    return {"s": s, "p": p, "tot": tot, "kwh": (tot * v_bat * ah_bat)/1000}

# --- TAB 1: DC SYSTEM ---
with tab1:
    wh_dc = wh_day / 0.85
    n_p, tot_wp = calc_panel(wh_dc / h_sun)
    d_bat = calc_bat(wh_dc)
    scc_amp = (tot_wp / v_sys) * 1.25

    # Card 1: Header
    st.markdown(f"""
    <div class="card">
        <h3 style='color:#1565C0; margin:0;'>Kapasitas: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3>
        <p>Sistem ini hanya menyalakan beban DC. Tidak butuh inverter.</p>
        <br>
    </div>
    """, unsafe_allow_html=True)

    # Card 2: Pros/Cons
    st.markdown('<div class="card">', unsafe_allow_html=True)
    display_pros_cons_system("DC")
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 3: Component Analysis
    display_component_analysis(p_type, b_type)

    # Card 4: Specs Table
    st.markdown('<div class="card"><h5>📋 Rincian Spesifikasi</h5>', unsafe_allow_html=True)
    d_spec = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Unit"},
        {"Komponen": "Baterai", "Spesifikasi": f"{b_type} {v_bat}V {ah_bat}Ah", "Jumlah": f"{d_bat['tot']} Unit ({d_bat['s']}S {d_bat['p']}P)"},
        {"Komponen": "SCC (Controller)", "Spesifikasi": f"MPPT Controller {int(scc_amp)}A (System {v_sys}V)", "Jumlah": "1 Unit"},
        {"Komponen": "Kabel & Safety", "Spesifikasi": "Kabel PV 4mm/6mm, MCB DC, Box Panel", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Card 5: RAB & ROI
    st.markdown('<div class="card"><h5>💰 RAB & ROI</h5>', unsafe_allow_html=True)
    items = [
        {'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']},
        {'item': f"Baterai {ah_bat}Ah", 'qty': d_bat['tot'], 'unit': 'Unit', 'price': (v_bat*ah_bat/1000)*BATTERY_SPECS[b_type]['price_per_kwh']},
        {'item': f"SCC {int(scc_amp)}A", 'qty': 1, 'unit': 'Unit', 'price': 800000 + (scc_amp*10000)},
        {'item': "Kabel & Acc DC", 'qty': 1, 'unit': 'Lot', 'price': 500000 + (n_p*100000)},
        {'item': "Jasa Instalasi", 'qty': 1, 'unit': 'Lot', 'price': 1500000}
    ]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, est_bill*12, "DC Battery")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: ON-GRID ---
with tab2:
    n_p, tot_wp = calc_panel(wh_day / (h_sun * 0.9))
    inv_cap = tot_wp / 1000
    
    st.markdown(f"""
    <div class="card">
        <h3 style='color:#1565C0; margin:0;'>Kapasitas: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3>
        <p>Terhubung ke PLN. Menghemat tagihan bulanan. Mati saat PLN padam.</p>
        <br>

[Image of On-Grid solar system diagram]

    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    display_pros_cons_system("On-Grid")
    st.markdown('</div>', unsafe_allow_html=True)
    display_component_analysis(p_type, None)
    
    st.markdown('<div class="card"><h5>📋 Rincian Spesifikasi</h5>', unsafe_allow_html=True)
    d_spec = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Unit"},
        {"Komponen": "Grid-Tie Inverter", "Spesifikasi": f"Inverter On-Grid {inv_cap:.1f} kW (Pure Sine Wave)", "Jumlah": "1 Unit"},
        {"Komponen": "Mounting System", "Spesifikasi": "Rail Aluminium, Clamp Mid/End, Hook Tile/Tin", "Jumlah": f"{n_p} Set"},
        {"Komponen": "Proteksi AC/DC", "Spesifikasi": "Combiner Box, SPD, MCB, Fuse", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h5>💰 RAB & ROI</h5>', unsafe_allow_html=True)
    items = [
        {'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']},
        {'item': f"Inverter {inv_cap:.1f}kW", 'qty': 1, 'unit': 'Unit', 'price': 3000000 * (inv_cap if inv_cap > 1 else 1)},
        {'item': "Mounting Kit", 'qty': n_p, 'unit': 'Set', 'price': 150000},
        {'item': "Proteksi & Kabel", 'qty': 1, 'unit': 'Lot', 'price': 2000000 + (n_p*50000)},
        {'item': "Instalasi & SLO", 'qty': 1, 'unit': 'Lot', 'price': 3500000}
    ]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, (tot_wp * h_sun * 0.85 * 365 / 1000) * trf, "On-Grid")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: OFF-GRID ---
with tab3:
    n_p, tot_wp = calc_panel((wh_day/0.85)/h_sun)
    d_bat = calc_bat(wh_day/0.85)
    inv_cap = max(1000, wh_day/12 * 2) # Minimal 1000W

    st.markdown(f"""
    <div class="card">
        <h3 style='color:#1565C0; margin:0;'>Kapasitas: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3>
        <p>Sistem mandiri 100%. Tidak tergantung PLN sama sekali.</p>
        <br>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    display_pros_cons_system("Off-Grid")
    st.markdown('</div>', unsafe_allow_html=True)
    display_component_analysis(p_type, b_type)
    
    st.markdown('<div class="card"><h5>📋 Rincian Spesifikasi</h5>', unsafe_allow_html=True)
    d_spec = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Unit"},
        {"Komponen": "Baterai Bank", "Spesifikasi": f"{b_type} {v_bat}V {ah_bat}Ah (Total: {d_bat['kwh']:.1f} kWh)", "Jumlah": f"{d_bat['tot']} Unit"},
        {"Komponen": "Inverter Off-Grid", "Spesifikasi": f"Pure Sine Wave {int(inv_cap)}W (Surge 2x)", "Jumlah": "1 Unit"},
        {"Komponen": "BOS", "Spesifikasi": "Rak Baterai, Kabel, Panel Box", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h5>💰 RAB & ROI</h5>', unsafe_allow_html=True)
    items = [
        {'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']},
        {'item': f"Baterai Bank", 'qty': d_bat['tot'], 'unit': 'Unit', 'price': (v_bat*ah_bat/1000)*BATTERY_SPECS[b_type]['price_per_kwh']},
        {'item': f"Inverter {int(inv_cap)}W", 'qty': 1, 'unit': 'Set', 'price': 3500000 + (inv_cap * 1500)},
        {'item': "Mounting & Rak", 'qty': 1, 'unit': 'Lot', 'price': 2000000},
        {'item': "Instalasi", 'qty': 1, 'unit': 'Lot', 'price': 3000000}
    ]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, est_bill*12, "Off-Grid Battery")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: HYBRID ---
with tab4:
    n_p, tot_wp = calc_panel((wh_day/(h_sun*0.9)))
    d_bat = calc_bat(wh_day*0.5) # Backup 50%
    inv_cap = (tot_wp/1000) + 1

    st.markdown(f"""
    <div class="card">
        <h3 style='color:#1565C0; margin:0;'>Kapasitas: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3>
        <p>Hemat tagihan + Backup saat mati lampu (UPS Function).</p>
        <br>

[Image of Hybrid solar inverter system diagram]

    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    display_pros_cons_system("Hybrid")
    st.markdown('</div>', unsafe_allow_html=True)
    display_component_analysis(p_type, b_type)
    
    st.markdown('<div class="card"><h5>📋 Rincian Spesifikasi</h5>', unsafe_allow_html=True)
    d_spec = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Unit"},
        {"Komponen": "Inverter Hybrid", "Spesifikasi": f"Hybrid Inverter {inv_cap:.1f} kW (On-Grid + Battery Backup)", "Jumlah": "1 Unit"},
        {"Komponen": "Baterai Backup", "Spesifikasi": f"{b_type} {v_bat}V {ah_bat}Ah (Backup 50% Load)", "Jumlah": f"{d_bat['tot']} Unit"},
        {"Komponen": "Sistem Proteksi", "Spesifikasi": "ATS/COS, Surge Protection, Grounding", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h5>💰 RAB & ROI</h5>', unsafe_allow_html=True)
    items = [
        {'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']},
        {'item': "Baterai Backup", 'qty': d_bat['tot'], 'unit': 'Unit', 'price': (v_bat*ah_bat/1000)*BATTERY_SPECS[b_type]['price_per_kwh']},
        {'item': f"Inverter {inv_cap:.1f}kW", 'qty': 1, 'unit': 'Unit', 'price': 8000000 + (inv_cap * 2000000)},
        {'item': "Aksesoris & ATS", 'qty': 1, 'unit': 'Lot', 'price': 3500000},
        {'item': "Instalasi Lengkap", 'qty': 1, 'unit': 'Lot', 'price': 5000000}
    ]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, (tot_wp * h_sun * 0.85 * 365 / 1000) * trf, "Hybrid")
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("Kalkulator PLTS Pro V6.7 - Ultimate Edition")