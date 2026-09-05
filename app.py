import streamlit as st
# ==========================================
# NAMA BULAN HIJRIAH STANDAR KBBI
# ==========================================
HIJRI_INDO = {1:"Muharam",2:"Safar",3:"Rabiulawal",4:"Rabiulakhir",5:"Jumadilawal",6:"Jumadilakhir",7:"Rajab",8:"Syakban",9:"Ramadan",10:"Syawal",11:"Zulkaidah",12:"Zulhijah"}

def indo_hijri(obj):
    if isinstance(obj, dict):
        h = obj.get('hijri')
        if isinstance(h, dict) and isinstance(h.get('month'), dict) and 'number' in h['month']:
            try:
                h['month']['en'] = HIJRI_INDO[int(h['month']['number'])]
            except Exception:
                pass
        for v in obj.values():
            indo_hijri(v)
    elif isinstance(obj, list):
        for v in obj:
            indo_hijri(v)
    return obj

def get_json(url):
    return indo_hijri(requests.get(url, timeout=10).json())

from zoneinfo import ZoneInfo

def get_city_data(city, country, method=20):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method}"
    data = get_json(url)
    if data.get('code') == 200:
        try:
            tz = ZoneInfo(data['data']['meta']['timezone'])
            local_now = datetime.now(tz)
            api_date = datetime.strptime(data['data']['date']['gregorian']['date'], '%d-%m-%Y').date()
            if local_now.date() != api_date:
                url2 = f"http://api.aladhan.com/v1/timingsByCity/{local_now.strftime('%d-%m-%Y')}?city={city}&country={country}&method={method}"
                d2 = get_json(url2)
                if d2.get('code') == 200:
                    data = d2
        except Exception:
            pass
    return data
import requests
from datetime import datetime, timedelta
import calendar

# Konfigurasi halaman
st.set_page_config(page_title="Dasbor Kalender Taqwim", layout="wide", page_icon="🌍")

# ==========================================
# SISTEM TEMA (pilihan warna dashboard)
# ==========================================
THEMES = {
    "💜 Ungu (Default)": ("#667eea", "#764ba2"),
    "💚 Hijau Masjid": ("#11998e", "#0b6b4f"),
    "💙 Biru Samudra": ("#2193b0", "#123c63"),
    "🧡 Emas Royal": ("#f7971e", "#8a5a00"),
    "❤️ Merah Marun": ("#b31217", "#4a0a0a"),
    "🖤 Gelap Malam": ("#232526", "#0f1011"),
}

if 'theme' not in st.session_state:
    st.session_state.theme = "💜 Ungu (Default)"
if 'theme_select' in st.session_state:
    st.session_state.theme = st.session_state.theme_select

tema_grad = THEMES.get(st.session_state.theme, THEMES["💜 Ungu (Default)"])

def easter_gregorian(year):
    a = year % 19
    b, c2 = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i2, k = divmod(c2, 4)
    l = (32 + 2 * e + 2 * i2 - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    bulan, hari = divmod(h + l - 7 * m + 114, 31)
    return datetime(year, bulan, hari + 1)

def hitung_libur_otomatis(year):
    try:
        from hijri_converter import Hijri
    except Exception:
        Hijri = None
    try:
        from lunardate import LunarDate
    except Exception:
        LunarDate = None
    lib = {
        "01-01": "Tahun Baru Masehi",
        "05-01": "Hari Buruh Internasional",
        "06-01": "Hari Lahir Pancasila",
        "08-17": "HUT Kemerdekaan RI",
        "12-25": "Hari Raya Natal",
    }
    ea = easter_gregorian(year)
    lib[(ea - timedelta(days=2)).strftime("%m-%d")] = "Wafat Isa Almasih"
    lib[(ea + timedelta(days=39)).strftime("%m-%d")] = "Kenaikan Isa Almasih"
    try:
        im = LunarDate(year, 1, 1).toSolarDate()
        lib[im.strftime("%m-%d")] = f"Tahun Baru Imlek {year + 551}"
    except Exception:
        pass
    for h in (year - 580, year - 579, year - 578):
        for hm, hd, fmt in [(7, 27, "Isra' Mi'raj Nabi Muhammad SAW {h} H"), (10, 1, "Idul Fitri {h} H"), (10, 2, "Idul Fitri {h} H (Hari 2)"), (12, 10, "Idul Adha {h} H"), (1, 1, "Tahun Baru Islam {h} H"), (3, 12, "Maulid Nabi Muhammad SAW {h} H")]:
            try:
                g = Hijri(h, hm, hd).to_gregorian()
            except Exception:
                continue
            if g.year == year:
                lib.setdefault(g.strftime("%m-%d"), fmt.format(h=h))
    return lib

def get_libur(year):
    lib = hitung_libur_otomatis(year)
    lib.update(LIBUR_NASIONAL.get(year, {}))
    cuti = dict(CUTI_BERSAMA.get(year, {}))
    return lib, cuti

HARI_INDO = {"Monday":"Senin","Tuesday":"Selasa","Wednesday":"Rabu","Thursday":"Kamis","Friday":"Jumat","Saturday":"Sabtu","Sunday":"Ahad"}
GREG_INDO = {"January":"Januari","February":"Februari","March":"Maret","April":"April","May":"Mei","June":"Juni","July":"Juli","August":"Agustus","September":"September","October":"Oktober","November":"November","December":"Desember"}

LIBUR_NASIONAL = {2026: {"01-01": "Tahun Baru Masehi", "01-16": "Isra' Mi'raj Nabi Muhammad SAW", "02-17": "Tahun Baru Imlek 2577", "03-19": "Hari Suci Nyepi 1948 Saka", "03-20": "Idul Fitri 1447 H", "03-21": "Idul Fitri 1447 H (Hari 2)", "04-03": "Wafat Isa Almasih", "05-01": "Hari Buruh Internasional", "05-14": "Kenaikan Isa Almasih", "05-27": "Idul Adha 1447 H", "05-31": "Hari Raya Waisak 2570", "06-01": "Hari Lahir Pancasila", "06-16": "Tahun Baru Islam 1448 H", "08-17": "HUT Kemerdekaan RI", "08-25": "Maulid Nabi Muhammad SAW", "12-25": "Hari Raya Natal"}}
CUTI_BERSAMA = {2026: {"02-16": "Cuti Bersama Imlek", "03-18": "Cuti Bersama Nyepi", "03-23": "Cuti Bersama Idul Fitri", "03-24": "Cuti Bersama Idul Fitri", "05-15": "Cuti Bersama Kenaikan Isa Almasih", "05-28": "Cuti Bersama Idul Adha", "12-24": "Cuti Bersama Natal"}}

TV_THEMES = {
    "gelap": ("#0f2027", "#203a43", "#2c5364"),
    "hijau": ("#06251a", "#0e4d33", "#17724c"),
    "marun": ("#200707", "#4a1010", "#6e1a1a"),
    "biru": ("#071a2e", "#123c63", "#1f5f8a"),
    "ungu": ("#1a1030", "#3a2f7d", "#5b4bb8"),
    "emas": ("#2a1a05", "#5a3a10", "#8a5a20"),
}

# CSS untuk membuat header sticky dan selalu terlihat
st.markdown(("""
<style>
header {visibility: hidden !important;}
.main-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: linear-gradient(135deg, GRAD1 0%, GRAD2 100%) !important;
    color: white !important;
    padding: 15px 20px 10px 20px !important;
    z-index: 99999 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    text-align: center !important;
}
.header-date { color: #fff; font-size: 1.25rem; margin-top: 4px; font-weight: 600; }
.main-header h1 {
    margin: 0 !important;
    font-size: 1.8rem !important;
    font-weight: bold !important;
    color: white !important;
    line-height: 1.2 !important;
}
.main > div:first-child {
    padding-top: 110px !important;
}
.block-container {
    padding-top: 110px !important;
}
.stApp > header {
    display: none !important;
}
body {
    overflow-x: hidden !important;
}

/* === TAMBAHKAN CSS JADWAL DI SINI === */
.jadwal-container {
    width: 100%;
    overflow-x: auto;
    padding: 10px 0;
}
.jadwal-grid {
    display: grid;
    grid-template-columns: repeat(10, minmax(80px, 1fr));
    gap: 8px;
    min-width: 900px;
}
.jadwal-item {
    background: linear-gradient(135deg, #f0f2f6 0%, #e8eaf6 100%);
    border-radius: 12px;
    padding: 12px 6px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    border: 1px solid #e0e0e0;
    transition: transform 0.2s;
}
.jadwal-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.jadwal-icon {
    font-size: clamp(1rem, 2.5vw, 1.8rem);
    margin-bottom: 4px;
}
.jadwal-label {
    font-size: clamp(0.55rem, 1.2vw, 0.85rem);
    color: #555;
    font-weight: 600;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.jadwal-time {
    font-size: clamp(0.9rem, 2vw, 1.5rem);
    font-weight: bold;
    color: #1a1a2e;
    font-family: 'Courier New', monospace;
}
.jadwal-item.highlight {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.jadwal-item.highlight .jadwal-label {
    color: rgba(255,255,255,0.95);
}
.jadwal-item.highlight .jadwal-time {
    color: white;
}
@media (max-width: 768px) {
    .jadwal-grid {
        grid-template-columns: repeat(5, minmax(70px, 1fr));
        min-width: 450px;
    }
}
/* === AKHIR CSS JADWAL === */
/* === PANEL KALENDER INDAH (semua jenis kalender) === */
.kal-panel { background: linear-gradient(135deg, #ffffff 0%, #f5f7ff 100%); border-radius: 16px; padding: clamp(10px, 1vw, 18px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); border: 1px solid #e3e6f0; }
.kal-table { width: 100%; table-layout: fixed; border-collapse: separate; border-spacing: clamp(6px, 0.7vw, 14px); font-family: 'Segoe UI', Tahoma, sans-serif; }
.kal-table th { background: linear-gradient(135deg, GRAD1 0%, GRAD2 100%); color: #fff; padding: 10px 4px; text-align: center; font-weight: 700; border-radius: 8px; font-size: clamp(11px, 1.2vw, 14px); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.kal-table th:nth-child(5) { background: linear-gradient(135deg, #11998e, #38ef7d) !important; }
.kal-table th:nth-child(6) { background: linear-gradient(135deg, #232526, #414345) !important; }
.kal-table th:nth-child(7) { background: linear-gradient(135deg, #cb2d3e, #ef473a) !important; }
.kal-table td { background: #fff; border: clamp(3px, 0.4vw, 6px) solid transparent; background-clip: padding-box; padding: 11px 4px; text-align: center; border-radius: 8px; color: #333; font-weight: 600; box-shadow: 0 1px 4px rgba(0,0,0,0.06); transition: transform .15s; }
.kal-table td:hover { transform: scale(1.06); }
.kal-table td:nth-child(-n+4) { background: linear-gradient(135deg, #4e54c8, #8f94fb); color: #fff; }
.kal-table td:nth-child(5) { background: linear-gradient(135deg, #11998e, #38ef7d); color: #fff; }
.kal-table td:nth-child(6) { background: linear-gradient(135deg, #232526, #414345); color: #fff; }
.kal-table td:nth-child(7) { background: linear-gradient(135deg, #cb2d3e, #ef473a); color: #fff; }
.kal-table td div { color: rgba(255,255,255,0.9) !important; }
.kal-table td.empty { background: transparent !important; box-shadow: none; }
.kal-table td.today { background: linear-gradient(135deg, #f7971e, #ffd200); color: #1a1a2e; font-weight: 800; box-shadow: 0 0 12px rgba(255,215,0,0.6); }
.kal-table td.libur { background: linear-gradient(135deg, #cb2d3e, #ef473a) !important; color: #fff !important; }
.kal-table td.cuti { background: linear-gradient(135deg, #f7971e, #ffd200) !important; color: #1a1a2e !important; }
.lib-name { font-size: 8px; line-height: 1.15; font-weight: 600; opacity: 0.95; }
/* === MODE COMPACT (muat satu layar) === */
.main h1 { font-size: 1.5rem !important; margin: 0.4rem 0 !important; }
.main h2 { font-size: 1.25rem !important; margin: 0.3rem 0 !important; }
.calendar-table th { padding: 6px !important; font-size: 13px !important; }
.calendar-table td { padding: 6px !important; font-size: 14px !important; }
.stButton > button { background: linear-gradient(135deg, GRAD1 0%, GRAD2 100%) !important; color: #fff !important; border: none !important; border-radius: 50% !important; width: 46px !important; height: 46px !important; padding: 0 !important; font-size: 1.15rem !important; font-weight: 800 !important; box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important; transition: transform .15s; }
.stButton > button:hover { transform: scale(1.1) !important; }
div[data-testid='stHorizontalBlock'] > div:last-child .stButton { display: flex !important; justify-content: flex-end !important; width: 100%; }

hr { margin: 0.5rem 0 !important; }
</style>
""").replace("GRAD1", tema_grad[0]).replace("GRAD2", tema_grad[1]), unsafe_allow_html=True)


# ==========================================
# MODE TV (UNTUK LAYAR MASJID)
# Akses: /?mode=tv&city=Jakarta&country=Indonesia&masjid=Al-Ikhlas
# ==========================================
mode = st.query_params.get("mode", "default")

if mode == "tv":
    tv_city = st.query_params.get("city", "Jakarta")
    tv_country = st.query_params.get("country", "Indonesia")
    tv_masjid = st.query_params.get("masjid", "Masjid Raya")
    tv_alamat = st.query_params.get("alamat", "")
    tv_kontak = st.query_params.get("kontak", "")
    tv_teks = st.query_params.get("teks", "")
    
    st.markdown("""<style>
html, body, .stApp { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%) !important; }
#MainMenu, header, footer { visibility: hidden !important; }
.main-header { display: none !important; }
.block-container { padding: 2vh 2vw !important; max-width: 100% !important; }
.tv-header { display:flex; justify-content:space-between; align-items:center; }
.tv-title { color:#ffd700; font-size:3.5vw; font-weight:800; }
.tv-clock { color:#fff; font-size:3.5vw; font-weight:800; font-family:monospace; }
.tv-dates { color:#cfe8ff; font-size:1.4vw; text-align:center; margin:1.5vh 0; }
.tv-grid { display:grid; grid-template-columns:repeat(10, 1fr); gap:1vw; margin-top:2vh; }
.tv-card { background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.15); border-radius:1vw; padding:2.5vh 0.5vw; text-align:center; }
.tv-card.next { background:linear-gradient(135deg,#f7971e,#ffd200); border-color:#ffd200; }
.tv-name { color:#ffd700; font-size:1.1vw; font-weight:700; }
.tv-card.next .tv-name { color:#1a1a2e; }
.tv-time { color:#fff; font-size:2vw; font-weight:800; font-family:monospace; }
.tv-card.next .tv-time { color:#1a1a2e; }
.tv-count { text-align:center; margin-top:3vh; color:#fff; font-size:2vw; }
.tv-count b { color:#ffd200; font-size:2.8vw; font-family:monospace; }
.tv-slogan { text-align:center; margin-top:2vh; color:#ffd700; font-size:clamp(12px, 1.7vw, 24px); font-weight:700; letter-spacing:2px; line-height:1.7; text-shadow:0 2px 8px rgba(0,0,0,0.5); }
</style>""", unsafe_allow_html=True)
    
    try:
        tv_method = st.query_params.get("method", "20")
        data = get_city_data(tv_city, tv_country, tv_method)
        
        if data['code'] == 200:
            timings = data['data']['timings']
            date_info = data['data']['date']
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(data['data']['meta']['timezone'])
            tz_name = data['data']['meta']['timezone']
            if tv_country.lower() == "indonesia" and ("Jakarta" in tz_name or "Pontianak" in tz_name):
                tz_label = "WIB"
            elif tv_country.lower() == "indonesia" and "Makassar" in tz_name:
                tz_label = "WITA"
            elif tv_country.lower() == "indonesia" and "Jayapura" in tz_name:
                tz_label = "WIT"
            else:
                tz_label = tz_name.split("/")[-1].replace("_", " ")
            
            daftar = [("Subuh", timings["Fajr"][:5]), ("Dzuhur", timings["Dhuhr"][:5]), ("Ashar", timings["Asr"][:5]), ("Maghrib", timings["Maghrib"][:5]), ("Isya", timings["Isha"][:5])]
            
            def cari_next(n):
                for nama, t in daftar:
                    jt = datetime.strptime(t, "%H:%M").replace(year=n.year, month=n.month, day=n.day, tzinfo=tz)
                    if jt > n:
                        return nama, jt
                return None, None
            
            next_name, next_time = cari_next(datetime.now(tz))
            
            @st.fragment(run_every=1)
            def tv_header():
                n = datetime.now(tz)
                st.markdown(f"<div class='tv-header'><div class='tv-title'>🕌 {tv_masjid}</div><div class='tv-clock'>🕐 {n.strftime('%H:%M:%S')} <span style='color:#ffd700;'>({tz_label})</span></div></div>", unsafe_allow_html=True)
            tv_header()
            
            hari_tv = HARI_INDO.get(date_info["gregorian"]["weekday"]["en"], "")
            bulan_m_tv = GREG_INDO.get(date_info["gregorian"]["month"]["en"], date_info["gregorian"]["month"]["en"])
            st.markdown(f"<div class='tv-dates'>📍 {tv_city}, {tv_country} &nbsp;•&nbsp; 🗓️ {hari_tv} &nbsp;•&nbsp; 📅 {date_info['gregorian']['day']} {bulan_m_tv} {date_info['gregorian']['year']} M &nbsp;•&nbsp; 🌙 {date_info['hijri']['day']} {date_info['hijri']['month']['en']} {date_info['hijri']['year']} H</div>", unsafe_allow_html=True)
            if tv_alamat or tv_kontak:
                extra = ""
                if tv_alamat:
                    extra += "📮 " + tv_alamat
                if tv_kontak:
                    extra += (" &nbsp;•&nbsp; " if extra else "") + "📞 " + tv_kontak
                st.markdown(f"<div class='tv-dates'>{extra}</div>", unsafe_allow_html=True)
            
            grid_items = [("Imsak", timings["Imsak"][:5]), ("Subuh", timings["Fajr"][:5]), ("Terbit", timings["Sunrise"][:5]), ("Dzuhur", timings["Dhuhr"][:5]), ("Ashar", timings["Asr"][:5]), ("Maghrib", timings["Maghrib"][:5]), ("Isya", timings["Isha"][:5]), ("1/3 Malam", timings["Firstthird"][:5]), ("Tengah Malam", timings["Midnight"][:5]), ("Akhir Malam", timings["Lastthird"][:5])]
            GAYA_KARTU = {"Imsak": ("🌑", "#0f2e2e", "#1f5f5f", "#fff"), "Subuh": ("🌅", "#4e54c8", "#8f94fb", "#fff"), "Terbit": ("🌄", "#f7971e", "#ffd200", "#1a1a2e"), "Dzuhur": ("☀️", "#2193b0", "#6dd5ed", "#fff"), "Ashar": ("⛅", "#f2994a", "#f2c94c", "#1a1a2e"), "Maghrib": ("🌆", "#8e2de2", "#c71f5e", "#fff"), "Isya": ("🌙", "#141e30", "#243b55", "#fff"), "1/3 Malam": ("🌌", "#1f1c4e", "#3a2f7d", "#fff"), "Tengah Malam": ("🕛", "#000000", "#434343", "#fff"), "Akhir Malam": ("✨", "#232526", "#414345", "#fff")}
            html = "<div class='tv-grid'>"
            for nama, t in grid_items:
                ikon, w1, w2, tk = GAYA_KARTU[nama]
                if nama == next_name:
                    html += f"<div style='background:linear-gradient(135deg,#f7971e,#ffd200);border-radius:0.8vw;padding:1.8vh 0.4vw;text-align:center;box-shadow:0 0 1.5vw rgba(255,215,0,0.6);'><div style='font-size:1.8vw;line-height:1;'>{ikon}</div><div style='color:#1a1a2e;font-size:1.1vw;font-weight:700;margin:0.6vh 0;'>{nama}</div><div style='color:#1a1a2e;font-size:2vw;font-weight:800;font-family:monospace;'>{t}</div></div>"
                else:
                    html += f"<div style='background:linear-gradient(135deg,{w1},{w2});border-radius:0.8vw;padding:1.8vh 0.4vw;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.35);'><div style='font-size:1.8vw;line-height:1;'>{ikon}</div><div style='color:{tk};font-size:1.1vw;font-weight:700;margin:0.6vh 0;'>{nama}</div><div style='color:{tk};font-size:2vw;font-weight:800;font-family:monospace;'>{t}</div></div>"
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
            
            @st.fragment(run_every=1)
            def tv_countdown():
                n = datetime.now(tz)
                nm, nt = cari_next(n)
                if nt:
                    total = int((nt - n).total_seconds())
                    h, m, s = total // 3600, (total % 3600) // 60, total % 60
                    st.markdown(f"<div class='tv-count'>⏳ Menuju waktu <b>{nm}</b> &nbsp; <b>{h:02d}:{m:02d}:{s:02d}</b></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='tv-count'>🌙 Menanti Subuh besok: <b>{daftar[0][1]}</b></div>", unsafe_allow_html=True)
            tv_countdown()
            pass
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
    
    # === RUNNING TEXT (ayat/hadits/pengumuman) ===
    tv_pesan = st.query_params.get("pesan", "")
    running_items = []
    if tv_pesan:
        running_items.append(tv_pesan)
    if tv_teks:
        running_items += [t for t in tv_teks.split("|") if t]
    if running_items:
        running_text = "☪️  " + "  ★  ".join(running_items) + "  ☪️  "
        marquee_css = "<style>.tv-marquee-wrap{margin-top:4vh;overflow:hidden;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);border-radius:1vw;padding:1.8vh 0;}.tv-marquee{display:inline-block;white-space:nowrap;padding-left:100%;animation:tv-scroll 60s linear infinite;color:#fff;font-size:1.8vw;}.ar{font-size:2.4vw;font-family:'Amiri','Scheherazade New','Traditional Arabic',serif;color:#ffd700;}@keyframes tv-scroll{0%{transform:translateX(0);}100%{transform:translateX(-100%);}}</style>"
        st.markdown(marquee_css + "<div class='tv-marquee-wrap'><div class='tv-marquee'>" + running_text + "</div></div>", unsafe_allow_html=True)
    tv_slogan = st.query_params.get("slogan", "Selamat Menunaikan Ibadah Sholat")
    _slog_lines = [t.strip()[:40] for t in tv_slogan.replace("|", "\n").split("\n") if t.strip()][:3]
    st.markdown("<div class='tv-slogan'>" + "<br>".join(_slog_lines) + "</div>", unsafe_allow_html=True)

    # === LATAR TV (Drive: gambar & video bisu+loop) ===
    tv_bg = st.query_params.get("bg", "")
    tv_jenis = st.query_params.get("jenis", "")
    drive_id = ""
    if "drive.google.com" in tv_bg:
        import re as _re
        m = _re.search(r"/d/([^/?]+)", tv_bg) or _re.search(r"id=([^&]+)", tv_bg)
        if m:
            drive_id = m.group(1)
            tv_bg = "https://lh3.googleusercontent.com/d/" + drive_id
    is_video = (tv_jenis == "video") or (tv_jenis != "gambar" and any(tv_bg.lower().endswith(e) for e in (".mp4", ".webm", ".ogg", ".mov", ".m4v")))
    bg_default = "background: linear-gradient(135deg, #064635 0%, #0a5c5c 50%, #123c63 100%) !important;"
    if tv_bg and is_video:
        if drive_id:
            video_html = "<video class='tv-bgvideo' autoplay muted loop playsinline><source src='https://drive.google.com/uc?export=download&id=" + drive_id + "' type='video/mp4'><source src='https://lh3.googleusercontent.com/d/" + drive_id + "' type='video/mp4'></video>"
        else:
            video_html = "<video class='tv-bgvideo' src='" + tv_bg + "' autoplay muted loop playsinline></video>"
        st.markdown("<style>html { background: linear-gradient(135deg, #064635 0%, #0a5c5c 50%, #123c63 100%) !important; } body, .stApp, .stAppViewContainer, [data-testid='stAppViewContainer'], [data-testid='stMainBlockContainer'], [data-testid='stAppViewBlockContainer'], section.main, .main, .block-container, header { background: transparent !important; background-color: transparent !important; } [data-testid='stComponentContainer'], [data-testid='stComponentContainer'] > div { position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; z-index: -1 !important; margin: 0 !important; } [data-testid='stComponentContainer'], [data-testid='stComponentContainer'] > div, [data-testid='stComponentContainer'] iframe { background: transparent !important; } [data-testid='stComponentContainer'] iframe { width: 100% !important; height: 100% !important; border: none !important; }</style>", unsafe_allow_html=True)
        st.components.v1.html("<style>html,body{margin:0;overflow:hidden;background:transparent;}video{position:fixed;top:0;left:0;width:100vw;height:100vh;object-fit:cover;filter:brightness(0.45);}</style>" + video_html + "<script>var v=document.querySelector('video');if(v){v.muted=true;v.defaultMuted=true;var tp=function(){v.play().catch(function(){});};v.addEventListener('loadeddata',tp);v.addEventListener('canplay',tp);tp();var lt=-1,st=0;setInterval(function(){if(v.currentTime===lt){st++;if(st>3){var s=v.querySelectorAll('source');if(s.length>1&&!v.dataset.sw){v.dataset.sw='1';v.src=s[1].src;v.load();}tp();}}else{st=0;}lt=v.currentTime;},1500);}</script>", height=10)
    elif tv_bg:
        bg_css = "background: linear-gradient(rgba(8,12,18,0.72), rgba(8,12,18,0.72)), url('" + tv_bg + "') center/cover no-repeat, linear-gradient(135deg, #064635 0%, #0a5c5c 50%, #123c63 100%) !important;"
        st.markdown("<style>html, body, .stApp { " + bg_css + " }</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>html, body, .stApp { " + bg_default + " }</style>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# DATABASE KOTA DUNIA
# ==========================================
WORLD_CITIES = {
    "Indonesia": [
        "Simeulue", "Aceh Singkil", "Aceh Selatan", "Aceh Tenggara", "Aceh Timur", "Aceh Tengah", "Aceh Barat", "Aceh Besar", "Pidie", "Bireuen", "Aceh Utara", "Aceh Barat Daya", "Gayo Lues", "Aceh Tamiang", "Nagan Raya", "Aceh Jaya", "Bener Meriah", "Pidie Jaya", "Banda Aceh", "Sabang", "Langsa", "Lhokseumawe", "Subulussalam",
        "Nias", "Mandailing Natal", "Tapanuli Selatan", "Tapanuli Tengah", "Tapanuli Utara", "Toba", "Labuhanbatu", "Asahan", "Simalungun", "Dairi", "Karo", "Deli Serdang", "Langkat", "Nias Selatan", "Humbang Hasundutan", "Pakpak Bharat", "Samosir", "Serdang Bedagai", "Batu Bara", "Padang Lawas Utara", "Padang Lawas", "Labuhanbatu Selatan", "Labuhanbatu Utara", "Nias Utara", "Nias Barat", "Sibolga", "Tanjungbalai", "Pematangsiantar", "Tebing Tinggi", "Medan", "Binjai", "Padangsidimpuan", "Gunungsitoli",
        "Kepulauan Mentawai", "Pesisir Selatan", "Solok", "Sijunjung", "Tanah Datar", "Padang Pariaman", "Agam", "Lima Puluh Kota", "Pasaman", "Dharmasraya", "Solok Selatan", "Pasaman Barat", "Padang", "Sawahlunto", "Padang Panjang", "Bukittinggi", "Payakumbuh", "Pariaman",
        "Kuantan Singingi", "Indragiri Hulu", "Indragiri Hilir", "Pelalawan", "Siak", "Kampar", "Rokan Hulu", "Bengkalis", "Rokan Hilir", "Kepulauan Meranti", "Pekanbaru", "Dumai",
        "Kerinci", "Merangin", "Sarolangun", "Batanghari", "Muaro Jambi", "Tanjung Jabung Timur", "Tanjung Jabung Barat", "Tebo", "Bungo", "Jambi", "Sungai Penuh",
        "Ogan Komering Ulu", "Ogan Komering Ilir", "Muara Enim", "Lahat", "Musi Rawas", "Musi Banyuasin", "Banyuasin", "Ogan Komering Ulu Selatan", "Ogan Komering Ulu Timur", "Ogan Ilir", "Empat Lawang", "Penukal Abab Lematang Ilir", "Musi Rawas Utara", "Palembang", "Prabumulih", "Pagar Alam", "Lubuklinggau",
        "Bengkulu Selatan", "Rejang Lebong", "Bengkulu Utara", "Kaur", "Seluma", "Mukomuko", "Lebong", "Kepahiang", "Bengkulu Tengah", "Bengkulu",
        "Lampung Barat", "Tanggamus", "Lampung Selatan", "Lampung Timur", "Lampung Tengah", "Lampung Utara", "Way Kanan", "Tulang Bawang", "Pesawaran", "Pringsewu", "Mesuji", "Tulang Bawang Barat", "Pesisir Barat", "Bandar Lampung", "Metro",
        "Bangka", "Belitung", "Bangka Barat", "Bangka Tengah", "Bangka Selatan", "Belitung Timur", "Pangkalpinang",
        "Karimun", "Bintan", "Natuna", "Lingga", "Kepulauan Anambas", "Batam", "Tanjungpinang",
        "Kepulauan Seribu", "Jakarta", "Jakarta Selatan", "Jakarta Timur", "Jakarta Pusat", "Jakarta Barat", "Jakarta Utara",
        "Bogor", "Sukabumi", "Cianjur", "Bandung", "Garut", "Tasikmalaya", "Ciamis", "Kuningan", "Cirebon", "Majalengka", "Sumedang", "Indramayu", "Subang", "Purwakarta", "Karawang", "Bekasi", "Bandung Barat", "Pangandaran", "Depok", "Cimahi", "Banjar",
        "Cilacap", "Banyumas", "Purbalingga", "Banjarnegara", "Kebumen", "Purworejo", "Wonosobo", "Magelang", "Boyolali", "Klaten", "Sukoharjo", "Wonogiri", "Karanganyar", "Sragen", "Grobogan", "Blora", "Rembang", "Pati", "Kudus", "Jepara", "Demak", "Semarang", "Temanggung", "Kendal", "Batang", "Pekalongan", "Pemalang", "Tegal", "Brebes", "Surakarta", "Salatiga",
        "Kulon Progo", "Bantul", "Gunungkidul", "Sleman", "Yogyakarta",
        "Pacitan", "Ponorogo", "Trenggalek", "Tulungagung", "Blitar", "Kediri", "Malang", "Lumajang", "Jember", "Banyuwangi", "Bondowoso", "Situbondo", "Probolinggo", "Pasuruan", "Sidoarjo", "Mojokerto", "Jombang", "Nganjuk", "Madiun", "Magetan", "Ngawi", "Bojonegoro", "Tuban", "Lamongan", "Gresik", "Bangkalan", "Sampang", "Pamekasan", "Sumenep", "Surabaya", "Batu",
        "Pandeglang", "Lebak", "Tangerang", "Serang", "Cilegon", "Tangerang Selatan",
        "Jembrana", "Tabanan", "Badung", "Gianyar", "Klungkung", "Bangli", "Karangasem", "Buleleng", "Denpasar",
        "Lombok Barat", "Lombok Tengah", "Lombok Timur", "Sumbawa", "Dompu", "Bima", "Sumbawa Barat", "Lombok Utara", "Mataram",
        "Sumba Barat", "Sumba Timur", "Kupang", "Timor Tengah Selatan", "Timor Tengah Utara", "Belu", "Alor", "Lembata", "Flores Timur", "Sikka", "Ende", "Ngada", "Manggarai", "Rote Ndao", "Manggarai Barat", "Sumba Tengah", "Sumba Barat Daya", "Nagekeo", "Manggarai Timur", "Sabu Raijua", "Malaka",
        "Sambas", "Bengkayang", "Landak", "Sintang", "Kapuas Hulu", "Sanggau", "Ketapang", "Sekadau", "Melawi", "Kayong Utara", "Kubu Raya", "Pontianak", "Singkawang",
        "Kotawaringin Barat", "Kotawaringin Timur", "Kapuas", "Barito Selatan", "Barito Utara", "Sukamara", "Lamandau", "Seruyan", "Katingan", "Pulang Pisau", "Gunung Mas", "Barito Timur", "Murung Raya", "Palangka Raya",
        "Tanah Laut", "Kota Baru", "Banjar", "Barito Kuala", "Tapin", "Hulu Sungai Selatan", "Hulu Sungai Tengah", "Hulu Sungai Utara", "Tabalong", "Tanah Bumbu", "Balangan", "Banjarmasin", "Banjarbaru",
        "Paser", "Kutai Barat", "Kutai Kartanegara", "Kutai Timur", "Berau", "Penajam Paser Utara", "Mahakam Ulu", "Balikpapan", "Samarinda", "Bontang",
        "Malinau", "Bulungan", "Tana Tidung", "Nunukan", "Tarakan",
        "Bolaang Mongondow", "Minahasa", "Kepulauan Sangihe", "Kepulauan Talaud", "Minahasa Selatan", "Minahasa Utara", "Bolaang Mongondow Utara", "Siau Tagulandang Biaro", "Minahasa Tenggara", "Bolaang Mongondow Selatan", "Bolaang Mongondow Timur", "Manado", "Bitung", "Tomohon", "Kotamobagu",
        "Banggai Kepulauan", "Banggai", "Morowali", "Poso", "Donggala", "Toli-Toli", "Buol", "Parigi Moutong", "Tojo Una-Una", "Sigi", "Banggai Laut", "Morowali Utara", "Palu",
        "Kepulauan Selayar", "Bulukumba", "Bantaeng", "Jeneponto", "Takalar", "Gowa", "Sinjai", "Maros", "Pangkajene Dan Kepulauan", "Barru", "Bone", "Soppeng", "Wajo", "Sidenreng Rappang", "Pinrang", "Enrekang", "Luwu", "Tana Toraja", "Luwu Utara", "Luwu Timur", "Toraja Utara", "Makassar", "Parepare", "Palopo",
        "Buton", "Muna", "Kendari", "Kolaka", "Konawe", "Konawe Selatan", "Bombana", "Wakatobi", "Kolaka Utara", "North Buton", "Konawe Utara", "Kolaka Timur", "Konawe Kepulauan", "Muna Barat", "Buton Tengah", "Buton Selatan", "Baubau",
        "Gorontalo", "Boalemo", "Bone Bolango", "Pohuwato", "Gorontalo Utara",
        "Majene", "Polewali Mandar", "Mamasa", "Mamuju", "Pasangkayu", "Mamuju Tengah",
        "Kepulauan Tanimbar", "Maluku Tenggara", "Maluku Tengah", "Buru", "Kepulauan Aru", "Seram Bagian Barat", "Seram Bagian Timur", "Maluku Barat Daya", "Buru Selatan", "Ambon", "Tual",
        "Halmahera Barat", "Halmahera Tengah", "Kepulauan Sula", "Halmahera Selatan", "Halmahera Utara", "Halmahera Timur", "Pulau Morotai", "Pulau Taliabu", "Ternate", "Tidore Kepulauan",
        "Jayapura", "Kepulauan Yapen", "Biak Numfor", "Sarmi", "Keerom", "Waropen", "Supiori", "Mamberamo Raya",
        "Manokwari", "Fakfak", "Teluk Bintuni", "Teluk Wondama", "Kaimana", "Manokwari Selatan", "Pegunungan Arfak",
        "Merauke", "Boven Digoel", "Mappi", "Asmat",
        "Nabire", "Puncak Jaya", "Paniai", "Mimika", "Puncak", "Dogiyai", "Intan Jaya", "Deiyai",
        "Jayawijaya", "Pegunungan Bintang", "Yahukimo", "Tolikara", "Lanny Jaya", "Mamberamo Tengah", "Nduga", "Yalimo",
        "Sorong", "Raja Ampat", "South Sorong", "Maybrat", "Tambrauw"
    ],
    "Malaysia": ["Kuala Lumpur", "George Town", "Johor Bahru", "Kota Kinabalu", "Kuching", "Ipoh", "Shah Alam", "Petaling Jaya"],
    "Singapore": ["Singapore"],
    "Brunei": ["Bandar Seri Begawan", "Kuala Belait", "Seria", "Tutong"],
    "Thailand": ["Bangkok", "Chiang Mai", "Phuket", "Pattaya", "Hat Yai", "Nakhon Ratchasima", "Khon Kaen"],
    "Vietnam": ["Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong", "Can Tho", "Nha Trang", "Hue"],
    "Philippines": ["Manila", "Quezon City", "Davao City", "Caloocan", "Cebu City", "Zamboanga City", "Taguig"],
    "Saudi Arabia": ["Makkah", "Madinah", "Riyadh", "Jeddah", "Dammam", "Khobar", "Taif", "Buraidah"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman"],
    "Qatar": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor"],
    "Kuwait": ["Kuwait City", "Al Ahmadi", "Hawalli", "Salmiya"],
    "Bahrain": ["Manama", "Riffa", "Muharraq", "Isa Town"],
    "Oman": ["Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Ibri"],
    "Yemen": ["Sanaa", "Aden", "Taiz", "Al Hudaydah", "Mukalla", "Ibb"],
    "Jordan": ["Amman", "Zarqa", "Irbid", "Aqaba", "Salt"],
    "Lebanon": ["Beirut", "Tripoli", "Sidon", "Tyre", "Nabatieh"],
    "Syria": ["Damascus", "Aleppo", "Homs", "Latakia", "Hama"],
    "Iraq": ["Baghdad", "Basra", "Mosul", "Erbil", "Najaf", "Karbala", "Sulaymaniyah"],
    "Palestine": ["Gaza", "Ramallah", "Nablus", "Hebron", "Jenin"],
    "Iran": ["Tehran", "Mashhad", "Isfahan", "Shiraz", "Tabriz", "Qom", "Ahvaz"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Gaziantep"],
    "Egypt": ["Cairo", "Alexandria", "Giza", "Luxor", "Aswan", "Port Said", "Suez"],
    "Nigeria": ["Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt", "Kaduna"],
    "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth"],
    "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"],
    "Ethiopia": ["Addis Ababa", "Dire Dawa", "Mekelle", "Gondar", "Hawassa"],
    "Tanzania": ["Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya"],
    "Uganda": ["Kampala", "Gulu", "Lira", "Mbarara", "Jinja"],
    "Ghana": ["Accra", "Kumasi", "Tamale", "Sekondi-Takoradi"],
    "Senegal": ["Dakar", "Touba", "Thies", "Kaolack"],
    "Mali": ["Bamako", "Sikasso", "Mopti", "Koutiala"],
    "Burkina Faso": ["Ouagadougou", "Bobo-Dioulasso", "Koudougou"],
    "Niger": ["Niamey", "Zinder", "Maradi", "Agadez"],
    "Chad": ["N'Djamena", "Moundou", "Sarh", "Abéché"],
    "Sudan": ["Khartoum", "Omdurman", "Port Sudan", "Kassala", "Nyala"],
    "Somalia": ["Mogadishu", "Hargeisa", "Bosaso", "Kismayo"],
    "Cameroon": ["Douala", "Yaoundé", "Bamenda", "Bafoussam"],
    "Ivory Coast": ["Abidjan", "Bouaké", "Daloa", "Yamoussoukro"],
    "Madagascar": ["Antananarivo", "Toamasina", "Antsirabe", "Fianarantsoa"],
    "Malawi": ["Lilongwe", "Blantyre", "Mzuzu", "Zomba"],
    "Zambia": ["Lusaka", "Kitwe", "Ndola", "Kabwe"],
    "Zimbabwe": ["Harare", "Bulawayo", "Chitungwiza", "Mutare"],
    "Mozambique": ["Maputo", "Matola", "Beira", "Nampula"],
    "Angola": ["Luanda", "Huambo", "Lobito", "Benguela"],
    "Botswana": ["Gaborone", "Francistown", "Molepolole"],
    "Namibia": ["Windhoek", "Rundu", "Walvis Bay", "Oshakati"],
    "Lesotho": ["Maseru", "Teyateyaneng", "Mafeteng"],
    "Rwanda": ["Kigali", "Butare", "Gitarama", "Ruhengeri"],
    "Burundi": ["Bujumbura", "Gitega", "Muyinga", "Ruyigi"],
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"],
    "Bangladesh": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna"],
    "Sri Lanka": ["Colombo", "Kandy", "Galle", "Jaffna", "Negombo"],
    "Maldives": ["Male", "Addu City", "Fuvahmulah"],
    "Nepal": ["Kathmandu", "Pokhara", "Lalitpur", "Bharatpur"],
    "Bhutan": ["Thimphu", "Phuntsholing", "Punakha", "Paro"],
    "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Hangzhou", "Wuhan", "Xi'an"],
    "Japan": ["Tokyo", "Yokohama", "Osaka", "Nagoya", "Sapporo", "Fukuoka", "Kobe", "Kyoto"],
    "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju"],
    "North Korea": ["Pyongyang", "Hamhung", "Chongjin", "Nampo"],
    "Taiwan": ["Taipei", "Kaohsiung", "Taichung", "Tainan"],
    "Hong Kong": ["Hong Kong", "Kowloon", "Tuen Mun"],
    "Macau": ["Macau", "Taipa", "Coloane"],
    "Mongolia": ["Ulaanbaatar", "Erdenet", "Darkhan", "Choibalsan"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Gold Coast"],
    "New Zealand": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Dunedin"],
    "Papua New Guinea": ["Port Moresby", "Lae", "Arawa", "Mount Hagen"],
    "Fiji": ["Suva", "Lautoka", "Nadi", "Labasa"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool", "Leeds", "Edinburgh"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes"],
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven"],
    "Belgium": ["Brussels", "Antwerp", "Ghent", "Bruges", "Liege"],
    "Switzerland": ["Zurich", "Geneva", "Basel", "Bern", "Lausanne", "Lucerne"],
    "Austria": ["Vienna", "Salzburg", "Innsbruck", "Graz", "Linz"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Florence", "Bologna", "Venice"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Malaga"],
    "Portugal": ["Lisbon", "Porto", "Faro", "Coimbra", "Braga"],
    "Greece": ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa"],
    "Russia": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan", "Nizhny Novgorod"],
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Francisco"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "Leon"],
    "Brazil": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza", "Belo Horizonte", "Manaus"],
    "Argentina": ["Buenos Aires", "Cordoba", "Rosario", "Mendoza", "La Plata", "San Miguel de Tucuman"],
    "Chile": ["Santiago", "Valparaiso", "Concepcion", "La Serena", "Antofagasta", "Temuco"],
    "Colombia": ["Bogota", "Medellin", "Cali", "Barranquilla", "Cartagena", "Cucuta"],
    "Peru": ["Lima", "Arequipa", "Trujillo", "Chiclayo", "Piura", "Cusco", "Iquitos"],
    "Venezuela": ["Caracas", "Maracaibo", "Valencia", "Barquisimeto", "Maracay"],
    "Ecuador": ["Quito", "Guayaquil", "Cuenca", "Santo Domingo", "Machala"],
    "Bolivia": ["La Paz", "Santa Cruz", "Cochabamba", "Sucre", "Oruro", "Tarija"],
    "Paraguay": ["Asuncion", "Ciudad del Este", "San Lorenzo", "Luque"],
    "Uruguay": ["Montevideo", "Salto", "Paysandu", "Las Piedras", "Rivera"]
}

# ==========================================
# BUAT ALL_CITIES
# ==========================================
ALL_CITIES = []
for country_name, cities in WORLD_CITIES.items():
    for city_name in cities:
        ALL_CITIES.append(f"{city_name}, {country_name}")
ALL_CITIES.sort()

# ==========================================
# INISIALISASI SESSION STATE (PENTING!)
# ==========================================
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year
if 'view_month' not in st.session_state:
    st.session_state.view_month = datetime.now().month
if 'city' not in st.session_state:
    st.session_state.city = "Jakarta"
if 'country' not in st.session_state:
    st.session_state.country = "Indonesia"
if 'method' not in st.session_state:
    st.session_state.method = (20, "Kemenag RI (Indonesia)")
if 'calendar_type' not in st.session_state:
    st.session_state.calendar_type = "Kalender Masehi"

# === SINKRONISASI OTOMATIS: bagian atas langsung ikut pengaturan terbaru ===
if 'city_select' in st.session_state:
    _loc = st.session_state.city_select
    st.session_state.city = _loc.split(", ")[0]
    st.session_state.country = _loc.split(", ")[1]

if 'method_select' in st.session_state:
    st.session_state.method = st.session_state.method_select

if 'cal_radio' in st.session_state:
    st.session_state.calendar_type = st.session_state.cal_radio

today = datetime.now()
hijri_pre = "-"
try:
    from zoneinfo import ZoneInfo as _ZoneInfo
    _method_no = st.session_state.method[0] if isinstance(st.session_state.method, tuple) else st.session_state.method
    _url = f"http://api.aladhan.com/v1/timingsByCity?city={st.session_state.city}&country={st.session_state.country}&method={_method_no}"
    _d = get_json(_url)

    if _d.get('code') == 200:
        _tz = _ZoneInfo(_d['data']['meta']['timezone'])
        _local_now = datetime.now(_tz)
        _api_date = datetime.strptime(_d['data']['date']['gregorian']['date'], '%d-%m-%Y').date()

        # Kalau tanggal API masih beda dengan tanggal lokal kota, ambil ulang tanggal lokal
        if _local_now.date() != _api_date:
            _url2 = f"http://api.aladhan.com/v1/timingsByCity/{_local_now.strftime('%d-%m-%Y')}?city={st.session_state.city}&country={st.session_state.country}&method={_method_no}"
            _d2 = get_json(_url2)
            if _d2.get('code') == 200:
                _d = _d2

        _g = _d['data']['date']['gregorian']
        today = datetime.strptime(_g['date'], '%d-%m-%Y')

        _h = _d['data']['date']['hijri']
        hijri_pre = f"{_h['day']} {_h['month']['en']} {_h['year']} H"
except Exception:
    pass


# HEADER DENGAN TANGGAL & LOKASI
# ==========================================
nama_hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]
nama_bulan = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

hijri_str = hijri_pre
hari_str = nama_hari[today.weekday()]
tgl_str = f"{today.day} {nama_bulan[today.month-1]} {today.year}"

st.markdown(f"""
<div class="main-header">
    <h1>🌍 Dasbor Kalender Taqwim</h1>
    <div class="header-date">{hari_str}, {tgl_str} M / {hijri_str} &nbsp;&nbsp; Lokasi : {st.session_state.city} {st.session_state.country}</div>
</div>
""", unsafe_allow_html=True)

# ============================================
# JADWAL SHOLAT (JUDUL KIRI + INFO KANAN)
# ============================================

col_kiri, col_kanan = st.columns([2, 3], gap="large")

with col_kiri:
    try:
        data = get_city_data(st.session_state.city, st.session_state.country, st.session_state.method[0])

        if data['code'] == 200:
            timings = data['data']['timings']
            date_info = data['data']['date']

            # === HEADER SEJAJAR: JUDUL KIRI + INFO KANAN (1 BARIS) ===
            st.markdown('<div style="font-size:1.6rem;font-weight:700;color:#1a1a2e;margin:8px 0;">🕌 Jadwal Sholat Hari Ini</div>', unsafe_allow_html=True)

            # === CSS KARTU (mulai kolom 0, jangan menjorok!) ===
            css_jadwal = """<style>
    .jadwal-wrapper{width:100%;overflow-x:auto;padding:10px 0;}
    .jadwal-row{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;}
    .jadwal-card{flex:1;min-width:90px;height:110px;border-radius:12px;padding:10px 6px;text-align:center;display:flex;flex-direction:column;justify-content:space-between;align-items:center;box-shadow:0 2px 8px rgba(0,0,0,0.08);border:1px solid #e0e0e0;transition:transform 0.2s;}
    .jadwal-card:hover{transform:translateY(-4px);box-shadow:0 6px 16px rgba(0,0,0,0.15);}
    .jadwal-card.regular{background:linear-gradient(135deg,#f0f2f6 0%,#e8eaf6 100%);}
    .jadwal-card.highlight{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);border-color:#5a67d8;}
    .jadwal-icon{font-size:1.5rem;line-height:1;}
    .jadwal-label{font-size:14px;font-weight:600;margin:4px 0;white-space:nowrap;}
    .jadwal-card.regular .jadwal-label{color:#555;}
    .jadwal-card.highlight .jadwal-label{color:rgba(255,255,255,0.95);}
    .jadwal-time{font-size:1.1rem;font-weight:bold;font-family:'Courier New',monospace;}
    .jadwal-card.regular .jadwal-time{color:#1a1a2e;}
    .jadwal-card.highlight .jadwal-time{color:white;}
    </style>"""
            st.markdown(css_jadwal, unsafe_allow_html=True)

                    # === DATA 10 WAKTU + WARNA PENCAHAYAAN ALAMI KHATULISTIWA ===
            # Format: (Nama, Icon, Waktu, WarnaAtas, WarnaBawah, WarnaTeks)
            def _hm(t):
                h, m = t.split(":")
                return int(h) * 60 + int(m)
            def _hm2(m):
                return f"{(m // 60) % 24:02d}:{m % 60:02d}"
            _sr = _hm(timings.get("Sunrise", "06:00")[:5])
            _ss = _hm(timings.get("Sunset", "18:00")[:5])
            dhuha_t = _hm2(_sr + 15)
            istiwa_t = _hm2(_hm(timings.get("Dhuhr", "12:00")[:5]) - 2)
            jadwal_data = [
                ("Imsak", "🌑", timings.get("Imsak", "-"), "#0f2027", "#2c5364", "#ffffff"),
                ("Subuh", "🌅", timings.get("Fajr", "-"), "#2b5876", "#4e4376", "#ffffff"),
                ("Terbit", "🌄", timings.get("Sunrise", "-"), "#f7971e", "#ffd200", "#1a1a2e"),
                ("Dhuha", "🌞", dhuha_t, "#FDC830", "#F37335", "#1a1a2e"),
                ("Istiwa", "🔆", istiwa_t, "#f83600", "#f9d423", "#1a1a2e"),
                ("Dzuhur", "☀️", timings.get("Dhuhr", "-"), "#2193b0", "#6dd5ed", "#ffffff"),
                ("Ashar", "🌤️", timings.get("Asr", "-"), "#f2994a", "#f2c94c", "#1a1a2e"),
                ("Maghrib", "🌇", timings.get("Maghrib", "-"), "#c33764", "#1d2671", "#ffffff"),
                ("Isya", "🌙", timings.get("Isha", "-"), "#141e30", "#243b55", "#ffffff"),
                ("1/3 Malam", "🌌", timings.get("Firstthird", "-"), "#0f0c29", "#302b63", "#ffffff"),
                ("Tengah Malam", "🕛", timings.get("Midnight", "-"), "#000000", "#434343", "#ffffff"),
                ("Akhir Malam", "✨", timings.get("Lastthird", "-"), "#232526", "#414345", "#ffffff"),
            ]

            # === HTML KARTU SATU BARIS (inline style warna alami) ===
            html_jadwal = '<div class="jadwal-wrapper"><div class="jadwal-row">'
            for nama, icon, waktu, c1, c2, tcolor in jadwal_data:
                html_jadwal += '<div style="flex:1;min-width:90px;height:110px;border-radius:12px;padding:10px 6px;text-align:center;display:flex;flex-direction:column;justify-content:space-between;align-items:center;box-shadow:0 3px 10px rgba(0,0,0,0.2);background:linear-gradient(135deg,' + c1 + ' 0%,' + c2 + ' 100%);"><div style="font-size:1.5rem;line-height:1;">' + icon + '</div><div style="font-size:14px;font-weight:600;margin:4px 0;white-space:nowrap;color:' + tcolor + ';">' + nama + '</div><div style="font-size:1.1rem;font-weight:bold;font-family:monospace;color:' + tcolor + ';">' + waktu + '</div></div>'
            html_jadwal += '</div></div>'

            st.markdown(html_jadwal, unsafe_allow_html=True)

            from zoneinfo import ZoneInfo as _ZI
            _tz = _ZI(data['data']['meta']['timezone'])
            _tzn = data['data']['meta']['timezone']
            if st.session_state.country.lower() == "indonesia" and ("Jakarta" in _tzn or "Pontianak" in _tzn):
                _tzl = "WIB"
            elif st.session_state.country.lower() == "indonesia" and "Makassar" in _tzn:
                _tzl = "WITA"
            elif st.session_state.country.lower() == "indonesia" and "Jayapura" in _tzn:
                _tzl = "WIT"
            else:
                _tzl = _tzn.split("/")[-1].replace("_", " ")
            _daftar5 = [("Subuh", timings["Fajr"][:5]), ("Dzuhur", timings["Dhuhr"][:5]), ("Ashar", timings["Asr"][:5]), ("Maghrib", timings["Maghrib"][:5]), ("Isya", timings["Isha"][:5])]

            @st.fragment(run_every=1)
            def dash_clock():
                n = datetime.now(_tz)
                nm_next = None
                t_next = None
                for nm, t in _daftar5:
                    jt = datetime.strptime(t, "%H:%M").replace(year=n.year, month=n.month, day=n.day, tzinfo=_tz)
                    if jt > n:
                        nm_next, t_next = nm, jt
                        break
                if t_next:
                    total = int((t_next - n).total_seconds())
                    h, m, s = total // 3600, (total % 3600) // 60, total % 60
                    cd = f"⏳ Menuju waktu <b>{nm_next}</b> &nbsp;<b>{h:02d}:{m:02d}:{s:02d}</b>"
                else:
                    cd = f"🌙 Menanti Subuh besok &nbsp;<b>{_daftar5[0][1]}</b>"
                st.markdown(f"<div style='text-align:center;margin-top:14px;'><div style='font-size:2.2rem;font-weight:800;font-family:monospace;color:#1a1a2e;'>🕐 {n.strftime('%H:%M:%S')} <span style='font-size:1.1rem;color:#764ba2;'>({_tzl})</span></div><div style='font-size:1.15rem;color:#444;margin-top:4px;'>{cd}</div></div>", unsafe_allow_html=True)
            dash_clock()
        else:
            st.subheader("🕌 Jadwal Sholat Hari Ini")
            st.error("❌ Kota tidak ditemukan di database API.")

    except requests.exceptions.Timeout:
        st.subheader("🕌 Jadwal Sholat Hari Ini")
        st.error("⏱️ Request timeout. Koneksi internet lambat.")
    except requests.exceptions.ConnectionError:
        st.subheader("🕌 Jadwal Sholat Hari Ini")
        st.error("🔌 Koneksi internet terputus.")
    except Exception as e:
        st.subheader("🕌 Jadwal Sholat Hari Ini")
        st.error(f"❌ Terjadi kesalahan: {str(e)}")

# ==========================================
# AMBIL NILAI DARI SESSION STATE (PASTI ADA!)
# ==========================================
calendar_type = st.session_state.calendar_type
city = st.session_state.city
country = st.session_state.country
method = st.session_state.method

# ==========================================
# FUNGSI-FUNGSI
# ==========================================
def prev_month():
    if st.session_state.view_month == 1:
        st.session_state.view_month = 12
        st.session_state.view_year -= 1
    else:
        st.session_state.view_month -= 1

def next_month():
    if st.session_state.view_month == 12:
        st.session_state.view_month = 1
        st.session_state.view_year += 1
    else:
        st.session_state.view_month += 1

def gregorian_to_persian(gy, gm, gd):
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + ((gy2 + 399) // 400) + gd + g_d_m[gm - 1]
    jy = -1595 + (33 * (days // 12053))
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd

def get_javanese_date(year, month, day):
    saka_year = year - 78
    bulan_jawa = ["Sura", "Sapar", "Mulud", "Bakda Mulud", "Jumadilawal", "Jumadilakhir", "Rejeb", "Ruwah", "Pasa", "Sawal", "Dulkaidah", "Besar"]
    ref_date = datetime(2024, 7, 17)
    current_date = datetime(year, month, day)
    days_diff = (current_date - ref_date).days
    total_days_from_ref = 1 + days_diff
    avg_days_per_month = 29.5
    months_from_ref = total_days_from_ref // avg_days_per_month
    remaining_days = total_days_from_ref % avg_days_per_month
    saka_month = int(months_from_ref) % 12
    saka_year_calc = 1956 + int(months_from_ref) // 12
    saka_day = int(remaining_days) + 1
    windu = ["Alip", "Ehe", "Jimawal", "Je", "Dal", "Be", "Wawu", "Jimakir"]
    windu_index = saka_year_calc % 8
    pasaran = ["Pon", "Wage", "Kliwon", "Legi", "Pahing"]
    ref_pasaran = datetime(2000, 1, 1)
    days_diff_pasaran = (current_date - ref_pasaran).days
    pasaran_index = (days_diff_pasaran + 3) % 5
    hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]
    return {
        'saka_year': saka_year_calc, 'saka_month': bulan_jawa[saka_month], 'saka_day': saka_day,
        'windu': windu[windu_index], 'pasaran': pasaran[pasaran_index],
        'hari': hari_indonesia[current_date.weekday()], 'weton': f"{hari_indonesia[current_date.weekday()]} {pasaran[pasaran_index]}"
    }

def get_chinese_date(year, month, day):
    shio = ["Tikus", "Kerbau", "Macan", "Kelinci", "Naga", "Ular", "Kuda", "Kambing", "Monyet", "Ayam", "Anjing", "Babi"]
    elemen = ["Kayu", "Api", "Tanah", "Logam", "Air"]
    shio_index = (year - 4) % 12
    elemen_index = (year - 4) % 10 // 2
    yin_yang = "Yang" if year % 2 == 0 else "Yin"
    return {'shio': shio[shio_index], 'elemen': elemen[elemen_index], 'yin_yang': yin_yang, 'tahun_cina': year - 2698}

persian_months = ["Farvardin", "Ordibehesht", "Khordad", "Tir", "Mordad", "Shahrivar", "Mehr", "Aban", "Azar", "Dey", "Bahman", "Esfand"]
hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]
bulan_indonesia = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def display_calendar(year, month, month_names, highlight_day=None):
    col_nav1, col_nav2, col_nav3 = st.columns([1, 12, 1])
    with col_nav1:
        if st.button("❮"):
            prev_month()
            st.rerun()
    with col_nav2:
        st.markdown(f"<h2 style='text-align: center;'> {month_names[month-1]} {year}</h2>", unsafe_allow_html=True)
    with col_nav3:
        if st.button("❯"):
            next_month()
            st.rerun()
    st.divider()
    cal = calendar.monthcalendar(year, month)
    header = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]
    calendar_css = """
    <style>
    .calendar-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px; }
    .calendar-table th { background-color: #f0f2f6; padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd; color: #333; }
    .calendar-table td { padding: 12px; text-align: center; border: 1px solid #ddd; color: #333; font-weight: 500; }
    .calendar-table td.empty { background-color: #fafafa; }
    </style>"""
    html_table = "<div class='kal-panel'><table class='kal-table'><thead><tr>"
    for day in header:
        html_table += f"<th>{day}</th>"
    html_table += "</tr></thead><tbody>"
    lib, cuti = get_libur(year)
    for week in cal:
        html_table += "<tr>"
        for day in week:
            key = f"{month:02d}-{day:02d}"
            if day == 0:
                html_table += "<td class='empty'></td>"
            elif highlight_day and day == highlight_day:
                html_table += f"<td class='today'>{day}</td>"
            elif key in lib:
                html_table += f"<td class='libur'>{day}<div class='lib-name'>{lib[key]}</div></td>"
            elif key in cuti:
                html_table += f"<td class='cuti'>{day}<div class='lib-name'>{cuti[key]}</div></td>"
            else:
                html_table += f"<td>{day}</td>"
        html_table += "</tr>"
    html_table += "</tbody></table></div>"
    st.markdown(html_table, unsafe_allow_html=True)

with col_kanan:
    # ============================================
    # KALENDER 1: MASEHI
    # ============================================
    if calendar_type == "Kalender Masehi":
        st.header("Kalender Masehi")
        display_calendar(st.session_state.view_year, st.session_state.view_month, bulan_indonesia, today.day if st.session_state.view_month == today.month and st.session_state.view_year == today.year else None)

    # ============================================
    # KALENDER 2: HIJRIAH QOMARIAH
    # ============================================
    elif calendar_type == "Kalender Hijriah Qomariah/Bulan":
        st.header("🌙 Kalender Hijriah Qomariah/Bulan")
    
        nama_bulan_hijriah = ["Muharram", "Safar", "Rabiul Awal", "Rabiul Akhir", "Jumadil Awal", "Jumadil Akhir", "Rajab", "Sya'ban", "Ramadhan", "Syawal", "Dzulqa'dah", "Dzulhijjah"]
    
        try:
            url = f"http://api.aladhan.com/v1/gToH/{today.strftime('%d-%m-%Y')}"
            response = requests.get(url, timeout=10)
            data = response.json()
        
            if data['code'] == 200:
                hijri = data['data']['hijri']
            
                       
                # Inisialisasi navigasi bulan Hijriah
                if 'hijri_view_year' not in st.session_state:
                    st.session_state.hijri_view_year = int(hijri['year'])
                if 'hijri_view_month' not in st.session_state:
                    st.session_state.hijri_view_month = int(hijri['month']['number'])
            
                # Navigasi bulan
                col_nav1, col_nav2, col_nav3 = st.columns([1, 12, 1])
                with col_nav1:
                    if st.button("❮", key="hijri_prev"):
                        if st.session_state.hijri_view_month == 1:
                            st.session_state.hijri_view_month = 12
                            st.session_state.hijri_view_year -= 1
                        else:
                            st.session_state.hijri_view_month -= 1
                        st.rerun()
                with col_nav2:
                    st.markdown(f"<h2 style='text-align: center;'>🌙 {nama_bulan_hijriah[st.session_state.hijri_view_month-1]} {st.session_state.hijri_view_year} H</h2>", unsafe_allow_html=True)
                with col_nav3:
                    if st.button("❯", key="hijri_next"):
                        if st.session_state.hijri_view_month == 12:
                            st.session_state.hijri_view_month = 1
                            st.session_state.hijri_view_year += 1
                        else:
                            st.session_state.hijri_view_month += 1
                        st.rerun()
            
                st.divider()
            
                # Ambil kalender bulan Hijriah dari API
                url_bulan = f"http://api.aladhan.com/v1/hijriCalendarByCity/{st.session_state.hijri_view_year}/{st.session_state.hijri_view_month}?city={st.session_state.city}&country={st.session_state.country}"
                r_bulan = requests.get(url_bulan, timeout=10)
                d_bulan = r_bulan.json()
            
                if d_bulan['code'] == 200:
                    days = d_bulan['data']
                
                    # Susun grid minggu (mulai Senin)
                    weeks = []
                    week = [None] * 7
                    pertama = datetime.strptime(days[0]['date']['gregorian']['date'], '%d-%m-%Y')
                    for i in range(pertama.weekday()):
                        week[i] = None
                
                    for item in days:
                        gd = datetime.strptime(item['date']['gregorian']['date'], '%d-%m-%Y')
                        wd = gd.weekday()
                        is_today = (gd.date() == today.date())
                        week[wd] = (item['date']['hijri']['day'], gd.strftime('%d/%m'), is_today)
                        if wd == 6:
                            weeks.append(week)
                            week = [None] * 7
                    if any(x is not None for x in week):
                        weeks.append(week)
                
                    # Render tabel
                    table_css = "<style>.calendar-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px; }.calendar-table th { background-color: #f0f2f6; padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd; color: #333; }.calendar-table td { padding: 10px; text-align: center; border: 1px solid #ddd; color: #333; font-weight: 500; }.calendar-table td.empty { background-color: #fafafa; }</style>"
                    html_table = "<div class='kal-panel'><table class='kal-table'><thead><tr>"
                    for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]:
                        html_table += f"<th>{day}</th>"
                    html_table += "</tr></thead><tbody>"
                
                    for w in weeks:
                        html_table += "<tr>"
                        for cell in w:
                            if cell is None:
                                html_table += "<td class='empty'></td>"
                            else:
                                h_day, g_short, is_today = cell
                                if is_today:
                                    html_table += f"<td class='today'><div style='font-size:20px;'>{h_day}</div><div style='font-size:11px;opacity:0.9;'>{g_short}</div></td>"
                                else:
                                    html_table += f"<td><div style='font-size:20px;font-weight:600;'>{h_day}</div><div style='font-size:11px;color:#888;'>{g_short}</div></td>"
                        html_table += "</tr>"
                    html_table += "</tbody></table></div>"
                    st.markdown(html_table, unsafe_allow_html=True)
                    st.caption("Angka besar = tanggal Hijriah | Angka kecil = tanggal Masehi | Hijau = hari ini")
                else:
                    st.error("❌ Gagal mengambil data kalender Hijriah.")
            else:
                st.error("❌ Gagal mengambil data tanggal Hijriah.")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timeout. Koneksi internet lambat.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Koneksi internet terputus.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    # ============================================
    # KALENDER 3: HIJRAH SYAMSIYAH
    # ============================================
    elif calendar_type == "Kalender Hijrah Syamsiah/Matahari":
        st.header("☀️ Kalender Hijrah Syamsiah/Matahari")
    
        p_year, p_month, p_day = gregorian_to_persian(today.year, today.month, today.day)
    
        
        # Inisialisasi navigasi bulan Syamsiah
        if 'syamsiah_view_year' not in st.session_state:
            st.session_state.syamsiah_view_year = p_year
        if 'syamsiah_view_month' not in st.session_state:
            st.session_state.syamsiah_view_month = p_month
    
        # Navigasi bulan
        col_nav1, col_nav2, col_nav3 = st.columns([1, 12, 1])
        with col_nav1:
            if st.button("❮", key="syams_prev"):
                if st.session_state.syamsiah_view_month == 1:
                    st.session_state.syamsiah_view_month = 12
                    st.session_state.syamsiah_view_year -= 1
                else:
                    st.session_state.syamsiah_view_month -= 1
                st.rerun()
        with col_nav2:
            st.markdown(f"<h2 style='text-align: center;'>☀️ {persian_months[st.session_state.syamsiah_view_month-1]} {st.session_state.syamsiah_view_year} HS</h2>", unsafe_allow_html=True)
        with col_nav3:
            if st.button("❯", key="syams_next"):
                if st.session_state.syamsiah_view_month == 12:
                    st.session_state.syamsiah_view_month = 1
                    st.session_state.syamsiah_view_year += 1
                else:
                    st.session_state.syamsiah_view_month += 1
                st.rerun()
    
        st.divider()
    
        # Kumpulkan hari pada bulan Syamsiah yang ditampilkan
        v_year = st.session_state.syamsiah_view_year
        v_month = st.session_state.syamsiah_view_month
    
        if v_month <= 6:
            offset_hari = (v_month - 1) * 31
        else:
            offset_hari = 186 + (v_month - 7) * 30
        mulai = datetime(v_year + 621, 3, 19) + timedelta(days=offset_hari - 3)
    
        hari_bulan = []
        for i in range(45):
            d = mulai + timedelta(days=i)
            py, pm, pd = gregorian_to_persian(d.year, d.month, d.day)
            if py == v_year and pm == v_month:
                hari_bulan.append((d, pd))
            elif hari_bulan:
                break
    
        # Susun grid minggu (mulai Senin)
        weeks = []
        week = [None] * 7
        if hari_bulan:
            for i in range(hari_bulan[0][0].weekday()):
                week[i] = None
            for d, pd in hari_bulan:
                wd = d.weekday()
                is_today = (d.date() == today.date())
                week[wd] = (pd, d.strftime('%d/%m'), is_today)
                if wd == 6:
                    weeks.append(week)
                    week = [None] * 7
            if any(x is not None for x in week):
                weeks.append(week)
    
        # Render tabel
        table_css = "<style>.calendar-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px; }.calendar-table th { background-color: #f0f2f6; padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd; color: #333; }.calendar-table td { padding: 10px; text-align: center; border: 1px solid #ddd; color: #333; font-weight: 500; }.calendar-table td.empty { background-color: #fafafa; }</style>"
        html_table = "<div class='kal-panel'><table class='kal-table'><thead><tr>"
        for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]:
            html_table += f"<th>{day}</th>"
        html_table += "</tr></thead><tbody>"
        for w in weeks:
            html_table += "<tr>"
            for cell in w:
                if cell is None:
                    html_table += "<td class='empty'></td>"
                else:
                    s_day, g_short, is_today = cell
                    if is_today:
                        html_table += f"<td class='today'><div style='font-size:20px;'>{s_day}</div><div style='font-size:11px;opacity:0.9;'>{g_short}</div></td>"
                    else:
                        html_table += f"<td><div style='font-size:20px;font-weight:600;'>{s_day}</div><div style='font-size:11px;color:#888;'>{g_short}</div></td>"
            html_table += "</tr>"
        html_table += "</tbody></table></div>"
        st.markdown(html_table, unsafe_allow_html=True)
        st.caption("Angka besar = tanggal Hijrah Syamsiah | Angka kecil = tanggal Masehi | Hijau = hari ini")

    # ============================================
    # KALENDER 4: JAWA (SAKA)
    # ============================================
    elif calendar_type == "Kalender Jawa (Saka)":
        st.header("📜 Kalender Jawa (Saka)")
        st.markdown("*Kalender Tradisional Indonesia*")
    
        bulan_jawa = ["Sura", "Sapar", "Mulud", "Bakda Mulud", "Jumadilawal", "Jumadilakhir", "Rejeb", "Ruwah", "Pasa", "Sawal", "Dulkaidah", "Besar"]
        neptu_hari = {"Senin": 4, "Selasa": 3, "Rabu": 7, "Kamis": 8, "Jumat": 6, "Sabtu": 9, "Minggu": 5}
        neptu_pasaran = {"Legi": 5, "Pahing": 9, "Pon": 7, "Wage": 4, "Kliwon": 8}
    
        j_today = get_javanese_date(today.year, today.month, today.day)
        neptu = neptu_hari[j_today['hari']] + neptu_pasaran[j_today['pasaran']]
    
        
        # Inisialisasi navigasi bulan Jawa
        if 'jawa_view_year' not in st.session_state:
            st.session_state.jawa_view_year = j_today['saka_year']
        if 'jawa_view_month' not in st.session_state:
            st.session_state.jawa_view_month = bulan_jawa.index(j_today['saka_month']) + 1
    
        # Navigasi bulan
        col_nav1, col_nav2, col_nav3 = st.columns([1, 12, 1])
        with col_nav1:
            if st.button("❮", key="jawa_prev"):
                if st.session_state.jawa_view_month == 1:
                    st.session_state.jawa_view_month = 12
                    st.session_state.jawa_view_year -= 1
                else:
                    st.session_state.jawa_view_month -= 1
                st.rerun()
        with col_nav2:
            st.markdown(f"<h2 style='text-align: center;'>📜 {bulan_jawa[st.session_state.jawa_view_month-1]} {st.session_state.jawa_view_year} Saka</h2>", unsafe_allow_html=True)
        with col_nav3:
            if st.button("❯", key="jawa_next"):
                if st.session_state.jawa_view_month == 12:
                    st.session_state.jawa_view_month = 1
                    st.session_state.jawa_view_year += 1
                else:
                    st.session_state.jawa_view_month += 1
                st.rerun()
    
        st.divider()
    
        # Kumpulkan hari pada bulan Jawa yang ditampilkan
        v_year = st.session_state.jawa_view_year
        v_month = st.session_state.jawa_view_month
    
        ref_date = datetime(2024, 7, 17)
        months_from_ref = (v_year - 1956) * 12 + (v_month - 1)
        approx_days = int(months_from_ref * 29.5)
        mulai = ref_date + timedelta(days=approx_days - 2)
    
        hari_bulan = []
        for i in range(40):
            d = mulai + timedelta(days=i)
            j = get_javanese_date(d.year, d.month, d.day)
            if j['saka_year'] == v_year and j['saka_month'] == bulan_jawa[v_month-1]:
                hari_bulan.append((d, j['saka_day'], j['pasaran']))
            elif hari_bulan:
                break
    
        # Susun grid minggu (mulai Senin)
        weeks = []
        week = [None] * 7
        if hari_bulan:
            for i in range(hari_bulan[0][0].weekday()):
                week[i] = None
            for d, s_day, pasaran in hari_bulan:
                wd = d.weekday()
                is_today = (d.date() == today.date())
                week[wd] = (s_day, pasaran, d.strftime('%d/%m'), is_today)
                if wd == 6:
                    weeks.append(week)
                    week = [None] * 7
            if any(x is not None for x in week):
                weeks.append(week)
    
        # Render tabel
        table_css = "<style>.calendar-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px; }.calendar-table th { background-color: #f0f2f6; padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd; color: #333; }.calendar-table td { padding: 10px; text-align: center; border: 1px solid #ddd; color: #333; font-weight: 500; }.calendar-table td.empty { background-color: #fafafa; }</style>"
        html_table = "<div class='kal-panel'><table class='kal-table'><thead><tr>"
        for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]:
            html_table += f"<th>{day}</th>"
        html_table += "</tr></thead><tbody>"
        for w in weeks:
            html_table += "<tr>"
            for cell in w:
                if cell is None:
                    html_table += "<td class='empty'></td>"
                else:
                    s_day, pasaran, g_short, is_today = cell
                    if is_today:
                        html_table += f"<td class='today'><div style='font-size:20px;'>{s_day}</div><div style='font-size:12px;font-weight:600;'>{pasaran}</div><div style='font-size:10px;opacity:0.9;'>{g_short}</div></td>"
                    else:
                        html_table += f"<td><div style='font-size:20px;font-weight:600;'>{s_day}</div><div style='font-size:12px;color:#764ba2;font-weight:600;'>{pasaran}</div><div style='font-size:10px;color:#888;'>{g_short}</div></td>"
            html_table += "</tr>"
        html_table += "</tbody></table></div>"
        st.markdown(html_table, unsafe_allow_html=True)
        st.caption("Angka besar = tanggal Jawa | Ungu = Pasaran | Angka kecil = tanggal Masehi | Hijau = hari ini")

    # ============================================
    # KALENDER 5: CINA (IMLEK)
    # ============================================
    elif calendar_type == "Kalender Cina (Imlek)":
        st.header("🏮 Kalender Cina (Imlek)")
        st.markdown("*Kalender Tradisional Cina*")
    
        try:
            from lunardate import LunarDate

        
            bulan_cina = ["Zheng", "Er", "San", "Si", "Wu", "Liu", "Qi", "Ba", "Jiu", "Shi", "Dong", "La"]
        
            l_today = LunarDate.fromSolarDate(today.year, today.month, today.day)
            chinese = get_chinese_date(today.year, today.month, today.day)
        
            leap_today = "Run " if l_today.isLeapMonth else ""
                
            # Inisialisasi navigasi
            if 'imlek_view_year' not in st.session_state:
                st.session_state.imlek_view_year = l_today.year
            if 'imlek_view_month' not in st.session_state:
                st.session_state.imlek_view_month = l_today.month
        
            v_year = st.session_state.imlek_view_year
            v_month = st.session_state.imlek_view_month
        
            # Navigasi bulan
            col_nav1, col_nav2, col_nav3 = st.columns([1, 12, 1])
            with col_nav1:
                if st.button("❮", key="imlek_prev"):
                    if st.session_state.imlek_view_month == 1:
                        st.session_state.imlek_view_month = 12
                        st.session_state.imlek_view_year -= 1
                    else:
                        st.session_state.imlek_view_month -= 1
                    st.rerun()
            with col_nav2:
                st.markdown(f"<h2 style='text-align: center;'>🏮 Bulan {bulan_cina[v_month-1]} ({v_month}) - Tahun {v_year + 2698}</h2>", unsafe_allow_html=True)
            with col_nav3:
                if st.button("❯", key="imlek_next"):
                    if st.session_state.imlek_view_month == 12:
                        st.session_state.imlek_view_month = 1
                        st.session_state.imlek_view_year += 1
                    else:
                        st.session_state.imlek_view_month += 1
                    st.rerun()
        
            # Cek bulan kabisat (Run)
            has_leap = False
            try:
                LunarDate(v_year, v_month, 1, True)
                has_leap = True
            except ValueError:
                has_leap = False
        
            show_leap = False
            if has_leap:
                show_leap = st.checkbox("🔄 Tampilkan Bulan Run (kabisat)", value=False)
        
            # Awal bulan & jumlah hari
            start_solar = LunarDate(v_year, v_month, 1, show_leap).toSolarDate()
            try:
                LunarDate(v_year, v_month, 30, show_leap)
                n_days = 30
            except ValueError:
                n_days = 29
        
            # Susun grid minggu (mulai Senin)
            weeks = []
            week = [None] * 7
            for i in range(start_solar.weekday()):
                week[i] = None
            for i in range(n_days):
                d = start_solar + timedelta(days=i)
                wd = d.weekday()
                is_today = (d == today.date())
                week[wd] = (i + 1, d.strftime('%d/%m'), is_today)
                if wd == 6:
                    weeks.append(week)
                    week = [None] * 7
            if any(x is not None for x in week):
                weeks.append(week)
        
            # Render tabel
            table_css = "<style>.calendar-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px; }.calendar-table th { background-color: #f0f2f6; padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd; color: #333; }.calendar-table td { padding: 10px; text-align: center; border: 1px solid #ddd; color: #333; font-weight: 500; }.calendar-table td.empty { background-color: #fafafa; }</style>"
            html_table = "<div class='kal-panel'><table class='kal-table'><thead><tr>"
            for day in ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Ahad"]:
                html_table += f"<th>{day}</th>"
            html_table += "</tr></thead><tbody>"
            for w in weeks:
                html_table += "<tr>"
                for cell in w:
                    if cell is None:
                        html_table += "<td class='empty'></td>"
                    else:
                        l_day, g_short, is_today = cell
                        if is_today:
                            html_table += f"<td class='today'><div style='font-size:20px;'>{l_day}</div><div style='font-size:11px;opacity:0.9;'>{g_short}</div></td>"
                        else:
                            html_table += f"<td><div style='font-size:20px;font-weight:600;'>{l_day}</div><div style='font-size:11px;color:#888;'>{g_short}</div></td>"
                html_table += "</tr>"
            html_table += "</tbody></table></div>"
            st.markdown(html_table, unsafe_allow_html=True)
            st.caption("Angka besar = tanggal Imlek | Angka kecil = tanggal Masehi | Hijau = hari ini")
        
            # Info Shio lengkap
            st.divider()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🐉 Shio", chinese['shio'])
            with col2:
                st.metric("🔥 Elemen", chinese['elemen'])
            with col3:
                st.metric("☯️ Yin/Yang", chinese['yin_yang'])
            with col4:
                st.metric("🏮 Tahun Cina", str(today.year + 2698))
        except ImportError:
            st.error("❌ Library 'lunardate' belum terinstall. Pastikan 'lunardate' ada di requirements.txt lalu push ulang.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ==========================================
# PENGATURAN (Expander di Main Content)
# ==========================================
with st.expander("⚙️ Pengaturan Kalender", expanded=False):
    st.markdown("### Pilih pengaturan di bawah ini:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        calendar_options = [
            "Kalender Masehi", "Kalender Hijriah Qomariah/Bulan",
            "Kalender Hijrah Syamsiah/Matahari", "Kalender Jawa (Saka)", "Kalender Cina (Imlek)"
        ]
        current_cal_idx = calendar_options.index(st.session_state.calendar_type) if st.session_state.calendar_type in calendar_options else 0
        
        # Langsung update session state saat user memilih
        st.session_state.calendar_type = st.radio("Pilih Kalender:", calendar_options, index=current_cal_idx, key="cal_radio")
    
    with col2:
        current_location = f"{st.session_state.city}, {st.session_state.country}"
        default_city_idx = ALL_CITIES.index(current_location) if current_location in ALL_CITIES else 0
        
        selected_loc = st.selectbox("🌍 Cari & Pilih Kota", options=ALL_CITIES, index=default_city_idx, key="city_select")
        # Langsung update session state saat user memilih
        st.session_state.city = selected_loc.split(", ")[0]
        st.session_state.country = selected_loc.split(", ")[1]
    
    with col3:
        method_options = [(20, "Kemenag RI (Indonesia)"), (2, "Muslim World League"), (4, "Umm Al-Qura University, Makkah")]
        current_method_idx = next((i for i, x in enumerate(method_options) if x == st.session_state.method), 0)
        
        # Langsung update session state saat user memilih
        st.session_state.method = st.selectbox("Metode Perhitungan Sholat", method_options, index=current_method_idx, format_func=lambda x: x[1], key="method_select")
    
    st.success("✅ Pengaturan tersimpan. Tutup panel ini untuk melihat hasil.")
    st.divider()
    tema_options = list(THEMES.keys())
    current_tema_idx = tema_options.index(st.session_state.theme) if st.session_state.theme in tema_options else 0
    st.session_state.theme = st.selectbox("🎨 Tema Dashboard", tema_options, index=current_tema_idx, key="theme_select")

# ==========================================
# GENERATOR LINK TV MASJID (SOLUSI MULTI-MASJID)
# ==========================================
from urllib.parse import quote

with st.expander("📺 Buat Link TV Masjid Anda (Solusi Multi-Masjid)"):
    st.markdown("**Untuk takmir & masjid lain:** isi data di bawah, salin link / cetak QR, tempel di TV masjid. Tanpa perlu sentuh kode!")
    
    g_col1, g_col2 = st.columns([2, 1])
    with g_col1:
        g_masjid = st.text_input("🕌 Nama Masjid", value="Masjid Al-Ikhlas", key="g_masjid")
        g_city = st.selectbox("🌍 Kota untuk TV", options=ALL_CITIES, index=ALL_CITIES.index("Jakarta, Indonesia") if "Jakarta, Indonesia" in ALL_CITIES else 0, key="g_city")
        g_alamat = st.text_input("📮 Alamat Masjid", value="Jl. Raya No. 1", key="g_alamat")
        g_kontak = st.text_input("📞 Kontak Takmir", value="0812-3456-7890", key="g_kontak")
        g_teks = st.text_area("📜 Running Text / Pengumuman (satu pesan per baris, opsional)", value="", height=100, key="g_teks")
        g_slogan = st.text_area("✍️ Tulisan statis bawah TV (maks 3 baris x 40 karakter — satu baris per pesan)", value="Selamat Menunaikan Ibadah Sholat", height=90, key="g_slogan")
        g_bg = st.text_input("🖼️ URL Gambar / Video Latar (opsional)", value="", key="g_bg")
        st.caption("📌 Google Drive: Share → 'Anyone with the link'. Gambar langsung tampil; untuk VIDEO pilih jenis 'video' → otomatis bisu + berulang di TV.")
        g_jenis = st.selectbox("📦 Jenis file Google Drive", ["otomatis", "gambar", "video"], key="g_jenis")
        g_method = st.selectbox("🧮 Metode Perhitungan", options=[(20, "Kemenag RI (Indonesia)"), (2, "Muslim World League"), (4, "Umm Al-Qura University, Makkah")], format_func=lambda x: x[1], key="g_method")
        
        st.info(f"🌍 Kota untuk TV: **{g_city}** (ubah di selectbox di atas)")
        
        teks_param = ""
        if g_teks.strip():
            teks_param = "&teks=" + quote("|".join([t.strip() for t in g_teks.split(chr(10)) if t.strip()]))
        tv_url = "https://takwimkalender.streamlit.app/?mode=tv&city=" + quote(st.session_state.city) + "&country=" + quote(g_city.split(", ")[1]) + "&masjid=" + quote(g_masjid) + "&alamat=" + quote(g_alamat) + "&kontak=" + quote(g_kontak) + ("&slogan=" + quote(g_slogan) if g_slogan.strip() else "") + "&method=" + str(g_method[0]) + ("&bg=" + quote(g_bg) + ("&jenis=" + g_jenis if g_jenis != "otomatis" else "") if g_bg.strip() else "") + teks_param
        
        st.markdown("**Link TV Masjid Anda:**")
        st.code(tv_url)
        st.markdown(f"🔗 **[Klik untuk Uji Coba Link]({tv_url})**")
    
    with g_col2:
        st.image("https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=" + quote(tv_url), width=200)
        st.caption("📱 Cetak QR ini & tempel di masjid — takmir tinggal scan!")

