import streamlit as st
import requests
from datetime import datetime
import calendar

st.set_page_config(page_title="Dasbor Kalender Taqwim", layout="wide")

# CSS untuk membuat header sticky/fixed
st.markdown("""
<style>
/* Fix header agar tidak scroll */
[data-testid="stHeading"] {
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 999;
    padding: 1rem 0;
    margin: 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Atau target elemen h1 langsung */
h1 {
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 999;
    padding: 1rem 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Pastikan sidebar juga fixed */
[data-testid="stSidebar"] {
    position: fixed;
    top: 0;
    height: 100vh;
    z-index: 1000;
    overflow-y: auto;
}

/* Beri padding pada konten utama agar tidak tertutup header */
.main > div {
    padding-top: 100px;
}
</style>
""", unsafe_allow_html=True)

# Anti Google Translate
st.markdown("""
<meta name="google" content="notranslate">
<meta name="translate" content="no">
<style>
.notranslate {
    translate: no;
}
</style>
""", unsafe_allow_html=True)

st.title("🌍 Dasbor Kalender Taqwim")

# ==========================================
# DATABASE KOTA DUNIA (Untuk Autocomplete)
# ==========================================
WORLD_CITIES = {
    "Indonesia": ["Jakarta", "Surabaya", "Bandung", "Medan", "Semarang", "Makassar", "Palembang", "Tangerang", "Depok", "Bekasi", "Padang", "Malang", "Denpasar", "Samarinda", "Banjarmasin", "Pontianak", "Manado", "Balikpapan", "Jambi", "Solo", "Yogyakarta", "Pekanbaru", "Bogor", "Batam", "Bandar Lampung", "Cirebon", "Mataram", "Kupang", "Ambon", "Jayapura", "Palu", "Kendari", "Ternate", "Sorong", "Bengkulu", "Pangkal Pinang", "Tanjung Pinang", "Gorontalo", "Mamuju", "Banda Aceh", "Dumai"],
    "Saudi Arabia": ["Makkah", "Madinah", "Riyadh", "Jeddah", "Dammam", "Khobar", "Taif", "Buraidah", "Khamis Mushait", "Najran", "Tabuk", "Hail", "Jubail", "Abha", "Yanbu"],
    "Malaysia": ["Kuala Lumpur", "George Town", "Johor Bahru", "Kota Kinabalu", "Kuching", "Shah Alam", "Petaling Jaya", "Ipoh", "Malacca", "Kuantan", "Kota Bharu", "Alor Setar", "Kuala Terengganu", "Seremban"],
    "Singapore": ["Singapore"],
    "Brunei": ["Bandar Seri Begawan"],
    "Thailand": ["Bangkok", "Chiang Mai", "Phuket", "Pattaya", "Hat Yai", "Nakhon Ratchasima", "Khon Kaen", "Udon Thani", "Narathiwat", "Yala", "Pattani"],
    "United Arab Emirates": ["Dubai", "Abu Dhabi", "Sharjah", "Al Ain", "Ajman", "Ras Al Khaimah", "Fujairah"],
    "Qatar": ["Doha", "Al Rayyan", "Al Wakrah", "Al Khor"],
    "Kuwait": ["Kuwait City", "Al Ahmadi", "Hawalli", "Salmiya"],
    "Bahrain": ["Manama", "Riffa", "Muharraq", "Isa Town"],
    "Oman": ["Muscat", "Salalah", "Sohar", "Nizwa", "Sur", "Ibri"],
    "Egypt": ["Cairo", "Alexandria", "Giza", "Luxor", "Aswan", "Port Said", "Suez", "Ismailia", "Tanta", "Mansoura"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Bursa", "Antalya", "Adana", "Gaziantep", "Konya", "Mersin", "Diyarbakir"],
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Multan", "Peshawar", "Quetta", "Sialkot", "Gujranwala"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Srinagar"],
    "Bangladesh": ["Dhaka", "Chittagong", "Sylhet", "Rajshahi", "Khulna", "Barisal", "Rangpur"],
    "Iran": ["Tehran", "Mashhad", "Isfahan", "Shiraz", "Tabriz", "Qom", "Ahvaz", "Kermanshah", "Yazd"],
    "Iraq": ["Baghdad", "Basra", "Mosul", "Erbil", "Najaf", "Karbala", "Sulaymaniyah", "Kirkuk"],
    "Jordan": ["Amman", "Zarqa", "Irbid", "Aqaba", "Salt", "Mafraq"],
    "Lebanon": ["Beirut", "Tripoli", "Sidon", "Tyre", "Nabatieh", "Zahle"],
    "Syria": ["Damascus", "Aleppo", "Homs", "Latakia", "Hama", "Deir ez-Zor"],
    "Yemen": ["Sanaa", "Aden", "Taiz", "Al Hudaydah", "Mukalla", "Ibb"],
    "Morocco": ["Casablanca", "Rabat", "Marrakech", "Fez", "Tangier", "Agadir", "Meknes"],
    "Algeria": ["Algiers", "Oran", "Constantine", "Annaba", "Blida", "Batna"],
    "Tunisia": ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte", "Gabes"],
    "Libya": ["Tripoli", "Benghazi", "Misrata", "Bayda", "Zawiya", "Tobruk"],
    "Sudan": ["Khartoum", "Omdurman", "Port Sudan", "Kassala", "Nyala", "El Obeid"],
    "Nigeria": ["Lagos", "Abuja", "Kano", "Ibadan", "Port Harcourt", "Kaduna", "Maiduguri"],
    "South Africa": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth", "Bloemfontein"],
    "Kenya": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Malindi"],
    "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Hangzhou", "Wuhan", "Xi'an", "Nanjing", "Tianjin", "Urumqi", "Kashgar"],
    "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama", "Nagoya", "Sapporo", "Fukuoka", "Kobe", "Hiroshima", "Sendai"],
    "South Korea": ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon", "Gwangju", "Ulsan", "Suwon"],
    "Philippines": ["Manila", "Quezon City", "Davao", "Cebu City", "Zamboanga", "Makati", "Pasig", "Marawi"],
    "Vietnam": ["Ho Chi Minh City", "Hanoi", "Da Nang", "Hai Phong", "Can Tho", "Nha Trang", "Hue"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Canberra", "Gold Coast", "Darwin"],
    "New Zealand": ["Auckland", "Wellington", "Christchurch", "Hamilton", "Dunedin", "Tauranga"],
    "United Kingdom": ["London", "Manchester", "Birmingham", "Glasgow", "Liverpool", "Leeds", "Edinburgh", "Bristol", "Cardiff", "Belfast"],
    "France": ["Paris", "Marseille", "Lyon", "Toulouse", "Nice", "Nantes", "Strasbourg", "Bordeaux", "Lille"],
    "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne", "Stuttgart", "Dusseldorf", "Leipzig", "Dortmund"],
    "Netherlands": ["Amsterdam", "Rotterdam", "The Hague", "Utrecht", "Eindhoven", "Groningen", "Tilburg"],
    "Belgium": ["Brussels", "Antwerp", "Ghent", "Bruges", "Liege", "Namur"],
    "Switzerland": ["Zurich", "Geneva", "Basel", "Bern", "Lausanne", "Lucerne", "Lugano"],
    "Austria": ["Vienna", "Salzburg", "Innsbruck", "Graz", "Linz", "Klagenfurt"],
    "Italy": ["Rome", "Milan", "Naples", "Turin", "Florence", "Bologna", "Venice", "Verona", "Palermo"],
    "Spain": ["Madrid", "Barcelona", "Valencia", "Seville", "Bilbao", "Malaga", "Zaragoza", "Murcia", "Granada"],
    "Portugal": ["Lisbon", "Porto", "Faro", "Coimbra", "Braga", "Funchal"],
    "Greece": ["Athens", "Thessaloniki", "Patras", "Heraklion", "Larissa", "Rhodes"],
    "Russia": ["Moscow", "Saint Petersburg", "Novosibirsk", "Yekaterinburg", "Kazan", "Nizhny Novgorod", "Chelyabinsk", "Ufa"],
    "United States": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Francisco", "Washington", "Boston", "Seattle", "Miami", "Detroit", "Minneapolis", "Denver", "Atlanta"],
    "Canada": ["Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg", "Quebec City", "Halifax"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "Leon", "Juarez", "Cancun"],
    "Brazil": ["Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza", "Belo Horizonte", "Manaus", "Curitiba", "Recife"],
    "Argentina": ["Buenos Aires", "Cordoba", "Rosario", "Mendoza", "La Plata", "San Miguel de Tucuman", "Mar del Plata"],
    "Chile": ["Santiago", "Valparaiso", "Concepcion", "La Serena", "Antofagasta", "Temuco", "Rancagua"]
}

# Buat daftar gabungan "Kota, Negara" untuk dropdown
ALL_CITIES = []
for country_name, cities in WORLD_CITIES.items():
    for city_name in cities:
        ALL_CITIES.append(f"{city_name}, {country_name}")
ALL_CITIES.sort()

# ==========================================
# SIDEBAR PENGATURAN
# ==========================================
if 'view_year' not in st.session_state:
    st.session_state.view_year = datetime.now().year
if 'view_month' not in st.session_state:
    st.session_state.view_month = datetime.now().month

st.sidebar.header("⚙️ Pengaturan")
calendar_type = st.sidebar.radio(
    "Pilih Kalender:",
    ["Kalender Masehi (Gregorian)", 
     "Kalender Hijriah Qomariah/Bulan",
     "Kalender Hijrah Syamsiah/Matahari",
     "Kalender Jawa (Saka)",
     "Kalender Cina (Imlek)"],
    index=0
)

# GANTI: Input teks biasa menjadi Dropdown dengan fitur ketik/cari (autocomplete)
default_idx = ALL_CITIES.index("Jakarta, Indonesia") if "Jakarta, Indonesia" in ALL_CITIES else 0
selected_location = st.sidebar.selectbox(
    "🌍 Cari & Pilih Kota",
    options=ALL_CITIES,
    index=default_idx
)

# Pisahkan kembali menjadi variabel city dan country agar API tetap berjalan normal
city = selected_location.split(", ")[0]
country = selected_location.split(", ")[1]

method = st.sidebar.selectbox("Metode Perhitungan Sholat", [
    (20, "Kemenag RI (Indonesia)"),
    (2, "Muslim World League"),
    (4, "Umm Al-Qura University, Makkah"),
], format_func=lambda x: x[1])

today = datetime.now()

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
if calendar_type == "Kalender Masehi (Gregorian)":
    st.header("📅 Kalender Masehi ")
    
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
            st.error("❌ Gagal mengambil data")
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
    st.header("📜 Kalender Jawa (Saka)")
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
            st.error(f" Error: {e}")

st.markdown("---")
st.markdown("Dibuat dengan ❤️ menggunakan Streamlit")