import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Solar System Pro V7.3",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS CUSTOM (WARM PASTEL THEME) ---
st.markdown("""
<style>
    /* === BACKGROUND WARM PASTEL === */
    .stApp {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFE0B2 100%);
        background-attachment: fixed;
    }

    /* RESET CONTAINER UTAMA */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
        margin: auto;
    }

    /* === INPUT CONTAINER STYLING === */
    [data-testid="stExpander"] {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        border: 1px solid #FFCC80;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* === GAYA KARTU UTAMA === */
    .card {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(255,255,255,0.6);
    }
    
    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li {
        color: #4E342E !important; 
    }
    .main-title {
        font-size: 32px; font-weight: 800; color: #E65100 !important;
        text-align: center; margin-bottom: 5px;
    }
    .main-caption {
        font-size: 16px; color: #6D4C41 !important;
        text-align: center; margin-bottom: 20px;
    }

    /* === INFO BOXES (PROS/CONS) === */
    .pros-box { background-color: #E8F5E9; border-left: 5px solid #43A047; padding: 10px; border-radius: 8px; font-size: 13px; height: 100%; }
    .cons-box { background-color: #FFEBEE; border-left: 5px solid #E53935; padding: 10px; border-radius: 8px; font-size: 13px; height: 100%; }
    .component-header { font-weight: bold; border-bottom: 1px solid #ddd; margin-bottom: 8px; padding-bottom: 4px; color: #333; }
    
    /* === REKOMENDASI TEXT BOXES === */
    .rec-box-green {
        background-color: #E8F5E9; border: 1px solid #4CAF50; border-radius: 8px;
        padding: 10px; margin-top: 5px; font-size: 13px; color: #1B5E20 !important;
    }
    .rec-box-blue {
        background-color: #E3F2FD; border: 1px solid #2196F3; border-radius: 8px;
        padding: 10px; margin-top: 5px; font-size: 13px; color: #0D47A1 !important;
    }
    .rec-box-yellow {
        background-color: #FFF3E0; border: 1px solid #FF9800; border-radius: 8px;
        padding: 10px; margin-top: 5px; font-size: 13px; color: #E65100 !important;
    }
    .rec-box-red {
        background-color: #FFEBEE; border: 1px solid #F44336; border-radius: 8px;
        padding: 10px; margin-top: 5px; font-size: 13px; font-weight: bold; color: #B71C1C !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE
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
        "pros": ["Teknologi terbaru & canggih", "Tetap bagus walau agak mendung", "Hemat tempat (ukuran lebih kecil)"],
        "cons": ["Harga per lembar agak mahal"]
    },
    "Polycrystalline (Standard)": {
        "min_wp": 50, "max_wp": 360, "default_wp": 250, "price_per_wp": 2600,
        "pros": ["Harga lebih murah/ekonomis", "Cukup tahan cuaca panas terik"],
        "cons": ["Butuh atap yang luas", "Teknologi lama (kurang efisien)"]
    }
}

BATTERY_SPECS = {
    "Lead Acid / VRLA / Gel": {
        "dod": 0.50, "default_v": 12.0, "price_per_kwh": 2500000, 
        "min_ah": 7, "max_ah": 250, "default_ah": 100,
        "pros": ["Harga beli awal paling murah", "Gampang dicari di toko aki"],
        "cons": ["Cepat rusak (1-2 tahun ganti)", "Berat banget", "Cuma bisa dipakai 50% isinya"]
    },
    "Lithium LiFePO4 (3.2V)": {
        "dod": 0.90, "default_v": 3.2, "price_per_kwh": 4800000, 
        "min_ah": 25, "max_ah": 320, "default_ah": 100,
        "pros": ["Sangat awet (bisa 7-10 tahun)", "Aman & tidak mudah terbakar", "Bisa dipakai sampai habis (90%)"],
        "cons": ["Harganya mahal di awal", "Perlu alat khusus (BMS)"]
    },
    "Lithium Ion / NMC (3.7V)": {
        "dod": 0.85, "default_v": 3.7, "price_per_kwh": 4200000, 
        "min_ah": 2, "max_ah": 200, "default_ah": 50,
        "pros": ["Ukurannya kecil & ringan", "Daya tampung besar"],
        "cons": ["Tidak tahan panas", "Kurang cocok untuk sistem besar"]
    },
}

SYSTEM_META = {
    "DC": {"pros": ["Biaya paling murah meriah", "Sangat hemat listrik"], "cons": ["Alat terbatas (cuma lampu/kipas DC)", "Tidak bisa colok TV/Kulkas biasa"]},
    "On-Grid": {"pros": ["Paling cepat balik modal", "Tagihan listrik turun drastis"], "cons": ["Ikut mati kalau PLN padam (Safety)", "Harus lapor pasang ke PLN"]},
    "Off-Grid": {"pros": ["Merdeka! Tidak butuh PLN sama sekali", "Bisa pasang di hutan/kebun"], "cons": ["Biaya mahal (beli banyak baterai)", "Baterai perlu perawatan"]},
    "Hybrid": {"pros": ["Double Untung: Hemat + Cadangan Listrik", "Anti Mati Lampu"], "cons": ["Modal awal paling besar", "Pemasangan kabel rumit"]}
}

VOLTAGE_OPTIONS = [2.0, 3.2, 3.7, 12.0, 24.0, 48.0]

# ==========================================
# FUNGSI HELPER
# ==========================================
def format_rupiah(angka): return f"Rp {int(angka):,}".replace(",", ".")

def generate_rab(items):
    data = []
    total_biaya = 0
    raw_labels, raw_values = [], []
    for i in items:
        subtotal = i['qty'] * i['price']
        total_biaya += subtotal
        data.append({"Uraian Pekerjaan": i['item'], "Volume": f"{i['qty']}", "Satuan": i['unit'], "Harga Satuan": format_rupiah(i['price']), "Total Harga": format_rupiah(subtotal)})
        short_label = "Support" if "Kabel" in i['item'] or "Mounting" in i['item'] else i['item'].split(' ')[0]
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
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(df_chart)))
    ax.pie(df_chart['value'], labels=df_chart['label'], autopct='%1.1f%%', startangle=90, colors=colors, textprops={'fontsize': 8, 'color': '#333333'})
    ax.axis('equal'); fig.patch.set_alpha(0)
    return fig

# ==========================================
# HEADER & INPUT DENGAN REKOMENDASI DINAMIS & PERSISTENT
# ==========================================
st.markdown("""
<div class="card" style="text-align: center; padding: 20px; background: rgba(255,255,255,0.95);">
    <h1 class="main-title">☀️ Kalkulator Solar System Pro</h1>
    <p class="main-caption">Simulasi Listrik Tenaga Surya Cerdas & Interaktif</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ Konfigurasi & Parameter Input (Klik untuk Buka/Tutup)", expanded=True):
    col1, col2, col3 = st.columns(3)

    # --- KOLOM 1: LISTRIK ---
    with col1:
        st.markdown("##### 1️⃣ Profil Listrik")
        metode = st.radio("Metode Hitung:", ["Tagihan (Estimasi)", "Manual (Watt)"], horizontal=True)
        gol = st.selectbox("Golongan Daya:", list(TARIF_PLN.keys()), index=1)
        
        trf_val = TARIF_PLN[gol] if gol != "Manual Input" else 1444.7
        trf = st.number_input("Tarif per kWh (Rp)", 100., 10000., float(trf_val), step=50.)

        wh_day = 0
        est_bill = 0
        
        if metode == "Tagihan (Estimasi)":
            bill = st.number_input("Tagihan Listrik per Bulan (Rp)", 50000, 100000000, 500000, step=50000)
            wh_day = ((bill / trf) / 30) * 1000
            est_bill = bill
        else:
            watt = st.number_input("Total Watt Alat", 1, 50000, 100)
            hours = st.number_input("Jam Nyala per Hari", 1, 24, 12)
            wh_day = watt * hours
            est_bill = (wh_day/1000) * 30 * trf
            
        st.markdown(f"**⚡ Beban Harian: {wh_day:,.0f} Wh**")
        
        # Rekomendasi Beban
        if wh_day > 10000:
            st.markdown('<div class="rec-box-red">⚠️ Beban sangat tinggi! Butuh area atap yang sangat luas.</div>', unsafe_allow_html=True)
        elif wh_day < 500:
            st.markdown('<div class="rec-box-blue">ℹ️ Beban kecil. Sistem 12V sederhana sudah cukup.</div>', unsafe_allow_html=True)

    # --- KOLOM 2: KOMPONEN (DENGAN LOGIKA REKOMENDASI PERSISTENT) ---
    with col2:
        st.markdown("##### 2️⃣ Pilih Komponen")
        
        # --- A. LOGIKA PANEL ---
        p_type = st.selectbox("Jenis Panel", list(PANEL_SPECS.keys()))
        p_data = PANEL_SPECS[p_type]
        wp_panel = st.number_input("Ukuran per Panel (Wp)", min_value=p_data['min_wp'], max_value=p_data['max_wp'], value=p_data['default_wp'], step=10)
        
        # Hitung estimasi panel kasar untuk rekomendasi
        est_h_sun = 3.5
        est_panels_needed = int(np.ceil(wh_day / (est_h_sun * wp_panel * 0.85)))
        
        if est_panels_needed > 12:
            st.markdown(f"""
            <div class="rec-box-red">
            ❌ <b>Ukuran Panel Kekecilan!</b><br>
            Anda akan butuh <b>±{est_panels_needed} lembar</b> panel.<br>
            Wajib ganti ke panel besar (450Wp-550Wp) agar atap muat.
            </div>
            """, unsafe_allow_html=True)
        elif est_panels_needed < 3 and wp_panel > 500:
            st.markdown(f"""
            <div class="rec-box-blue">
            ℹ️ Panel terlalu besar untuk beban sekecil ini. Panel 200Wp-300Wp lebih mudah dipasang.
            </div>
            """, unsafe_allow_html=True)
        else:
             st.markdown(f"""<div class="rec-box-green">✅ Pas. Butuh sekitar {est_panels_needed} lembar panel.</div>""", unsafe_allow_html=True)

        # --- B. LOGIKA BATERAI ---
        b_type = st.selectbox("Jenis Baterai", list(BATTERY_SPECS.keys()))
        b_data = BATTERY_SPECS[b_type]
        
        idx_v = VOLTAGE_OPTIONS.index(b_data["default_v"]) if b_data["default_v"] in VOLTAGE_OPTIONS else 3
        v_bat = st.selectbox("Voltase Baterai (V)", VOLTAGE_OPTIONS, index=idx_v)
        ah_bat = st.number_input("Kapasitas Baterai (Ah)", min_value=b_data['min_ah'], max_value=b_data['max_ah'], value=b_data['default_ah'], step=5)
        
        # --- PERHITUNGAN REKOMENDASI BATERAI ---
        # Asumsi 1 hari cadangan (minimal) untuk hitungan cepat di input
        cap_per_bat_wh = v_bat * ah_bat
        # Safety factor 0.6 (DoD rata-rata kasar untuk display input)
        if cap_per_bat_wh > 0 and wh_day > 0:
            est_bat_needed = wh_day / (cap_per_bat_wh * 0.7) 
            
            if est_bat_needed > 16:
                st.markdown(f"""
                <div class="rec-box-red">
                ❌ <b>Kapasitas Baterai Kekecilan!</b><br>
                Anda akan butuh <b>±{int(est_bat_needed)} unit</b> baterai.<br>
                Ganti ke Ah lebih besar (misal 100Ah/200Ah) atau Voltase lebih tinggi (Lithium 48V).
                </div>
                """, unsafe_allow_html=True)
            elif est_bat_needed > 6:
                st.markdown(f"""
                <div class="rec-box-yellow">
                ⚠️ <b>Terlalu Banyak Unit</b><br>
                Estimasi butuh <b>±{int(est_bat_needed)} unit</b>.<br>
                Saran: Naikkan kapasitas Ah baterai agar hemat tempat rak.
                </div>
                """, unsafe_allow_html=True)
            else:
                 st.markdown(f"""<div class="rec-box-green">✅ Ukuran Sesuai. Estimasi butuh ±{int(np.ceil(est_bat_needed))} unit.</div>""", unsafe_allow_html=True)
        
        # Saran Tipe Baterai
        if "Lead Acid" in b_type and wh_day > 3000:
             st.markdown('<div class="rec-box-blue">💡 Tips: Untuk beban berat, Baterai Lithium (LiFePO4) jauh lebih awet jangka panjang.</div>', unsafe_allow_html=True)

    # --- KOLOM 3: LINGKUNGAN & VOLTASE SISTEM ---
    with col3:
        st.markdown("##### 3️⃣ Sistem & Lokasi")
        h_sun = st.slider("Sun Hours (Jam)", 2.0, 8.0, 3.5, 0.1)
        h_backup = st.slider("Cadangan (Hari)", 1, 5, 1)

        # Auto Recommend Logic
        v_sys_rec = 48 if wh_day > 4000 else 24 if wh_day > 1000 else 12
        v_sys = st.selectbox(
            "Voltase Sistem (V)", [12, 24, 48], 
            index=[12, 24, 48].index(v_sys_rec)
        )
        
        # --- REKOMENDASI TEGAS VOLTASE ---
        if wh_day > 5000 and v_sys == 12:
            st.markdown(f"""
            <div class="rec-box-red">
            🛑 <b>BAHAYA: Jangan Pakai 12V!</b><br>
            Beban >5000Wh di 12V akan membuat kabel sangat panas & berisiko kebakaran.<br>
            👉 <b>Wajib Ganti ke 48V.</b>
            </div>
            """, unsafe_allow_html=True)
        elif wh_day > 2000 and v_sys == 12:
            st.markdown("""<div class="rec-box-yellow">⚠️ Tidak Efisien. Sebaiknya gunakan sistem 24V atau 48V.</div>""", unsafe_allow_html=True)
        elif v_sys == v_sys_rec:
             st.markdown(f"""<div class="rec-box-green">✅ Pilihan Tepat. Sistem {v_sys}V cocok untuk beban ini.</div>""", unsafe_allow_html=True)

# ==========================================
# FUNGSI TAMPILAN
# ==========================================
def display_energy_balance(load_wh, capacity_wp, sun_hours, efficiency=0.85):
    prod_wh = capacity_wp * sun_hours * efficiency
    balance = prod_wh - load_wh
    st.markdown("""<div class="card" style="padding: 15px; margin-bottom: 20px;">
        <h5 style="margin-top:0; color:#E65100;">⚡ Neraca Energi Harian</h5>""", unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)
    k1.metric("Beban Rumah (Load)", f"{load_wh/1000:.2f} kWh")
    k2.metric("Produksi Panel (Est)", f"{prod_wh/1000:.2f} kWh")
    label_bal = "Surplus (Disimpan/Ekspor)" if balance >= 0 else "Defisit (Ambil PLN)"
    k3.metric(label_bal, f"{balance/1000:.2f} kWh", delta=f"{balance/1000:.2f} kWh")
    st.caption("*) Surplus = Listrik sisa yang bisa ditabung ke baterai atau dijual ke PLN.")
    st.markdown("</div>", unsafe_allow_html=True)

def display_component_live_analysis(panel_type, bat_type):
    p_data, b_data = PANEL_SPECS[panel_type], BATTERY_SPECS[bat_type]
    st.markdown("##### 🔍 Info Komponen Pilihan Anda")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="card" style="padding: 15px; background: rgba(255,255,255,0.6);"><div class="component-header">☀️ Panel: {panel_type}</div><div style="display:flex; gap:10px;"><div class="pros-box" style="flex:1;"><b style="color:#2E7D32">👍 ENAKNYA:</b><br>{'<br>'.join(['+ '+x for x in p_data['pros']])}</div><div class="cons-box" style="flex:1;"><b style="color:#C62828">👎 KURANGNYA:</b><br>{'<br>'.join(['- '+x for x in p_data['cons']])}</div></div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="card" style="padding: 15px; background: rgba(255,255,255,0.6);"><div class="component-header">🔋 Baterai: {bat_type}</div><div style="display:flex; gap:10px;"><div class="pros-box" style="flex:1;"><b style="color:#2E7D32">👍 ENAKNYA:</b><br>{'<br>'.join(['+ '+x for x in b_data['pros']])}</div><div class="cons-box" style="flex:1;"><b style="color:#C62828">👎 KURANGNYA:</b><br>{'<br>'.join(['- '+x for x in b_data['cons']])}</div></div></div>""", unsafe_allow_html=True)

def display_system_pros_cons(sys_type):
    data = SYSTEM_META[sys_type]
    st.markdown(f"""<div style="margin-bottom: 20px;"><div style="display:flex; gap:15px; align-items:stretch;"><div class="pros-box" style="flex:1; background-color: #F1F8E9; border-left: 5px solid #66BB6A;"><h5 style="margin:0; color:#2E7D32;">✅ Kenapa Pilih {sys_type}?</h5><ul style="margin:5px 0 0 -15px; color:#33691E;">{''.join(['<li>'+x+'</li>' for x in data['pros']])}</ul></div><div class="cons-box" style="flex:1; background-color: #FFEBEE; border-left: 5px solid #EF5350;"><h5 style="margin:0; color:#C62828;">⚠️ Yang Perlu Dipikirkan</h5><ul style="margin:5px 0 0 -15px; color:#B71C1C;">{''.join(['<li>'+x+'</li>' for x in data['cons']])}</ul></div></div></div>""", unsafe_allow_html=True)

def display_roi_analysis(total_invest, yearly_savings_potential, system_type):
    maint_percent = 0.005 if "Battery" not in system_type else 0.015 
    yearly_maintenance = total_invest * maint_percent
    net_savings = yearly_savings_potential - yearly_maintenance
    roi_years = 999 if net_savings <= 0 else total_invest / net_savings
    roi_text = "Tidak Balik Modal" if roi_years == 999 else f"{roi_years:.1f} Tahun"
    st.markdown(f"""<div class="card" style="border-left: 5px solid #29B6F6;"><h4 style='color:#0277BD; margin:0;'>📊 Kapan Balik Modal?</h4><hr style="border-color:#E1F5FE;"><div style='display: flex; justify-content: space-between; align-items: center;'><div><small>Modal Awal</small><br><b style='font-size: 20px; color: #D84315;'>{format_rupiah(total_invest)}</b></div><div style='text-align: right;'><small>Perkiraan Balik Modal</small><br><b style='font-size: 20px; color: #2E7D32;'>{roi_text}</b></div></div><div style="background-color:#E1F5FE; padding:10px; border-radius:8px; margin-top:10px;"><small>➕ Hemat Listrik: {format_rupiah(yearly_savings_potential)} /tahun<br>➖ Biaya Perawatan: {format_rupiah(yearly_maintenance)} /tahun<br><b>💰 Untung Bersih: {format_rupiah(net_savings)} /tahun</b></small></div></div>""", unsafe_allow_html=True)

# PREVIEW KOMPONEN (GLOBAL)
display_component_live_analysis(p_type, b_type)

# LOGIKA HITUNGAN
def calc_panel(req_wp): 
    n = int(np.ceil(req_wp / wp_panel))
    return n, n * wp_panel

def calc_bat(wh_load):
    wh_real = wh_load * h_backup / BATTERY_SPECS[b_type]['dod']
    s = int(np.ceil(v_sys / v_bat))
    p = int(np.ceil((wh_real / v_sys) / ah_bat))
    tot = s * p
    return {"s": s, "p": p, "tot": tot, "kwh": (tot * v_bat * ah_bat)/1000}

st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["💡 SYSTEM DC", "🏠 ON-GRID (HEMAT)", "🔋 OFF-GRID (MANDIRI)", "🔄 HYBRID (BACKUP)"])

# --- TAB 1: DC SYSTEM ---
with tab1:
    display_system_pros_cons("DC")
    wh_dc = wh_day / 0.85
    n_p, tot_wp = calc_panel(wh_dc / h_sun)
    d_bat = calc_bat(wh_dc)
    scc_amp = (tot_wp / v_sys) * 1.25
    st.markdown(f"""<div class="card"><h3 style='color:#E65100; margin:0;'>Kapasitas Panel: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3><p>Sistem sederhana. Hanya bisa menyalakan lampu DC atau kipas DC.</p></div>""", unsafe_allow_html=True)
    display_energy_balance(wh_dc, tot_wp, h_sun, efficiency=0.85)
    st.markdown('<div class="card"><h5>📋 Daftar Belanja</h5>', unsafe_allow_html=True)
    d_spec = [{"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Lembar"}, {"Komponen": "Baterai", "Spesifikasi": f"{b_type} {v_bat}V {ah_bat}Ah", "Jumlah": f"{d_bat['tot']} Unit"}, {"Komponen": "SCC (Cas Aki)", "Spesifikasi": f"MPPT Controller {int(scc_amp)}A (Sistem {v_sys}V)", "Jumlah": "1 Unit"}, {"Komponen": "Kabel & Pengaman", "Spesifikasi": "Kabel PV, Sekring DC, Box Panel", "Jumlah": "1 Paket"}]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h5>💰 Perkiraan Biaya & Untung</h5>', unsafe_allow_html=True)
    items = [{'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']}, {'item': f"Baterai {ah_bat}Ah", 'qty': d_bat['tot'], 'unit': 'Unit', 'price': (v_bat*ah_bat/1000)*BATTERY_SPECS[b_type]['price_per_kwh']}, {'item': f"SCC {int(scc_amp)}A", 'qty': 1, 'unit': 'Unit', 'price': 800000 + (scc_amp*10000)}, {'item': "Kabel & Acc DC", 'qty': 1, 'unit': 'Lot', 'price': 500000 + (n_p*100000)}, {'item': "Jasa Pasang", 'qty': 1, 'unit': 'Lot', 'price': 1500000}]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, est_bill*12, "DC Battery")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: ON-GRID ---
with tab2:
    display_system_pros_cons("On-Grid")
    n_p, tot_wp = calc_panel(wh_day / (h_sun * 0.9))
    inv_cap = tot_wp / 1000
    st.markdown(f"""<div class="card"><h3 style='color:#E65100; margin:0;'>Kapasitas Panel: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3><p>Sistem penghemat tagihan PLN. Tanpa Baterai.</p>
    </div>""", unsafe_allow_html=True)
   

    
    display_energy_balance(wh_day, tot_wp, h_sun, efficiency=0.90)
    st.markdown('<div class="card"><h5>📋 Daftar Belanja</h5>', unsafe_allow_html=True)
    d_spec = [{"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Lembar"}, {"Komponen": "Inverter On-Grid", "Spesifikasi": f"Inverter {inv_cap:.1f} kW (Pengubah Arus ke PLN)", "Jumlah": "1 Unit"}, {"Komponen": "Dudukan Panel", "Spesifikasi": "Rel Aluminium & Penjepit", "Jumlah": f"{n_p} Set"}, {"Komponen": "Pengaman Listrik", "Spesifikasi": "Box Panel, Anti Petir (SPD), MCB", "Jumlah": "1 Paket"}]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h5>💰 Perkiraan Biaya & Untung</h5>', unsafe_allow_html=True)
    items = [{'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']}, {'item': f"Inverter {inv_cap:.1f}kW", 'qty': 1, 'unit': 'Unit', 'price': 3000000 * (inv_cap if inv_cap > 1 else 1)}, {'item': "Dudukan", 'qty': n_p, 'unit': 'Set', 'price': 150000}, {'item': "Pengaman", 'qty': 1, 'unit': 'Lot', 'price': 2000000 + (n_p*50000)}, {'item': "Pasang & SLO", 'qty': 1, 'unit': 'Lot', 'price': 3500000}]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, (tot_wp * h_sun * 0.85 * 365 / 1000) * trf, "On-Grid")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: OFF-GRID ---
with tab3:
    display_system_pros_cons("Off-Grid")
    n_p, tot_wp = calc_panel((wh_day/0.85)/h_sun)
    d_bat = calc_bat(wh_day/0.85)
    inv_cap = max(1000, wh_day/12 * 2) 
    st.markdown(f"""<div class="card"><h3 style='color:#E65100; margin:0;'>Kapasitas Panel: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3><p>Sistem mandiri tanpa PLN. Listrik disimpan di baterai.</p></div>""", unsafe_allow_html=True)
    display_energy_balance(wh_day/0.85, tot_wp, h_sun, efficiency=0.85)
    st.markdown('<div class="card"><h5>📋 Daftar Belanja</h5>', unsafe_allow_html=True)
    d_spec = [{"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Lembar"}, {"Komponen": "Bank Baterai", "Spesifikasi": f"{b_type} {v_bat}V {ah_bat}Ah (Total: {d_bat['kwh']:.1f} kWh)", "Jumlah": f"{d_bat['tot']} Unit"}, {"Komponen": "Inverter Off-Grid", "Spesifikasi": f"Pengubah Arus {int(inv_cap)} Watt", "Jumlah": "1 Unit"}, {"Komponen": "Aksesoris", "Spesifikasi": "Rak Baterai, Kabel, Box Panel", "Jumlah": "1 Paket"}]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h5>💰 Perkiraan Biaya & Untung</h5>', unsafe_allow_html=True)
    items = [{'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']}, {'item': f"Baterai Bank", 'qty': d_bat['tot'], 'unit': 'Unit', 'price': (v_bat*ah_bat/1000)*BATTERY_SPECS[b_type]['price_per_kwh']}, {'item': f"Inverter {int(inv_cap)}W", 'qty': 1, 'unit': 'Set', 'price': 3500000 + (inv_cap * 1500)}, {'item': "Rak & Mounting", 'qty': 1, 'unit': 'Lot', 'price': 2000000}, {'item': "Jasa Pasang", 'qty': 1, 'unit': 'Lot', 'price': 3000000}]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, est_bill*12, "Off-Grid Battery")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 4: HYBRID ---
with tab4:
    display_system_pros_cons("Hybrid")
    n_p, tot_wp = calc_panel((wh_day/(h_sun*0.9)))
    d_bat = calc_bat(wh_day*0.5)
    inv_cap = (tot_wp/1000) + 1
    st.markdown(f"""<div class="card"><h3 style='color:#E65100; margin:0;'>Kapasitas Panel: {tot_wp} Wp ({tot_wp/1000:.2f} kWp)</h3><p>Gabungan On-Grid (Hemat) + Baterai (Backup).</p>
    </div>""", unsafe_allow_html=True)
    
   
    display_energy_balance(wh_day, tot_wp, h_sun, efficiency=0.90)
    st.markdown('<div class="card"><h5>📋 Daftar Belanja</h5>', unsafe_allow_html=True)
    d_spec = [{"Komponen": "Panel Surya", "Spesifikasi": f"{p_type} {wp_panel}Wp", "Jumlah": f"{n_p} Lembar"}, {"Komponen": "Inverter Hybrid", "Spesifikasi": f"Hybrid Inverter {inv_cap:.1f} kW", "Jumlah": "1 Unit"}, {"Komponen": "Baterai Cadangan", "Spesifikasi": f"{b_type} {v_bat}V {ah_bat}Ah", "Jumlah": f"{d_bat['tot']} Unit"}, {"Komponen": "Sistem Otomatis", "Spesifikasi": "ATS, Anti Petir, Grounding", "Jumlah": "1 Paket"}]
    st.dataframe(pd.DataFrame(d_spec), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><h5>💰 Perkiraan Biaya & Untung</h5>', unsafe_allow_html=True)
    items = [{'item': f"Panel {wp_panel}Wp", 'qty': n_p, 'unit': 'Unit', 'price': wp_panel * PANEL_SPECS[p_type]['price_per_wp']}, {'item': "Baterai Cadangan", 'qty': d_bat['tot'], 'unit': 'Unit', 'price': (v_bat*ah_bat/1000)*BATTERY_SPECS[b_type]['price_per_kwh']}, {'item': f"Inverter {inv_cap:.1f}kW", 'qty': 1, 'unit': 'Unit', 'price': 8000000 + (inv_cap * 2000000)}, {'item': "Aksesoris & ATS", 'qty': 1, 'unit': 'Lot', 'price': 3500000}, {'item': "Pasang Lengkap", 'qty': 1, 'unit': 'Lot', 'price': 5000000}]
    df, tot_rab, l, v = generate_rab(items)
    c1, c2 = st.columns([2, 1])
    with c1: st.table(df)
    with c2: st.pyplot(plot_rab_pie(l, v))
    display_roi_analysis(tot_rab, (tot_wp * h_sun * 0.85 * 365 / 1000) * trf, "Hybrid")
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("Kalkulator PLTS Pro V7.3 - Edisi Rekomendasi Pintar")