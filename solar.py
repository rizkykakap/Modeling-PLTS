import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Kalkulator Solar System Pro V6.3",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS CUSTOM ---
st.markdown("""
<style>
    .header-style { font-size:26px; font-weight: bold; color: #1565C0; margin-bottom: 5px; border-left: 5px solid #1565C0; padding-left: 10px; }
    .sub-header { font-size:18px; font-weight: bold; color: #424242; margin-top: 20px; margin-bottom: 10px; background-color: #f0f2f6; padding: 5px 10px; border-radius: 5px;}
    .pros-box { background-color: #E8F5E9; padding: 10px; border-radius: 5px; border-left: 3px solid #43A047; font-size: 14px; margin-bottom: 5px; }
    .cons-box { background-color: #FFEBEE; padding: 10px; border-radius: 5px; border-left: 3px solid #E53935; font-size: 14px; margin-bottom: 5px; }
    .component-box { background-color: #FFF3E0; padding: 10px; border-radius: 5px; border: 1px solid #FFB74D; font-size: 13px; margin-top: 5px;}
    .roi-box { background-color: #E3F2FD; padding: 15px; border-radius: 8px; border: 1px solid #2196F3; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE & KONSTANTA
# ==========================================
# Data Tarif PLN (Estimasi per 2025/2026)
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
        "pros": ["Efisiensi tinggi (s/d 22%)", "Performa baik saat mendung/teduh", "Hemat tempat (densitas daya tinggi)"],
        "cons": ["Harga investasi sedikit lebih tinggi dibanding Poly"]
    },
    "Polycrystalline (Standard)": {
        "min_wp": 50, "max_wp": 360, "default_wp": 250, "price_per_wp": 2600,
        "pros": ["Harga per panel lebih ekonomis", "Tahan panas berlebih (koefisien suhu baik)"],
        "cons": ["Butuh area atap lebih luas", "Teknologi lama, efisiensi lebih rendah"]
    }
}

BATTERY_SPECS = {
    "Lead Acid / VRLA / Gel / Deep Cycle": {
        "dod": 0.50, "default_v": 12.0, "price_per_kwh": 2500000,
        "min_ah": 7, "max_ah": 250, "default_ah": 100, 
        "pros": ["Biaya awal paling murah", "Teknologi matang & mudah didapat", "Aman (tidak mudah terbakar)"],
        "cons": ["Umur pendek (1-2 thn ganti)", "Sangat berat", "Hanya boleh dipakai 50% (DoD)"]
    },
    "Lithium LiFePO4 (3.2V Prismatic)": {
        "dod": 0.90, "default_v": 3.2, "price_per_kwh": 4800000,
        "min_ah": 25, "max_ah": 320, "default_ah": 100, 
        "pros": ["Umur sangat panjang (7-10 thn)", "Sangat Aman & Stabil", "Bisa dipakai sampai 90% (DoD)"],
        "cons": ["Investasi awal cukup mahal", "Membutuhkan BMS (Battery Management System)"]
    },
    "Lithium Ion / NMC (3.7V)": {
        "dod": 0.85, "default_v": 3.7, "price_per_kwh": 4200000,
        "min_ah": 2, "max_ah": 200, "default_ah": 50,
        "pros": ["Densitas energi tertinggi (Kecil tapi kuat)", "Ringan & Kompak", "Populer untuk kendaraan listrik"],
        "cons": ["Sensitif suhu panas", "Resiko thermal runaway (terbakar) lebih tinggi"]
    },
}

SYSTEM_META = {
    "DC": {"pros": ["Efisiensi Tertinggi (Tanpa Inverter)", "Biaya Termurah"], "cons": ["Hanya bisa menyalakan alat DC 12/24V", "Kabel harus tebal (Losses tinggi)"]},
    "On-Grid": {"pros": ["Termurah per Watt", "Tanpa Baterai (Bebas Perawatan)", "ROI Tercepat (Paling Hemat)"], "cons": ["Mati total saat PLN padam (Anti-Islanding)", "Wajib Izin/Net Metering PLN"]},
    "Off-Grid": {"pros": ["Mandiri Energi 100%", "Bisa dipasang di pelosok (Tanpa PLN)"], "cons": ["Biaya Mahal (Investasi Baterai)", "Baterai perlu diganti berkala"]},
    "Hybrid": {"pros": ["Hemat Tagihan + Backup saat mati lampu", "Fitur Paling Lengkap & Canggih"], "cons": ["Biaya Paling Mahal (Inverter Hybrid + Baterai)", "Sistem Kompleks"]}
}

VOLTAGE_OPTIONS = [2.0, 3.2, 3.7, 12.0, 24.0, 48.0]

# ==========================================
# FUNGSI BANTUAN
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
            "Volume": i['qty'],
            "Satuan": i['unit'],
            "Harga Satuan": format_rupiah(i['price']),
            "Total Harga": format_rupiah(subtotal)
        })
        short_label = i['item'].split(' ')[0]
        if "Kabel" in i['item'] or "Mounting" in i['item'] or "Proteksi" in i['item']:
            short_label = "Aksesoris"
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
    ax.pie(df_chart['value'], labels=df_chart['label'], autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    ax.axis('equal') 
    plt.tight_layout()
    return fig

def display_roi_analysis(total_invest, yearly_savings_potential, system_type):
    # UPDATE: Mengurangi persentase maintenance agar perhitungan ROI lebih realistis
    # On-Grid minim perawatan (0.5%), Baterai butuh sinking fund (1%)
    maint_percent = 0.005 
    if "Battery" in system_type: 
        maint_percent = 0.015 
    
    yearly_maintenance = total_invest * maint_percent
    net_savings = yearly_savings_potential - yearly_maintenance
    
    if net_savings <= 0:
        roi_years = 999
        roi_text = "Tidak Balik Modal"
    else:
        roi_years = total_invest / net_savings
        roi_text = f"{roi_years:.1f} Tahun"

    st.markdown("<div class='sub-header'>📊 Analisis Balik Modal (ROI)</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.metric("Total Investasi", format_rupiah(total_invest))
        st.metric("Estimasi ROI", roi_text, delta_color="normal", help="Estimasi waktu yang dibutuhkan agar penghematan listrik menutup biaya modal.")
    
    with col2:
        st.write("**Cashflow Tahunan:**")
        st.caption(f"➕ Hemat Listrik: {format_rupiah(yearly_savings_potential)} /thn")
        st.caption(f"➖ Dana Perawatan (Est): {format_rupiah(yearly_maintenance)} /thn")
        st.markdown("---")
        st.write(f"**💰 Net Benefit: {format_rupiah(net_savings)} /thn**")

def display_pros_cons_system(sys_type):
    data = SYSTEM_META[sys_type]
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='pros-box'>✅ <b>KELEBIHAN SISTEM {sys_type.upper()}:</b><br>{'<br>'.join(['• '+x for x in data['pros']])}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='cons-box'>⚠️ <b>KEKURANGAN SISTEM {sys_type.upper()}:</b><br>{'<br>'.join(['• '+x for x in data['cons']])}</div>", unsafe_allow_html=True)

# FUNGSI BARU: Menampilkan Pros/Cons Komponen Terpilih
def display_component_analysis(panel_type, bat_type=None):
    st.markdown("##### 🔍 Analisis Komponen Terpilih")
    c1, c2 = st.columns(2)
    
    # Panel Analysis
    p_data = PANEL_SPECS[panel_type]
    with c1:
        html_panel = f"<b>PANEL: {panel_type}</b><br>"
        html_panel += "<i>Kelebihan:</i><br>" + "<br>".join([f"+ {x}" for x in p_data['pros']]) + "<br>"
        html_panel += "<i>Kekurangan:</i><br>" + "<br>".join([f"- {x}" for x in p_data['cons']])
        st.markdown(f"<div class='component-box'>{html_panel}</div>", unsafe_allow_html=True)
    
    # Battery Analysis (If exists)
    if bat_type:
        b_data = BATTERY_SPECS[bat_type]
        with c2:
            html_bat = f"<b>BATERAI: {bat_type}</b><br>"
            html_bat += "<i>Kelebihan:</i><br>" + "<br>".join([f"+ {x}" for x in b_data['pros']]) + "<br>"
            html_bat += "<i>Kekurangan:</i><br>" + "<br>".join([f"- {x}" for x in b_data['cons']])
            st.markdown(f"<div class='component-box'>{html_bat}</div>", unsafe_allow_html=True)
    else:
        with c2:
             st.markdown(f"<div class='component-box' style='background-color:#f0f0f0; border-color:#ccc;'><b>BATERAI: Tidak Ada</b><br>Sistem On-Grid tidak menggunakan baterai.</div>", unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.title("🎛️ Parameter Input")

st.sidebar.markdown("### 1️⃣ Profil Listrik")
# UPDATE: Mengganti input manual tarif dengan Golongan Daya
metode_hitung = st.sidebar.radio("Dasar Perhitungan:", ["Tagihan Listrik (Estimasi)", "Manual (Watt & Jam)"])
golongan_daya = st.sidebar.selectbox("Golongan Daya PLN:", list(TARIF_PLN.keys()), index=1)

# Set Harga per kWh berdasarkan golongan
if golongan_daya == "Manual Input":
    harga_per_kwh = st.sidebar.number_input("Input Tarif per kWh (Rp)", 100.0, 5000.0, 1444.70, step=50.0)
else:
    harga_per_kwh = TARIF_PLN[golongan_daya]
    st.sidebar.caption(f"⚡ Tarif: {format_rupiah(harga_per_kwh)} /kWh")

wh_harian_ac = 0
total_watt_manual = 0
estimated_bill_saving = 0

if metode_hitung == "Tagihan Listrik (Estimasi)":
    biaya_bulanan = st.sidebar.number_input("Rata2 Tagihan Listrik (Rp)", 50000, 100000000, 500000, step=50000)
    kwh_bulanan = biaya_bulanan / harga_per_kwh
    wh_harian_ac = (kwh_bulanan / 30) * 1000
    estimated_bill_saving = biaya_bulanan 
    st.sidebar.info(f"⚡ Beban Harian: **{wh_harian_ac:,.0f} Wh**")
else:
    total_watt_manual = st.sidebar.number_input("Total Daya Alat (Watt)", 1, 50000, 100)
    jam_nyala_manual = st.sidebar.number_input("Durasi Nyala (Jam/hari)", 1, 24, 12)
    wh_harian_ac = total_watt_manual * jam_nyala_manual
    estimated_bill_saving = (wh_harian_ac/1000) * 30 * harga_per_kwh
    st.sidebar.info(f"⚡ Beban Harian: **{wh_harian_ac:,.0f} Wh**")

st.sidebar.markdown("---")

st.sidebar.markdown("### 2️⃣ Komponen")
# Panel Logic
jenis_panel = st.sidebar.selectbox("Jenis Panel Surya", list(PANEL_SPECS.keys()))
p_specs = PANEL_SPECS[jenis_panel]
watt_panel_pilihan = st.sidebar.number_input(
    f"Kapasitas per Panel ({p_specs['min_wp']}-{p_specs['max_wp']} Wp)", 
    min_value=p_specs['min_wp'], 
    max_value=p_specs['max_wp'], 
    value=p_specs['default_wp'],
    step=10
)

# Battery Logic
jenis_baterai = st.sidebar.selectbox("Jenis Baterai", list(BATTERY_SPECS.keys()))
b_specs = BATTERY_SPECS[jenis_baterai]
default_volt_bat = b_specs["default_v"]

try: idx_def = VOLTAGE_OPTIONS.index(default_volt_bat)
except: idx_def = 3 
volt_baterai_unit = st.sidebar.selectbox("Voltase per Unit/Cell (V)", VOLTAGE_OPTIONS, index=idx_def)

kapasitas_baterai_unit = st.sidebar.number_input(
    f"Kapasitas per Unit ({b_specs['min_ah']}-{b_specs['max_ah']} Ah)", 
    min_value=b_specs['min_ah'], 
    max_value=b_specs['max_ah'], 
    value=b_specs['default_ah'],
    step=5
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 3️⃣ Parameter Sistem")
hari_efektif = st.sidebar.number_input("Sun Hours (Jam/Hari)", 2.0, 8.0, 3.5, help="Rata-rata jam efektif matahari di Indonesia (3.5 - 4.5 jam)")
hari_otonomi = st.sidebar.number_input("Cadangan Mendung (Hari)", 1, 5, 1, help="Berapa hari sistem baterai bertahan tanpa matahari")

saran_volt = 12
if wh_harian_ac > 5000: saran_volt = 48
elif wh_harian_ac > 1500: saran_volt = 24
volt_sistem = st.sidebar.selectbox("Voltase Sistem Total (V)", [12, 24, 48], index=[12, 24, 48].index(saran_volt))

# ==========================================
# LOGIKA HITUNGAN
# ==========================================
dod_pilihan = BATTERY_SPECS[jenis_baterai]["dod"]

def hitung_baterai_detail(total_wh_needed):
    wh_kapasitas_real = total_wh_needed * hari_otonomi / dod_pilihan
    ah_total_sistem = wh_kapasitas_real / volt_sistem
    butuh_seri = np.ceil(volt_sistem / volt_baterai_unit)
    butuh_paralel = np.ceil(ah_total_sistem / kapasitas_baterai_unit)
    total_unit = butuh_seri * butuh_paralel
    
    kwh_real = (total_unit * volt_baterai_unit * kapasitas_baterai_unit) / 1000
    
    return {
        "seri": int(butuh_seri),
        "paralel": int(butuh_paralel),
        "total_unit": int(total_unit),
        "volt_real_pack": butuh_seri * volt_baterai_unit,
        "ah_total_sistem": butuh_paralel * kapasitas_baterai_unit,
        "kwh_total": kwh_real
    }

def hitung_panel(target_wp):
    jml_panel = np.ceil(target_wp / watt_panel_pilihan)
    return int(jml_panel), int(jml_panel * watt_panel_pilihan)

# ==========================================
# HALAMAN UTAMA
# ==========================================
st.title("⚡ Kalkulator PLTS Pro V6.3")
st.caption("Solusi Perhitungan PLTS: Akurat, Detail, & Analisis ROI.")

# TABS
tab_dc, tab_on, tab_off, tab_hyb = st.tabs([
    "💡 DC SYSTEM", 
    "🏠 ON-GRID", 
    "🔋 OFF-GRID", 
    "🔄 HYBRID"
])

# ==============================================================================
# TAB 1: DC SYSTEM
# ==============================================================================
with tab_dc:
    eff_dc = 0.85
    wh_load_dc = wh_harian_ac / eff_dc
    wp_req_dc = wh_load_dc / hari_efektif
    
    qty_panel_dc, total_wp_dc = hitung_panel(wp_req_dc)
    bat_dc = hitung_baterai_detail(wh_load_dc)
    scc_amp = (total_wp_dc / volt_sistem) * 1.25

    st.markdown(f"<div class='header-style'>Kapasitas: {total_wp_dc} Wp ({total_wp_dc/1000:.2f} kWp)</div>", unsafe_allow_html=True)
    
    display_pros_cons_system("DC")
    # NEW: Menampilkan analisis komponen
    display_component_analysis(jenis_panel, jenis_baterai)

    st.markdown("### 📋 Rincian Komponen & Spesifikasi Detail")
    data_dc = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{jenis_panel} {watt_panel_pilihan}Wp", "Jumlah": f"{qty_panel_dc} Unit"},
        {"Komponen": "Baterai Utama", "Spesifikasi": f"{jenis_baterai} - {volt_baterai_unit}V {kapasitas_baterai_unit}Ah", "Jumlah": f"{bat_dc['total_unit']} Unit"},
        {"Komponen": "Konfigurasi Baterai", "Spesifikasi": f"Rangkaian {bat_dc['seri']} Seri x {bat_dc['paralel']} Paralel", "Jumlah": "1 Set"},
        {"Komponen": "Solar Charge Controller", "Spesifikasi": f"MPPT Controller {int(scc_amp)}A (Min {volt_sistem}V)", "Jumlah": "1 Unit"},
        {"Komponen": "Kabel & Safety", "Spesifikasi": "Kabel PV 4mm/6mm, MCB DC, Box Panel", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(data_dc), use_container_width=True, hide_index=True)

    # RAB UPDATE
    st.markdown("<div class='sub-header'>💰 RAB & ROI</div>", unsafe_allow_html=True)
    items_dc = [
        {'item': f"Panel Surya {watt_panel_pilihan}Wp", 'qty': qty_panel_dc, 'unit': 'Unit', 'price': watt_panel_pilihan * PANEL_SPECS[jenis_panel]['price_per_wp']},
        {'item': f"Baterai {kapasitas_baterai_unit}Ah", 'qty': bat_dc['total_unit'], 'unit': 'Unit', 'price': (volt_baterai_unit * kapasitas_baterai_unit / 1000) * BATTERY_SPECS[jenis_baterai]['price_per_kwh']},
        {'item': f"SCC MPPT {int(scc_amp)}A", 'qty': 1, 'unit': 'Unit', 'price': 850000 + (scc_amp*15000)},
        {'item': "Kabel PV & Aksesoris DC", 'qty': 1, 'unit': 'Lot', 'price': 500000 + (qty_panel_dc * 100000)},
        {'item': "Jasa Rakit & Instalasi", 'qty': 1, 'unit': 'Lot', 'price': 1500000}
    ]
    df_rab_dc, total_rab_dc, l_dc, v_dc = generate_rab(items_dc)
    
    rc1, rc2 = st.columns([2, 1])
    with rc1: st.table(df_rab_dc)
    with rc2: st.pyplot(plot_rab_pie(l_dc, v_dc))
    
    savings_dc = estimated_bill_saving * 12
    display_roi_analysis(total_rab_dc, savings_dc, "DC Battery")

# ==============================================================================
# TAB 2: ON-GRID
# ==============================================================================
with tab_on:
    eff_on = 0.90
    wp_req_on = wh_harian_ac / (hari_efektif * eff_on)
    qty_panel_on, total_wp_on = hitung_panel(wp_req_on)
    inv_cap_on = total_wp_on / 1000
    
    annual_kwh_prod = (total_wp_on * hari_efektif * 0.85 * 365) / 1000
    # ROI Logic Fix: Hemat tidak bisa lebih besar dari tagihan (kecuali ekspor diperhitungkan, anggap net metering)
    annual_savings = annual_kwh_prod * harga_per_kwh 

    st.markdown(f"<div class='header-style'>Kapasitas: {total_wp_on} Wp ({total_wp_on/1000:.2f} kWp)</div>", unsafe_allow_html=True)
    
    display_pros_cons_system("On-Grid")
    # NEW: Menampilkan analisis komponen (Tanpa Baterai)
    display_component_analysis(jenis_panel, None)

    st.markdown("### 📋 Rincian Komponen & Spesifikasi Detail")
    data_on = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{jenis_panel} - {watt_panel_pilihan} Wp", "Jumlah": f"{qty_panel_on} Unit"},
        {"Komponen": "Inverter", "Spesifikasi": f"Grid-Tie Inverter {inv_cap_on:.1f} kW (Pure Sine Wave)", "Jumlah": "1 Unit"},
        {"Komponen": "Mounting System", "Spesifikasi": "Rail Aluminium, Mid/End Clamp, Hook Tile/Tin", "Jumlah": f"{qty_panel_on} Set"},
        {"Komponen": "Proteksi & Kabel", "Spesifikasi": "PV Cable, AC/DC Combiner Box (SPD, MCB)", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(data_on), use_container_width=True, hide_index=True)

    st.markdown("<div class='sub-header'>💰 RAB & ROI</div>", unsafe_allow_html=True)
    items_on = [
        {'item': f"Panel Surya {watt_panel_pilihan}Wp", 'qty': qty_panel_on, 'unit': 'Unit', 'price': watt_panel_pilihan * PANEL_SPECS[jenis_panel]['price_per_wp']},
        {'item': f"Inverter Grid-Tie {inv_cap_on:.1f}kW", 'qty': 1, 'unit': 'Unit', 'price': 3000000 * (inv_cap_on if inv_cap_on > 1 else 1)},
        {'item': "Mounting Kit (Rail & Clamp)", 'qty': qty_panel_on, 'unit': 'Set', 'price': 175000},
        {'item': "Panel Proteksi (AC/DC Box Complete)", 'qty': 1, 'unit': 'Lot', 'price': 2000000 + (inv_cap_on * 100000)},
        {'item': "Kabel PV, Konektor & Grounding", 'qty': 1, 'unit': 'Lot', 'price': 1500000 + (qty_panel_on * 50000)},
        {'item': "Instalasi, Setting & SLO", 'qty': 1, 'unit': 'Ls', 'price': 3500000}
    ]
    df_rab_on, total_rab_on, l_on, v_on = generate_rab(items_on)
    
    rc1, rc2 = st.columns([2, 1])
    with rc1: st.table(df_rab_on)
    with rc2: st.pyplot(plot_rab_pie(l_on, v_on))

    display_roi_analysis(total_rab_on, annual_savings, "On-Grid System")

# ==============================================================================
# TAB 3: OFF-GRID
# ==============================================================================
with tab_off:
    eff_off = 0.85
    wh_load_off = wh_harian_ac / eff_off
    wp_req_off = wh_load_off / hari_efektif
    
    qty_panel_off, total_wp_off = hitung_panel(wp_req_off)
    bat_off = hitung_baterai_detail(wh_load_off)
    # Kapasitas Inverter min 1.5x load running atau manual input
    inv_watt_off_fix = (total_watt_manual if total_watt_manual > 0 else (wh_harian_ac/10)) * 2 
    if inv_watt_off_fix < 1000: inv_watt_off_fix = 1000

    st.markdown(f"<div class='header-style'>Kapasitas: {total_wp_off} Wp ({total_wp_off/1000:.2f} kWp)</div>", unsafe_allow_html=True)
    
    display_pros_cons_system("Off-Grid")
    # NEW: Menampilkan analisis komponen
    display_component_analysis(jenis_panel, jenis_baterai)

    st.markdown("### 📋 Rincian Komponen & Spesifikasi Detail")
    data_off = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{jenis_panel} {watt_panel_pilihan} Wp", "Jumlah": f"{qty_panel_off} Unit"},
        {"Komponen": "Baterai Bank", "Spesifikasi": f"{jenis_baterai} {bat_off['kwh_total']:.1f} kWh ({bat_off['total_unit']} unit)", "Jumlah": "1 Set"},
        {"Komponen": "Inverter Off-Grid", "Spesifikasi": f"Pure Sine Wave {int(inv_watt_off_fix)}W (Surge 2x)", "Jumlah": "1 Unit"},
        {"Komponen": "Balance of System", "Spesifikasi": "Rak Baterai, Kabel NYAF, Mounting PV, Proteksi", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(data_off), use_container_width=True, hide_index=True)

    st.markdown("<div class='sub-header'>💰 RAB & ROI</div>", unsafe_allow_html=True)
    items_off = [
        {'item': f"Panel Surya {watt_panel_pilihan}Wp", 'qty': qty_panel_off, 'unit': 'Unit', 'price': watt_panel_pilihan * PANEL_SPECS[jenis_panel]['price_per_wp']},
        {'item': f"Baterai Bank ({bat_off['kwh_total']:.1f}kWh)", 'qty': bat_off['total_unit'], 'unit': 'Unit', 'price': (volt_baterai_unit * kapasitas_baterai_unit / 1000) * BATTERY_SPECS[jenis_baterai]['price_per_kwh']},
        {'item': f"Inverter Off-Grid {int(inv_watt_off_fix)}W + SCC", 'qty': 1, 'unit': 'Set', 'price': 3500000 + (inv_watt_off_fix * 1800)},
        {'item': "Mounting Kit Panel Surya", 'qty': qty_panel_off, 'unit': 'Set', 'price': 175000},
        {'item': "Panel Distribusi & Kabel Baterai", 'qty': 1, 'unit': 'Lot', 'price': 2500000},
        {'item': "Instalasi Sistem", 'qty': 1, 'unit': 'Ls', 'price': 3000000}
    ]
    df_rab_off, total_rab_off, l_off, v_off = generate_rab(items_off)
    
    rc1, rc2 = st.columns([2, 1])
    with rc1: st.table(df_rab_off)
    with rc2: st.pyplot(plot_rab_pie(l_off, v_off))
    
    savings_off = estimated_bill_saving * 12
    display_roi_analysis(total_rab_off, savings_off, "Off-Grid Battery")

# ==============================================================================
# TAB 4: HYBRID
# ==============================================================================
with tab_hyb:
    backup_ratio = 0.5
    wh_load_hyb = wh_harian_ac * backup_ratio
    wp_req_hyb = wh_harian_ac / (hari_efektif * 0.9)
    qty_panel_hyb, total_wp_hyb = hitung_panel(wp_req_hyb)
    bat_hyb = hitung_baterai_detail(wh_load_hyb)
    inv_cap_hyb = (total_wp_hyb / 1000) + 1

    st.markdown(f"<div class='header-style'>Kapasitas: {total_wp_hyb} Wp ({total_wp_hyb/1000:.2f} kWp)</div>", unsafe_allow_html=True)
    
    display_pros_cons_system("Hybrid")
    # NEW: Menampilkan analisis komponen
    display_component_analysis(jenis_panel, jenis_baterai)

    st.markdown("### 📋 Rincian Komponen & Spesifikasi Detail")
    data_hyb = [
        {"Komponen": "Panel Surya", "Spesifikasi": f"{jenis_panel} {watt_panel_pilihan} Wp", "Jumlah": f"{qty_panel_hyb} Unit"},
        {"Komponen": "Inverter Hybrid", "Spesifikasi": f"Hybrid Inverter {inv_cap_hyb:.1f} kW (On-Grid + Backup)", "Jumlah": "1 Unit"},
        {"Komponen": "Baterai Backup", "Spesifikasi": f"Bank {bat_hyb['kwh_total']:.1f} kWh ({jenis_baterai})", "Jumlah": f"{bat_hyb['total_unit']} Unit"},
        {"Komponen": "Sistem Proteksi", "Spesifikasi": "ATS/COS, Surge Protection, Grounding, Wifi Kit", "Jumlah": "1 Lot"}
    ]
    st.dataframe(pd.DataFrame(data_hyb), use_container_width=True, hide_index=True)

    st.markdown("<div class='sub-header'>💰 RAB & ROI</div>", unsafe_allow_html=True)
    items_hyb = [
        {'item': f"Panel Surya {watt_panel_pilihan}Wp", 'qty': qty_panel_hyb, 'unit': 'Unit', 'price': watt_panel_pilihan * PANEL_SPECS[jenis_panel]['price_per_wp']},
        {'item': f"Baterai Backup", 'qty': bat_hyb['total_unit'], 'unit': 'Unit', 'price': (volt_baterai_unit * kapasitas_baterai_unit / 1000) * BATTERY_SPECS[jenis_baterai]['price_per_kwh']},
        {'item': f"Inverter Hybrid {inv_cap_hyb:.1f}kW", 'qty': 1, 'unit': 'Unit', 'price': 7500000 * (inv_cap_hyb if inv_cap_hyb > 1 else 1)},
        {'item': "Mounting & Rak Baterai", 'qty': 1, 'unit': 'Lot', 'price': 1500000 + (qty_panel_hyb * 175000)},
        {'item': "Kabel, Proteksi, & ATS", 'qty': 1, 'unit': 'Lot', 'price': 3500000},
        {'item': "Instalasi Lengkap", 'qty': 1, 'unit': 'Ls', 'price': 5000000}
    ]
    df_rab_hyb, total_rab_hyb, l_hyb, v_hyb = generate_rab(items_hyb)
    
    rc1, rc2 = st.columns([2, 1])
    with rc1: st.table(df_rab_hyb)
    with rc2: st.pyplot(plot_rab_pie(l_hyb, v_hyb))

    annual_kwh_prod_hyb = (total_wp_hyb * hari_efektif * 0.85 * 365) / 1000
    annual_savings_hyb = annual_kwh_prod_hyb * harga_per_kwh
    display_roi_analysis(total_rab_hyb, annual_savings_hyb, "Hybrid System")

st.markdown("---")
st.caption("Kalkulator PLTS Pro V6.3 - Ultimate Edition")