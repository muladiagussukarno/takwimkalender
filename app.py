import streamlit as st
import requests
from datetime import datetime
import calendar

# Konfigurasi halaman
st.set_page_config(page_title="Dasbor Kalender Taqwim", layout="wide", page_icon="🌍")

# CSS untuk membuat header sticky dan selalu terlihat
st.markdown("""
<style>
header {visibility: hidden !important;}
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
[data-testid="stSidebar"] {
    position: fixed !important;
    top: 140px !important;
    height: calc(100vh - 140px) !important;
    z-index: 99998 !important;
    overflow-y: auto !important;
}
.main > div:first-child {
    padding-top: 220px !important;
}
.block-container {
    padding-top: 220px !important;
}
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

# Header
st.markdown("""
<div class="main-header">
    <h1>🌍 Dasbor Kalender Taqwim</h1>
    <p>Standar Internasional ISO | Terverifikasi Indonesia</p>
</div>
""", unsafe_allow_html=True)

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
        "Kepulauan Seribu", "Jakarta Selatan", "Jakarta Timur", "Jakarta Pusat", "Jakarta Barat", "Jakarta Utara",
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

# Default values untuk Jadwal Sholat & Kalender
if 'city' not in st.session_state:
    st.session_state.city = "Jakarta"
if 'country' not in st.session_state:
    st.session_state.country = "Indonesia"
if 'method' not in st.session_state:
    st.session_state.method = (20, "Kemenag RI (Indonesia)")
if 'calendar_type' not in st.session_state:
    st.session_state.calendar_type = "Kalender Masehi"

today = datetime.now()

# ============================================
# JADWAL SHOLAT (OTOMATIS MUNCUL DI ATAS!)
# ============================================
st.divider()
st.subheader("🕌 Jadwal Sholat Hari Ini")

# Info lokasi diambil dari session state
st.info(f"📍 **Lokasi:** {st.session_state.city.title()}, {st.session_state.country.title()} | **Metode:** {st.session_state.method[1]}")

try:
    url = f"http://api.aladhan.com/v1/timingsByCity?city={st.session_state.city}&country={st.session_state.country}&method={st.session_state.method[0]}"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data['code'] == 200:
        timings = data['data']['timings']
        date_info = data['data']['date']
        
        st.write(f"**📅 Tanggal:** {date_info['gregorian']['date']} | {date_info['hijri']['date']} {date_info['hijri']['month']['en']} {date_info['hijri']['year']} H")
        st.divider()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌅 Subuh (Fajr)", timings["Fajr"])
            st.metric("☀️ Dzuhur (Dhuhr)", timings["Dhuhr"])
            st.metric("🌤️ Ashar (Asr)", timings["Asr"])
        with col2:
            st.metric("🌇 Maghrib", timings["Maghrib"])
            st.metric("🌙 Isya (Isha)", timings["Isha"])
            st.metric("🌄 Terbit (Sunrise)", timings["Sunrise"])
        with col3:
            st.info("**⏰ Waktu Lainnya:**")
            st.write(f"- Imsak: {timings.get('Imsak', '-')}")
            st.write(f"- Midnight: {timings.get('Midnight', '-')}")
            st.write(f"- First Third: {timings.get('Firstthird', '-')}")
            st.write(f"- Last Third: {timings.get('Lastthird', '-')}")
    else:
        st.error("❌ Kota tidak ditemukan di database API.")
        st.warning("💡 Coba pilih kota lain atau periksa koneksi internet.")
        
except requests.exceptions.Timeout:
    st.error("⏱️ Request timeout. Koneksi internet lambat.")
except requests.exceptions.ConnectionError:
    st.error("🔌 Koneksi internet terputus. Periksa koneksi Anda.")
except Exception as e:
    st.error(f"❌ Terjadi kesalahan: {str(e)}")


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
        
        calendar_type = st.radio("Pilih Kalender:", calendar_options, index=current_cal_idx, key="calendar_type_input")
        st.session_state.calendar_type = calendar_type
    
    with col2:
        current_location = f"{st.session_state.city}, {st.session_state.country}"
        default_city_idx = ALL_CITIES.index(current_location) if current_location in ALL_CITIES else 0
        
        selected_location = st.selectbox("🌍 Cari & Pilih Kota", options=ALL_CITIES, index=default_city_idx, key="location_input")
        st.session_state.city = selected_location.split(", ")[0]
        st.session_state.country = selected_location.split(", ")[1]
    
    with col3:
        method_options = [(20, "Kemenag RI (Indonesia)"), (2, "Muslim World League"), (4, "Umm Al-Qura University, Makkah")]
        current_method_idx = next((i for i, x in enumerate(method_options) if x == st.session_state.method), 0)
        
        method = st.selectbox("Metode Perhitungan Sholat", method_options, index=current_method_idx, format_func=lambda x: x[1], key="method_input")
        st.session_state.method = method
    
    st.success("✅ Pengaturan tersimpan. Tutup panel ini untuk melihat hasil.")

# Ambil nilai dari session state untuk digunakan di bagian kalender di bawah
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
    hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
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
hari_indonesia = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
bulan_indonesia = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

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
    .calendar-table { width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 16px; }
    .calendar-table th { background-color: #f0f2f6; padding: 12px; text-align: center; font-weight: 600; border: 1px solid #ddd; color: #333; }
    .calendar-table td { padding: 12px; text-align: center; border: 1px solid #ddd; color: #333; font-weight: 500; }
    .calendar-table td.empty { background-color: #fafafa; }
    </style>"""
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
    st.header("Kalender Masehi")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tanggal</p><p style="font-size: 48px; font-weight: bold;">' + today.strftime("%d") + '</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Bulan</p><p style="font-size: 48px; font-weight: bold;">' + bulan_indonesia[today.month-1] + '</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="notranslate" translate="no"><p style="font-size: 14px; color: gray;">Tahun</p><p style="font-size: 48px; font-weight: bold;">' + today.strftime("%Y") + '</p></div>', unsafe_allow_html=True)
    st.divider()
    st.info(f"**Hari: {hari_indonesia[today.weekday()]}, {today.strftime('%d')} {bulan_indonesia[today.month-1]} {today.strftime('%Y')}**")
    display_calendar(st.session_state.view_year, st.session_state.view_month, bulan_indonesia, today.day if st.session_state.view_month == today.month and st.session_state.view_year == today.year else None)

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

st.markdown("---")
st.markdown("Dibuat dengan ❤️ menggunakan Streamlit")