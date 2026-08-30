import streamlit as st
import requests
from datetime import datetime
import calendar

# Konfigurasi halaman
st.set_page_config(page_title="Dasbor Kalender Taqwim", layout="wide", page_icon="🌍")

# CSS untuk membuat header sticky dan selalu terlihat
st.markdown("""
<style>
/* Sembunyikan Streamlit header decoration */
header {visibility: hidden !important;}

/* Sticky Header Utama */
.main-header {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    padding: 50px 20px 20px 20px !important;
    z-index: 99999 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
    text-align: center !important;
}

.main-header h1 {
    margin: 0 !important;
    font-size: 2rem !important;
    font-weight: bold !important;
    color: white !important;
    line-height: 1.2 !important;
}

.main-header p {
    margin: 8px 0 0 0 !important;
    font-size: 0.9rem !important;
    color: rgba(255,255,255,0.95) !important;
}

/* Sidebar fixed di bawah header */
[data-testid="stSidebar"] {
    position: fixed !important;
    top: 140px !important;
    height: calc(100vh - 140px) !important;
    z-index: 99998 !important;
    overflow-y: auto !important;
}

/* Konten utama diberi padding yang LEBIH BESAR */
.main > div:first-child {
    padding-top: 220px !important;
}

.block-container {
    padding-top: 220px !important;
}

/* Sembunyikan element Streamlit yang mengganggu */
.stApp > header {
    display: none !important;
}

.calendar-table {
    margin-top: 20px !important;
}

body {
    overflow-x: hidden !important;
}
</style>
""", unsafe_allow_html=True)

# Header yang akan sticky/fixed (HANYA SATU KALI)
st.markdown("""
<div class="main-header">
    <h1>🌍 Dasbor Kalender Taqwim</h1>
    <p>Standar Internasional ISO | Terverifikasi Indonesia</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# DATABASE KOTA DUNIA (Versi Lengkap)
# ==========================================
WORLD_CITIES = {
    "Indonesia": ["Banda Aceh", "Medan", "Padang", "Pekanbaru", "Jambi", "Palembang", "Bandar Lampung", "Jakarta", "Bogor", "Depok", "Bekasi", "Bandung", "Semarang", "Yogyakarta", "Surabaya", "Malang", "Denpasar", "Mataram", "Kupang", "Pontianak", "Palangka Raya", "Banjarmasin", "Samarinda", "Balikpapan", "Palu", "Makassar", "Kendari", "Manado", "Gorontalo", "Ambon", "Ternate", "Jayapura", "Sorong"],
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
# PENTING: BUAT ALL_CITIES SEKARANG (sebelum expander)
# ==========================================
ALL_CITIES = []
for country_name, cities in WORLD_CITIES.items():
    for city_name in cities:
        ALL_CITIES.append(f"{city_name}, {country_name}")
ALL_CITIES.sort()

# ==========================================
# INISIALISASI DEFAULT VALUES
# ==========================================
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year
if 'view_month' not in st.session_state:
    st.session_state.view_month = datetime.now().month

# Default values
default_calendar = "Kalender Masehi"
default_city = "Jakarta"
default_country = "Indonesia"
default_method = (20, "Kemenag RI (Indonesia)")

# ==========================================
# PENGATURAN (Expander di Main Content)
# ==========================================
with st.expander("⚙️ Pengaturan Kalender", expanded=False):
    st.markdown("### Pilih pengaturan di bawah ini:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        calendar_type = st.radio(
            "Pilih Kalender:",
            ["Kalender Masehi", 
             "Kalender Hijriah Qomariah/Bulan",
             "Kalender Hijrah Syamsiah/Matahari",
             "Kalender Jawa (Saka)",
             "Kalender Cina (Imlek)"],
            index=0
        )
    
    with col2:
        default_city_idx = ALL_CITIES.index("Jakarta, Indonesia") if "Jakarta, Indonesia" in ALL_CITIES else 0
        selected_location = st.selectbox(
            "🌍 Cari & Pilih Kota",
            options=ALL_CITIES,
            index=default_city_idx
        )
        city = selected_location.split(", ")[0]
        country = selected_location.split(", ")[1]
    
    with col3:
        method = st.selectbox("Metode Perhitungan Sholat", [
            (20, "Kemenag RI (Indonesia)"),
            (2, "Muslim World League"),
            (4, "Umm Al-Qura University, Makkah"),
        ], format_func=lambda x: x[1])
    
    st.success("✅ Pengaturan tersimpan. Tutup panel ini untuk melihat hasil.")

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
    bulan_jawa = ["Sura", "Sapar", "Mulud", "Bakda Mulud", 
                  "Jumadilawal", "Jumadilakhir", "Rejeb", 
                  "Ruwah", "Pasa", "Sawal", "Dulkaidah", "Besar"]
    
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
    
    hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    
    return {
        'saka_year': saka_year_calc,
        'saka_month': bulan_jawa[saka_month],
        'saka_day': saka_day,
        'windu': windu[windu_index],
        'pasaran': pasaran[pasaran_index],
        'hari': hari_indonesia[current_date.weekday()],
        'weton': f"{hari_indonesia[current_date.weekday()]} {pasaran[pasaran_index]}"
    }

def get_chinese_date(year, month, day):
    shio = ["Tikus", "Kerbau", "Macan", "Kelinci", "Naga", "Ular", 
            "Kuda", "Kambing", "Monyet", "Ayam", "Anjing", "Babi"]
    elemen = ["Kayu", "Api", "Tanah", "Logam", "Air"]
    
    shio_index = (year - 4) % 12
    elemen_index = (year - 4) % 10 // 2
    yin_yang = "Yang" if year % 2 == 0 else "Yin"
    
    return {
        'shio': shio[shio_index],
        'elemen': elemen[elemen_index],
        'yin_yang': yin_yang,
        'tahun_cina': year - 2698
    }

persian_months = ["Farvardin", "Ordibehesht", "Khordad", "Tir", 
                  "Mordad", "Shahrivar", "Mehr", "Aban", 
                  "Azar", "Dey", "Bahman", "Esfand"]

hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
bulan_indonesia = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", 
                   "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

def display_calendar(year, month, month_names, highlight_day=None):
    col_nav1, col_nav2, col_nav3 = st.columns([1, 3, 1])
    
    with col_nav1:
        if st.button("◀️ Bulan Sebelumnya", key="prev_month"):
            prev_month()
            st.rerun()
    
    with col_nav2:
        st.markdown(f"<h2 style='text-align: center;'>📆 {month_names[month-1]} {year}</h2>", unsafe_allow_html=True)
    
    with col_nav3:
        if st.button("Bulan Berikutnya ▶️", key="next_month"):
            next_month()
            st.rerun()
    
    st.divider()
    
    cal = calendar.monthcalendar(year, month)
    header = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    
    calendar_css = """
    <style>
    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 16px;
    }
    .calendar-table th {
        background-color: #f0f2f6;
        padding: 12px;
        text-align: center;
        font-weight: 600;
        border: 1px solid #ddd;
        color: #333;
    }
    .calendar-table td {
        padding: 12px;
        text-align: center;
        border: 1px solid #ddd;
        color: #333;
        font-weight: 500;
    }
    .calendar-table td.empty {
        background-color: #fafafa;
    }
    </style>
    """
    
    html_table = calendar_css + "<table class='calendar-table'><thead><tr>"
    
    for day in header:
        html_table += f"<th>{day}</th>"
    html_table += "</tr></thead><tbody>"
    
    for week in cal:
        html_table += "<tr>"
        for day in week:
            if day == 0:
                html_table += "<td class='empty'></td>"
            elif highlight_day and day == highlight_day:
                html_table += f"<td style='background-color: #4CAF50; color: white; font-weight: bold;'>{day}</td>"
            else:
                html_table += f"<td>{day}</td>"
        html_table += "</tr>"
    
    html_table += "</tbody></table>"
    st.markdown(html_table, unsafe_allow_html=True)

# ============================================
# KALENDER 1: MASEHI
# ============================================
if calendar_type == "Kalender Masehi":
    st.header("📅 Kalender Masehi")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tanggal</p><p style="font-size: 48px; font-weight: bold;">' + today.strftime("%d") + '</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Bulan</p><p style="font-size: 48px; font-weight: bold;">' + bulan_indonesia[today.month-1] + '</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun</p><p style="font-size: 48px; font-weight: bold;">' + today.strftime("%Y") + '</p></div>', unsafe_allow_html=True)
    
    st.divider()
    st.info(f"**Hari: {hari_indonesia[today.weekday()]}, {today.strftime('%d')} {bulan_indonesia[today.month-1]} {today.strftime('%Y')}**")
    
    display_calendar(
        st.session_state.view_year, 
        st.session_state.view_month, 
        bulan_indonesia,
        today.day if st.session_state.view_month == today.month and st.session_state.view_year == today.year else None
    )

# ============================================
# KALENDER 2: HIJRIAH QOMARIAH
# ============================================
elif calendar_type == "Kalender Hijriah Global Tunggal Qomariah":
    st.header("🌙 Kalender Hijriah Qomariah/Bulan")
    
    try:
        url = f"http://api.aladhan.com/v1/gToH/{today.strftime('%d-%m-%Y')}"
        response = requests.get(url)
        data = response.json()
        
        if data['code'] == 200:
            hijri = data['data']['hijri']
            gregorian = data['data']['gregorian']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tanggal Hijriah</p><p style="font-size: 48px; font-weight: bold;">' + hijri['day'] + '</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Bulan</p><p style="font-size: 48px; font-weight: bold;">' + hijri['month']['en'] + '</p></div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun</p><p style="font-size: 48px; font-weight: bold;">' + hijri['year'] + '</p></div>', unsafe_allow_html=True)
            
            st.divider()
            st.success(f"**Hari: {hijri['weekday']['en']}, {hijri['day']} {hijri['month']['en']} {hijri['year']} H**")
            st.info(f"**Arab:** {hijri['day']} {hijri['month']['ar']} {hijri['year']}")
        else:
            st.error(" Gagal mengambil data")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ============================================
# KALENDER 3: HIJRIAH SYAMSIYAH
# ============================================
elif calendar_type == "Kalender Hijrah Global Tunggal Syamsiah":
    st.header("☀️ Kalender Hijrah Syamsiah/Matahari")
       
    p_year, p_month, p_day = gregorian_to_persian(today.year, today.month, today.day)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tanggal</p><p style="font-size: 48px; font-weight: bold;">' + str(p_day) + '</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Bulan</p><p style="font-size: 48px; font-weight: bold;">' + persian_months[p_month-1] + '</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun</p><p style="font-size: 48px; font-weight: bold;">' + str(p_year) + '</p></div>', unsafe_allow_html=True)
    
    st.divider()
    st.success(f"**Hari: {hari_indonesia[today.weekday()]}, {p_day} {persian_months[p_month-1]} {p_year} HS**")

# ============================================
# KALENDER 4: JAWA
# ============================================
elif calendar_type == "Kalender Jawa (Saka)":
    st.header(" Kalender Jawa (Saka)")
    st.markdown("*Kalender Tradisional Indonesia*")
    
    javanese = get_javanese_date(today.year, today.month, today.day)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tanggal Jawa</p><p style="font-size: 48px; font-weight: bold;">' + str(javanese['saka_day']) + '</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Bulan</p><p style="font-size: 48px; font-weight: bold;">' + javanese['saka_month'] + '</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun Saka</p><p style="font-size: 48px; font-weight: bold;">' + str(javanese['saka_year']) + '</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun Windu</p><p style="font-size: 48px; font-weight: bold;">' + javanese['windu'] + '</p></div>', unsafe_allow_html=True)
    
    st.divider()
    st.success(f"**Hari: {javanese['hari']} {javanese['pasaran']}**\n\n**Weton: {javanese['weton']}**")

# ============================================
# KALENDER 5: CINA
# ============================================
elif calendar_type == "Kalender Cina (Imlek)":
    st.header("🏯 Kalender Cina (Imlek)")
    st.markdown("*Kalender Tradisional Cina*")
    
    chinese = get_chinese_date(today.year, today.month, today.day)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Shio</p><p style="font-size: 48px; font-weight: bold;">' + chinese['shio'] + '</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Elemen</p><p style="font-size: 48px; font-weight: bold;">' + chinese['elemen'] + '</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Yin/Yang</p><p style="font-size: 48px; font-weight: bold;">' + chinese['yin_yang'] + '</p></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun Cina</p><p style="font-size: 48px; font-weight: bold;">' + str(chinese['tahun_cina']) + '</p></div>', unsafe_allow_html=True)
    
    st.divider()
    st.success(f"**Tahun {chinese['shio']} - {chinese['elemen']} ({chinese['yin_yang']})**")

# ============================================
# JADWAL SHOLAT
# ============================================
st.divider()
st.subheader("🕌 Jadwal Sholat Hari Ini")

if st.button("🔍 Tampilkan Jadwal Sholat"):
    with st.spinner("Mengambil data..."):
        try:
            url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method={method[0]}"
            response = requests.get(url)
            data = response.json()
            
            if data['code'] == 200:
                timings = data['data']['timings']
                st.write(f"**Lokasi:** {city.title()}, {country.title()}")
                
                cols = st.columns(5)
                prayers = [
                    ("Subuh", timings["Fajr"]),
                    ("Dzuhur", timings["Dhuhr"]),
                    ("Ashar", timings["Asr"]),
                    ("Maghrib", timings["Maghrib"]),
                    ("Isya", timings["Isha"])
                ]
                for i, (name, time) in enumerate(prayers):
                    cols[i].metric(name, time)
            else:
                st.error("Kota tidak ditemukan")
        except Exception as e:
            st.error(f"❌ Error: {e}")

st.markdown("---")
st.markdown("Dibuat dengan ❤️ menggunakan Streamlit")