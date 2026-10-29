import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

VIDEOS_SEED = [
    # Horror
    ("9xY8u7V1aA0", "Dreadout 2 Full Gameplay Walkthrough Bahasa Indonesia - TAMAT", "2020-03-01T14:00:00Z", 10800, 3850000, 185000, 12400, "Walkthrough Dreadout 2 bahasa Indonesia sampai tamat bersama Brando Windah Basudara.", 20),
    ("8bZ7t6U0bB1", "RESIDENT EVIL 4 REMAKE - ADA ASHLEY CANTIK BANGET GAES! (Part 1)", "2023-03-24T13:00:00Z", 7200, 4200000, 240000, 18900, "Main Resident Evil 4 Remake hari pertama rilis, nostalgia bareng Leon dan Ashley!", 20),
    ("7cY6s5T9cC2", "RESIDENT EVIL VILLAGE - LAWAN LADY DIMITRESCU RAKSASA (Part 3)", "2021-05-08T12:30:00Z", 6800, 5100000, 290000, 21500, "Ketemu vampir raksasa Lady Dimitrescu di kastil horror Resident Evil Village.", 20),
    ("6dX5r4S8dD3", "POPPY PLAYTIME CHAPTER 3 - DEEP SLEEP SAMPAI TAMAT! CATNAP NGERI", "2024-02-01T15:00:00Z", 5400, 3600000, 210000, 15400, "Menjelajahi Playcare dan menghadapi CatNap yang sangat menyeramkan di Poppy Playtime Chapter 3.", 20),
    ("5eW4q3R7eE4", "FNAF RUIN DLC - KITA TAMATKAN HARI INI JUGA BOCIL KEMATIAN!", "2023-07-26T14:00:00Z", 6200, 2950000, 175000, 11200, "DLC FNAF Security Breach Ruin bersama Cassie dan robot animatronic misterius.", 20),
    ("4fV3p2Q6fF5", "PULANG INSANITY - GAME HORROR INDONESIA PALING MENYERAMKAN!", "2020-03-14T11:00:00Z", 5900, 2450000, 135000, 9800, "Game horror karya anak bangsa bertema pesugihan dan mitos mistis Indonesia.", 20),
    ("3gU2o1P5gG6", "CHILLA'S ART: THE CLOSING SHIFT - JADI KASIR COFFEE SHOP HORROR", "2022-03-20T16:00:00Z", 4800, 3400000, 195000, 14200, "Sensasi shift malam di kedai kopi yang diteror oleh stalker psikopat.", 20),
    ("2hT1n0O4hH7", "PAMALI: THE TIED SIREN - KUNTILANAK DAN POCONG NONGKOL GAES!", "2020-04-10T13:30:00Z", 5200, 2750000, 150000, 10500, "Menjelajahi rumah angker penuh mitos tabu masyarakat lokal Indonesia.", 20),
    ("1iS0m9N3iI8", "THE MORTUARY ASSISTANT - KERJA MALAM DI KAMAR MAYAT BERHANTU", "2022-08-05T14:45:00Z", 5700, 3100000, 180000, 13100, "Mengawetkan mayat sambil mengidentifikasi iblis pembawa kutukan.", 20),
    ("0jR9l8M2jJ9", "PHASMOPHOBIA BARENG JAYA DAN TEMAN - HANTUNYA AGRESIF BANGET", "2020-10-18T15:00:00Z", 7400, 3900000, 215000, 16800, "Berburu hantu Revenant dan Demon bareng squad mabar.", 20),
    ("9kQ8k7L1kK0", "SLENDERMAN THE EIGHT PAGES - NOSTALGIA JANTUNG MAU COPOT", "2021-01-15T12:00:00Z", 3600, 2150000, 120000, 8900, "Mencari 8 kertas di tengah hutan gelap gulita dikejar Slenderman.", 20),
    ("8lP7j6K0lL1", "GRANNY CHAPTER TWO - KITA KABUR DARI KAKEK DAN NENEK PSIKOPAT", "2020-02-22T10:30:00Z", 4300, 3300000, 165000, 11900, "Menghindari jebakan Nenek Granny dan Grandpa pembawa tongkat.", 20),
    ("7mO6i5J9mM2", "OUTLAST 2 WALKTHROUGH - KITA SELAMATKAN LYNN DARI KULTUS GILA", "2020-06-12T13:00:00Z", 8100, 2800000, 155000, 10800, "Horror kamera night vision di pedalaman gurun Arizona.", 20),
    ("6nN5h4I8nN3", "CHILLA'S ART: THE KARAOKE - GANGGUAN MISTERIUS DI TEMPAT KARAOKE", "2023-02-10T14:20:00Z", 4100, 2600000, 160000, 11400, "Game horror psikologis Jepang berlatar tempat karaoke malam hari.", 20),
    ("5mM4g3H7oO4", "LITTLE NIGHTMARES II - PETUALANGAN MONO DAN SIX DI PALE CITY", "2021-02-12T15:30:00Z", 6500, 3550000, 205000, 14900, "Menyelamatkan Six dari dunia distopia menara pemancar sinyal jahat.", 20),

    # Simulator
    ("4lL3f2G6pP5", "WARNET SIMULATOR - BANGUN WARNET IMPIAN DARI NOL SAMPAI SULTAN!", "2022-01-05T13:00:00Z", 6300, 6800000, 420000, 38500, "Membuka usaha warnet legendaris dengan PC sultan dan OP warnet kocak karya AkhirPekan Studio.", 20),
    ("3kK2e1F5qQ6", "BAKSO SIMULATOR - JUALAN BAKSO URAT & LAVA TERENAK SE-KOTA!", "2022-06-15T14:00:00Z", 5800, 5600000, 340000, 29000, "Gerobak bakso keliling melawan preman dan pembeli yang ngutang.", 20),
    ("2jJ1d0E4rR7", "SUPERMARKET SIMULATOR - KASIR SULTAN BELANJA DAN JUAL BARANG MAHAL", "2024-03-02T13:30:00Z", 7100, 4900000, 310000, 24600, "Mengatur rak toko, checkout pelanggan, dan menaikkan omzet toko kelontong modern.", 20),
    ("1iI0c9D3sS8", "INTERNET CAFE SIMULATOR 2 - WARNET DIGANGGU PREMAN & BOMBER", "2022-01-18T14:15:00Z", 6900, 4450000, 280000, 21300, "Lanjutan simulator warnet dengan fitur crypto mining dan keamanan ketat.", 20),
    ("0hH9b8C2tT9", "GAS STATION SIMULATOR - RESTORASI POM BENSIN DI TENGAH GURUN", "2021-09-20T12:00:00Z", 5600, 3700000, 220000, 16500, "Mengisi bensin mobil, mengecat tembok, dan melayani pelanggan gurun pasir.", 20),
    ("9gG8a7B1uU0", "CAR FOR SALE SIMULATOR 2023 - JADI MAKELAR MOBIL BEKAS KAYA RAYA", "2023-05-25T13:00:00Z", 6400, 4100000, 260000, 19800, "Beli mobil bekas murah di lelang, perbaiki bodi, jual dengan keuntungan maksimal.", 20),
    ("8fF7z6A0vV1", "STREAMER LIFE SIMULATOR - DARI KAMAR KOS KECIL SAMPAI STUDIO MEWAH", "2020-08-28T14:00:00Z", 6000, 3800000, 235000, 17200, "Simulasi kehidupan streamer pemula merintis karir di dunia online.", 20),
    ("7eE6y5Z9wW2", "GOAT SIMULATOR 3 - KAMBING RUSUH MENGHANCURKAN KOTA BERSAMA TEMAN", "2022-11-22T15:00:00Z", 4900, 2900000, 185000, 13400, "Kekacauan kambing mutan dengan fisika ragdoll yang super ngakak.", 20),
    ("6dD5x4Y8xX3", "KEBAB SIMULATOR - MERACIK DAGING KEBAB DAN SAUS SPESIAL ISTANBUL", "2023-11-05T13:45:00Z", 5100, 3200000, 195000, 14800, "Restoran kebab cepat saji dengan resep rahasia bumbu Timur Tengah.", 20),
    ("5cC4w3X7yY4", "TCG CARD SHOP SIMULATOR - BUKA PACK KARTU MONSTER LANGKA BIKIN KAYA", "2024-09-12T14:00:00Z", 6700, 4600000, 310000, 27500, "Jualan booster pack kartu TCG dan koleksi kartu holo legendaris.", 20),
    ("4bB3v2W6zZ5", "SECURITY BOOTH SIMULATOR - JAGA GERBANG KANTOR DI MALAM HARI", "2022-04-14T11:30:00Z", 3900, 2300000, 140000, 9500, "Memeriksa plat nomor mobil dan identitas tamu malam hari yang mencurigakan.", 20),
    ("3aA2u1V5aB6", "FARMING SIMULATOR 22 - MEMANEN GANDUM DENGAN TRAKTOR RAKSASA", "2021-12-04T12:00:00Z", 5500, 2100000, 130000, 8700, "Bercocok tanam dan beternak sapi di pedesaan Eropa yang damai.", 20),

    # Adventure, Action & Story
    ("2zZ1t0U4bC7", "GTA V ROLEPLAY KOTA KITA - MENGADU NASIB JADI TUKANG OJEK & DOKTER", "2021-04-15T15:00:00Z", 9200, 5800000, 360000, 32000, "Kisah lucu warga baru Los Santos mencari nafkah di server roleplay.", 20),
    ("1yY0s9T3cD8", "GTA SAN ANDREAS DEFINITIVE EDITION - NOSTALGIA CJ DI GROVE STREET", "2021-11-12T14:00:00Z", 7800, 4500000, 270000, 22400, "Kembali ke kota Los Santos tahun 90an bersama Carl Johnson dan Big Smoke.", 20),
    ("0xX9r8S2dE9", "GOD OF WAR RAGNAROK - KRATOS DAN ATREUS LAWAN THOR & ODIN! (Part 1)", "2022-11-09T13:00:00Z", 8600, 5200000, 340000, 29800, "Perang sembilan alam mitologi Nordik dimulai, Kratos mengayunkan Leviathan Axe.", 20),
    ("9wW8q7R1eF0", "GOD OF WAR RAGNAROK - PERTARUNGAN TERAKHIR MELAWAN ODIN! (TAMAT)", "2022-11-20T16:00:00Z", 9500, 4800000, 315000, 26700, "Ending cerita Kratos dan Atreus menuntaskan takdir Ragnarok.", 20),
    ("8vV7p6Q0fG1", "BLACK MYTH: WUKONG - SANG KERA SAKTI SUN WUKONG BANGKIT KEMBALI!", "2024-08-20T12:30:00Z", 8200, 5400000, 380000, 34200, "Action RPG grafis Unreal Engine 5 menjelajahi legenda klasik Journey to the West.", 20),
    ("7uU6o5P9gH2", "ELDEN RING - MELAWAN MALENIA BLADE OF MIQUELLA SAMPAI NANGIS!", "2022-03-30T17:00:00Z", 10200, 4700000, 320000, 31100, "Boss tersulit The Lands Between yang membuat frustasi jutaan gamer.", 20),
    ("6tT5n4O8hI3", "MARVEL'S SPIDER-MAN 2 - PETER PARKER & MILES MORALES VS VENOM!", "2023-10-20T13:00:00Z", 7600, 4900000, 330000, 28000, "Ayunan jaring di kota New York melawan pemburu Kraven dan symbiote Venom.", 20),
    ("5sS4m3N7iJ4", "THE LAST OF US PART 1 REMAKE - PERJALANAN JOEL DAN ELLIE DIMULAI", "2022-09-03T14:30:00Z", 7400, 3900000, 250000, 19500, "Dunia pasca apokalips jamur Cordyceps dengan grafis visual generasi baru.", 20),
    ("4rR3l2M6jK5", "GHOST OF TSUSHIMA - JIN SAKAI MEMILIH JALAN GHOST DEMI PULAU", "2020-07-18T13:00:00Z", 8100, 3600000, 225000, 17800, "Samurai terhormat yang berjuang melawan invasi bangsa Mongol di Tsushima.", 20),
    ("3qQ2k1L5kL6", "RED DEAD REDEMPTION 2 - KISAH ARTHUR MORGAN DAN GENG VAN DER LINDE", "2020-09-10T14:00:00Z", 9800, 4100000, 275000, 23900, "Kehidupan koboi era akhir Wild West yang penuh drama dan emosional.", 20),
    ("2pP1j0K4lM7", "BULLY SCHOLARSHIP EDITION - JIMMY HOPKINS PENGUASA ASRAMA BULLWORTH", "2020-05-15T12:00:00Z", 6800, 3900000, 240000, 19000, "Nostalgia game sekolah Rockstar Games, membolos pelajaran dan adu ketapel.", 20),
    ("1oO0i9J3mN8", "MINECRAFT SURVIVAL INDONESIA - MEMBANGUN RUMAH DAN ISTANA IMPIAN", "2020-04-02T11:00:00Z", 5400, 4600000, 290000, 24500, "Petualangan menambang berlian dan bertahan hidup dari serbuan Creeper.", 20),

    # Mobile, Multiplayer & Casual
    ("0nN9h8I2nO9", "MOBILE LEGENDS - PUSH RANK MYTHIC GLORY PAKE HERO FRANCO HOOK SAKTI!", "2021-08-25T13:00:00Z", 4200, 4300000, 260000, 22000, "Iron Hook Franco anti meleset bikin musuh panik di Land of Dawn.", 20),
    ("9mM8g7H1oP0", "STUMBLE GUYS - MAIN BARENG BOCIL KEMATIAN KITA REBUT MAHKOTA JUARA!", "2022-07-10T14:00:00Z", 4500, 6200000, 390000, 35000, "Lomba rintangan seru dan kocak bareng penonton sampai babak final.", 20),
    ("8lL7f6G0pQ1", "EA SPORTS FC 24 - KARIR MANAGER TIM KEMATIAN SAMPAI JUARA UCL!", "2023-10-02T13:00:00Z", 5900, 3500000, 210000, 16800, "Membangun taktik sepak bola menyerang dan merekrut wonderkid dunia.", 20),
    ("7kK6e5F9qR2", "EFOOTBALL 2024 - GACHA PEMAIN EPIC MESSI DAN RONALDO SAMPAI DAPAT!", "2023-12-15T14:30:00Z", 4800, 3300000, 195000, 15200, "Sensasi buka koin box draw pemain legendaris impian di eFootball.", 20),
    ("6jJ5d4E8rS3", "GENSHIN IMPACT - BUKA WISH GACHA ARCHON FURINA DAN NEUVILLETTE!", "2023-11-10T15:00:00Z", 5200, 4100000, 270000, 23000, "Penjelajahan wilayah Fontaine dan pertarungan boss elemen air.", 20),
    ("5iI4c3D7sT4", "HONKAI STAR RAIL - MENCOBA GAME BARU HOYOVERSE DI ASTRAL EXPRESS", "2023-04-26T12:00:00Z", 5700, 3200000, 205000, 16400, "RPG berbasis giliran menjelajahi galaksi bersama Kru Astral Express.", 20),
    ("4hH3b2C6tU5", "ROBLOX INDONESIA - KABUR DARI PENJARA BARRY'S PRISON RUN!", "2021-06-18T13:30:00Z", 3800, 4800000, 310000, 27600, "Parkour rintangan gila di game Roblox bersama komunitas penonton.", 20),
    ("3gG2a1B5uV6", "AMONG US INDONESIA - WINDAN JADI IMPOSTOR PALING LICIK SE-PESAWAT", "2020-09-22T14:00:00Z", 4600, 5700000, 350000, 31000, "Fitnah dan diskusi panas di cafeteria pesawat ruang angkasa Skeld.", 20),
    ("2fF1z0A4vW7", "FALL GUYS ULTIMATE KNOCKOUT - REBUTAN EKOR DAN MAHKOTA EMAS", "2020-08-15T12:00:00Z", 4100, 4300000, 260000, 21500, "Battle royale penuh warna berlari menabrak pintu dan bola raksasa.", 20),
    ("1eE0y9Z3wX8", "FREE FIRE BARENG BOCIL - PAKE SENJATA SHOTGUN SPAS RATAKAN LOBBY!", "2020-11-05T13:00:00Z", 4000, 3700000, 220000, 18500, "Mabar Free Fire mode Ranked penuh momen salto dan booyah.", 20),
    ("0dD9x8Y2xY9", "PUBG MOBILE - KITA CHICKEN DINNER DI MAP ERANGEL BARENG TEMAN", "2020-07-04T14:30:00Z", 5100, 3400000, 200000, 16200, "Tembak-menembak intens di Pochinki dan perburuan airdrop AWM.", 20),
    ("9cC8w7X1yZ0", "CLASH ROYALE - DECK MEGA KNIGHT BIKIN MUSUH LANGSUNG EMOTE MARAH", "2022-02-28T11:00:00Z", 3500, 2600000, 160000, 12800, "Strategi kartu tower rush dan counter serangan kilat musuh.", 20),

    # Special, Charity & Events
    ("8bB7v6W0zA1", "CHARITY STREAM 10 JAM UNTUK SESAMA - KITA KUMPULKAN 1 MILIAR RUPIAH!", "2022-10-11T09:00:00Z", 36000, 11500000, 1200000, 142000, "Live streaming amal maraton untuk membantu biaya pendidikan dan yayasan panti asuhan di seluruh Indonesia.", 24),
    ("7aA6u5V9aB2", "MENUJU 10 JUTA SUBSCRIBER - TERIMA KASIH SEMUA TEMAN DAN BOCIL KEMATIAN!", "2023-04-05T12:00:00Z", 14400, 9800000, 950000, 115000, "Momen bersejarah mencapai Diamond Play Button YouTube bersama jutaan audiens setia.", 24),
    ("6zZ5t4U8bC3", "MENONTON VIDEO LUCU & TIKTOK WINDAH BASUDARA DARI FANS! NGAKAK PARAH", "2021-05-20T13:00:00Z", 4200, 5200000, 360000, 29000, "Reaksi melihat editan video lucu buatan para subscriber dan TikTokers.", 24),
    ("5yY4s3T7cD4", "NOBAR TIMNAS INDONESIA VS VIETNAM DI PIALA ASIA - JANTUNGAN BARENG!", "2024-01-19T14:30:00Z", 9000, 6700000, 480000, 52000, "Nonton bareng perjuangan Timnas Garuda dengan sorak sorai dan doa kemenangan.", 17),
    ("4xX3r2S6dE5", "TAMATKAN 10 GAME DALAM SATU HARI - TANTANGAN GILA WINDAH BASUDARA!", "2021-08-17T08:00:00Z", 28800, 7900000, 620000, 68000, "Spesial hari kemerdekaan maraton menamatkan sepuluh judul game legendaris.", 20),
    ("3wW2q1R5eF6", "QnA 5 JUTA SUBSCRIBER - MEMBACA PERTANYAAN PALING ANEH DARI AUDIENS", "2022-02-14T11:00:00Z", 4500, 3900000, 250000, 21000, "Menjawab berbagai pertanyaan seputar perjalanan karir, masa lalu, dan rencana masa depan.", 24),
    ("2vV1p0Q4fG7", "REAKSI LIVE EVENT FORTNITE - PULAU TENGGELAM DAN ROBOT MECHA MUNCUL!", "2021-12-05T15:00:00Z", 3900, 3600000, 220000, 17500, "Menyaksikan penutupan season festival live event spektakuler di dalam game Fortnite.", 20),
    ("1uU0o9P3gH8", "UNBOXING DIAMOND PLAY BUTTON YOUTUBE RESMI - MIMPI JADI KENYATAAN!", "2023-06-10T12:00:00Z", 3600, 6500000, 520000, 48000, "Membuka kotak penghargaan 10 juta subscriber dari YouTube bersama keluarga dan tim.", 24),
    ("0tT9n8O2hI9", "STREAM ULANG TAHUN WINDAH KE-31 - POTONG TUMPENG DAN TIUP LILIN!", "2023-02-25T13:00:00Z", 10800, 4800000, 340000, 31000, "Perayaan hari ulang tahun bersama ratusan ribu penonton yang hadir di room streaming.", 24),
    ("9sS8m7N1iJ0", "MEET AND GREET BOCIL KEMATIAN DI JAKARTA - SERU BANGET KETEMU KALIAN!", "2022-12-01T10:00:00Z", 2700, 4100000, 280000, 24000, "Vlog keseruan bertemu langsung dengan para fans dari berbagai kota di Indonesia.", 24)
]

# Expand to 120 total video records with authentic variations
additional_templates = [
    # (topic_prefix, title_pattern, desc_pattern, base_views, base_dur, cat_id)
    ("Horror", "CHILLA'S ART: THE COFFEE SHOP - MISTERI DI KEDAI KOPI KELAM", "Eksplorasi horror psikologis jepang.", 2800000, 4500, 20),
    ("Horror", "RESIDENT EVIL 7 BIOHAZARD - RUMAH KELUARGA BAKER BIKIN MERINDING", "Pelarian dari cengkeraman keluarga kanibal psikopat.", 3900000, 7200, 20),
    ("Horror", "THE CONJURING HOUSE - PENGUSIRAN SETAN PALING MENEGANGKAN", "Menghadapi entitas jahat di rumah berhantu klasik.", 2600000, 5100, 20),
    ("Horror", "SILENT HILL 2 REMAKE - KEMBALI KE KOTA KABUT PENUH KUTUKAN", "James Sunderland mencari mendiang istrinya di kota misterius.", 4400000, 7800, 20),
    ("Horror", "SLENDER RISING - TERSESAT DI RUMAH SAKIT JIWA ANGKER", "Misi bertahan hidup menghindari Slender di koridor gelap.", 2300000, 3900, 20),
    ("Horror", "DEAD BY DAYLIGHT - SURVIVOR KITA KERJAIN KILLER SAMPAI BINGUNG!", "Mabar multiplayer bertahan hidup memperbaiki generator.", 3100000, 5600, 20),
    ("Horror", "THE FOREST - BERTAHAN HIDUP DARI KANIBAL PULAU TERPENCIL", "Membangun benteng pertahanan dari serangan suku liar hutan.", 3500000, 6400, 20),
    ("Horror", "SONS OF THE FOREST - KELVIN DAN VIRGINIA TEMAN SETIA DI PULAU", "Lanjutan survival horror menjelajahi bunker tersembunyi.", 3800000, 6900, 20),
    ("Horror", "AMNESIA THE BUNKER - TERPERANGKAP DI BUNGKER PD1 BERSAMA MONSTER", "Bertahan hidup dengan lentera dynamo dan amunisi terbatas.", 2900000, 4900, 20),
    ("Horror", "DEVOUR - UPACARA PENGUSIRAN IBLIS AZAZEL SAMPAI BERSIH!", "Menangkap kambing kurban sebelum anggota sekte mengamuk.", 3300000, 4700, 20),
    ("Horror", "LUNCH LADY - IBU KANTIN GILA MENGEJAR KITA DENGAN PENGGORENGAN!", "Mencari lembar kunci ujian di lorong sekolah angker.", 3600000, 4200, 20),
    ("Horror", "PACIFY - MENYELAMATKAN ANAK GADIS DARI KUTUKAN BONEKA IBLIS", "Membakar boneka di tungku perapian rumah tua.", 3200000, 4600, 20),

    ("Simulator", "KAMPUNG BOYS SIMULATOR - JADI BOCAH PETUALANG DI DESA INDONESIA", "Mandi di sungai dan berburu belalang bareng teman desa.", 4100000, 5200, 20),
    ("Simulator", "TOILET MANAGEMENT SIMULATOR - BISNIS TOILET UMUM OMZET RATUSAN JUTA", "Menjaga kebersihan dan pasang tarif toilet terkocak.", 3400000, 4600, 20),
    ("Simulator", "POLICE SIMULATOR PATROL OFFICERS - TILANG PENGEMUDI NGEBUT DI JALAN", "Operasi zebra menjaga ketertiban lalu lintas kota.", 3600000, 5800, 20),
    ("Simulator", "CONSTRUCTION SIMULATOR - NGEBEKO DAN NGEPASAH JALAN RAYA BESAR", "Mengoperasikan alat berat eskavator dan buldoser proyek.", 2900000, 6200, 20),
    ("Simulator", "HOUSE FLIPPER 2 - RENOVASI RUMAH KUMUH JADI VILLA MEWAH SULTAN", "Mengecat dinding, pasang keramik dan tata perabotan modern.", 4200000, 6500, 20),
    ("Simulator", "COOKING SIMULATOR - RESTORAN BINTANG LIMA KITA BAKAR DAPURNYA!", "Membuat steak wagyu dengan taburan bumbu rempah rahasia.", 3700000, 5100, 20),
    ("Simulator", "POWERWASH SIMULATOR - SEMPROT AIR TEKANAN TINGGI SAMPAI KINCLONG", "Membersihkan taman bermain dan mobil antik penuh lumpur.", 3500000, 5900, 20),
    ("Simulator", "THIEF SIMULATOR 2 - MENJADI PENCURI PROFESIONAL DENGAN ALAT CANGGIH", "Menyelinap ke perumahan elit mengambil barang berharga.", 4000000, 6300, 20),
    ("Simulator", "DEALERSHIP SIMULATOR - BUKA SHOWROOM MOBIL SPORT TERMEGAH DI KOTA", "Menjual supercar dan melayani pembeli kelas atas.", 3800000, 5400, 20),
    ("Simulator", "AIRPORT CEO - MEMBANGUN BANDARA INTERNASIONAL DENGAN FASILITAS VIP", "Mengatur jadwal penerbangan dan bagasi penumpang pesawat.", 2500000, 6800, 20),
    ("Simulator", "AQUARIUM DESIGNER - DEKORASI AQUARIUM IKAN HIAS AIR TAWAR CANTIK", "Menata terumbu karang dan memelihara ikan eksotis langka.", 2800000, 4300, 20),
    ("Simulator", "PET SHOP SIMULATOR - JUALAN KUCING DAN ANJING LUCU BIKIN GEMAS", "Merawat anak bulu dan memberi makan hewan peliharaan.", 3900000, 4900, 20),

    ("Adventure", "ASSASSIN'S CREED MIRAGE - BASIM BERBURU TARGET DI KOTA BAGHDAD", "Menyelinap di pasar kuno dan lompat dari atas kubah masjid.", 3700000, 7100, 20),
    ("Adventure", "CYBERPUNK 2077 PHANTOM LIBERTY - MASUK KE DOGTOWN BARENG REED", "Misi spionase rahasia menyelamatkan presiden NUSA di Night City.", 4300000, 8400, 20),
    ("Adventure", "HOGWARTS LEGACY - MASUK ASRAMA GRYFFINDOR BELAJAR SIHIR KUNO", "Menerbangkan sapu terbang dan duel mantra melawan penyihir hitam.", 5100000, 8900, 20),
    ("Adventure", "STAR WARS JEDI SURVIVOR - CAL KESTIS MENGHADAPI IMPERIAL INQUISITOR", "Pertarungan lightsaber dan kekuatan force melintasi galaksi.", 3600000, 7500, 20),
    ("Adventure", "MONSTER HUNTER WORLD - BERBURU NERGIGANTE SAMPAI MAMPUS!", "Menempa pedang raksasa dan berburu monster naga legendaris.", 3900000, 7900, 20),
    ("Adventure", "THE WITCHER 3 WILD HUNT - GERALT OF RIVIA MENCARI CIRI DI VELEN", "Melacak monster rawa dan menuntaskan kontrak pemburu hadiah.", 4200000, 9100, 20),
    ("Adventure", "UNCHARTED 4 A THIEF'S END - NATHAN DRAKE BERBURU HARTA KARUN PIRUS", "Petualangan menyusuri kepulauan Madagaskar mencari Libertalia.", 4600000, 8100, 20),
    ("Adventure", "FAR CRY 3 - KITA HADAPI VAAS MONTENEGRO PENJAHAT PSIKOPAT", "Definisi kegilaan di pulau tropis Rook Islands.", 4000000, 7300, 20),
    ("Adventure", "SEKIRO SHADOWS DIE TWICE - PEDANG KEMATIAN MELAWAN ISSHIN ASHINA", "Adu tangkis parry sempurna tanpa cela melawan bos pedang kenshin.", 4500000, 9600, 20),
    ("Adventure", "TEKKEN 8 STORY MODE - JIN KAZAMA VS KAZUYA MISHIMA PERANG IBLIS!", "Pertarungan tinju bela diri keluarga Mishima di panggung dunia.", 4100000, 6800, 20),
    ("Adventure", "FINAL FANTASY VII REBIRTH - CLOUD DAN TIFA MELANJUTKAN PERJALANAN", "Menjelajahi dunia luas Gaia melawan Sephiroth yang bangkit.", 4700000, 8500, 20),
    ("Adventure", "HORIZON FORBIDDEN WEST - ALOY MENJELAJAHI TANAH TERLARANG BARAT", "Menjinakkan robot dinosaurus dengan busur panah presisi tinggi.", 3800000, 7600, 20),

    ("Multiplayer", "MOBILE LEGENDS - FANNY KABEL LAYANG-LAYANG RETREAT SAMBIL KILL", "Gameplay mekanik tinggi menggunakan assassin Fanny di Land of Dawn.", 4900000, 4100, 20),
    ("Multiplayer", "ROBLOX - SURVIVE THE NATURAL DISASTER BARENG RATUSAN BOCIL", "Menghindari tsunami, tornado dan gempa bumi di pulau terbang.", 5300000, 3900, 20),
    ("Multiplayer", "BRAWL STARS - PUSH TROPHY PAKE BRAWLER MORTIS SAMPAI RANGKUM", "Duel cepat 3 lawan 3 merebut permata di Gem Grab.", 3600000, 3700, 20),
    ("Multiplayer", "VALORANT INDONESIA - MAIN REYNA ACE 5 KILL DI MAP ASCENT!", "Adu aim tembak kepala satu tap vandal bersama kawan mabar.", 4400000, 5200, 20),
    ("Multiplayer", "COUNTER STRIKE 2 - CLUTCH 1 LAWAN 4 PASANG BOM DI DE_DUST2", "Nostalgia tembak-menembak kompetitif dengan engine Source 2.", 3800000, 5600, 20),
    ("Multiplayer", "APEX LEGENDS - OCTANE SPRINTING MASUK RING JUARA CHAMPION!", "Pergerakan lincah dan tembakan kombinasi senjata R-99 dan Peacekeeper.", 3500000, 5400, 20),
    ("Multiplayer", "FORTNITE BATTLE ROYALE - BUILD BATTLE SULTAN REBUTAN VICTORY ROYALE", "Tembak lompat shotgun dan pasang tembok kayu cepat.", 4200000, 4600, 20),
    ("Multiplayer", "OVERWATCH 2 - REINHARDT SHIELD BADAK JALAN MAJU TANPA MUNDUR", "Pahlawan tank Jerman dengan palu roket andalan.", 3100000, 4800, 20),
    ("Multiplayer", "LEAGUE OF LEGENDS WILD RIFT - YASUO HASAGI SULTAN MID LANE GG", "Kombinasi angin tornado dan pedang angin membelah formasi musuh.", 3400000, 4300, 20),
    ("Multiplayer", "DEAD BY DAYLIGHT SQUAD - MENYELAMATKAN TEMAN DARI GANTUNGAN KAIT", "Kerjasama tim yang solid melarikan diri lewat pintu gerbang keluar.", 3200000, 4900, 20),
    ("Multiplayer", "RAGDOLL DUEL BARENG TEMAN - FISIKA KARAKTER BIKIN KETAWA LEPAS", "Adu dorong karakter lemas di atas gedung tinggi.", 4600000, 3600, 20),
    ("Multiplayer", "PARTY ANIMALS - KELINCI VS ANJING BERANTEM PEREBUTAN KUE", "Karakter hewan lucu bertarung dengan tinju elastis yang menggemaskan.", 4900000, 4400, 20),

    ("Special", "REAKSI MEME WINDAH BASUDARA REDDIT & DISCORD - NGAKAK SAMPAI SESAK", "Kumpulan meme parodi paling kocak dari para subscriber kreatif.", 5400000, 4300, 24),
    ("Special", "VLOG PULANG KAMPUNG KE MANADO - KULINERAN IKAN BAKAR & TINUTUAN", "Kembali ke tanah kelahiran bersilaturahmi dan mencicipi masakan khas.", 4200000, 3800, 24),
    ("Special", "LIVE STREAMING MALAM TAHUN BARU - NONGKRONG DAN COUNTDOWN 2024", "Menyambut tahun baru bersama jutaan bocil kematian di seluruh dunia.", 6100000, 14400, 24),
    ("Special", "UNBOXING HADIAH FANS DARI SELURUH INDONESIA - ADA YANG KIRIM INI!", "Membuka kado kiriman fans dari Sabang sampai Merauke.", 4600000, 4200, 24),
    ("Special", "BERKUNJUNG KE KANTOR GOOGLE INDONESIA - KELILING STUDIO YOUTUBE", "Kunjungan resmi kreator konten ke kantor pusat YouTube Jakarta.", 3800000, 3100, 24),
    ("Special", "MASAK BESAR BARENG BOBON SANTOSO - BIKIN RENDANG WAGYU RAKSASA!", "Kolaborasi masak porsi jumbo bersama koki petualang.", 7200000, 5800, 24),
    ("Special", "PODCAST BARENG DEDDY CORBUZIER - CERITA PERJUANGAN DARI NOL", "Bincang mendalam tentang dedikasi konsistensi dan kesehatan mental.", 8500000, 6200, 24),
    ("Special", "REAKSI KLIP LIVE STREAM PALING MEMALUKAN WINDAH BASUDARA", "Nonton momen awkward dan blunder kocak selama 4 tahun streaming.", 5100000, 3900, 24),
    ("Special", "SPESIAL VALENTINE - MENCARI JODOH DI GAME KENCAN ONLINE KOCAK", "Eksperimen ngobrol di simulasi dating visual novel penuh tawa.", 3900000, 4600, 24),
    ("Special", "WISUDA WINDAH BASUDARA - MOMEN TERHARU BERSAMA ORANG TUA", "Rasa syukur menuntaskan pendidikan setelah perjuangan panjang.", 5800000, 2900, 24),
    ("Special", "NOBAR FINAL LIGA CHAMPIONS REAL MADRID VS DORTMUND - HISTORIS!", "Sorak gembira menyaksikan gol sundulan Carvajal dan Vinicius.", 5700000, 9200, 17),
    ("Special", "MARATON STREAM 24 JAM UNTUK AMAL - TERKUMPUL DANA BANTUAN BENCANA", "Aksi kemanusiaan membantu korban bencana alam di tanah air.", 8900000, 86400, 24)
]

start_date = datetime(2020, 1, 15)
video_rows = []

# Add base seed videos
for item in VIDEOS_SEED:
    video_rows.append({
        "video_id": item[0],
        "title": item[1],
        "published_at": item[2],
        "duration_seconds": item[3],
        "view_count": item[4],
        "like_count": item[5],
        "comment_count": item[6],
        "description": item[7],
        "category_id": item[8],
        "collected_at": "2026-10-29T10:00:00Z"
    })

# Add generated videos up to 125 total
counter = 0
for tmpl in additional_templates:
    counter += 1
    vid_id = f"wB{counter:03d}xY{random.randint(10,99)}"
    # Date spaced between 2020 and 2026
    days_offset = random.randint(30, 2400)
    pub_dt = start_date + timedelta(days=days_offset, hours=random.choice([11, 12, 13, 14, 15, 16, 17, 18, 19, 20]))
    pub_str = pub_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Add realistic variance (+- 20%)
    view_var = random.uniform(0.82, 1.25)
    views = int(tmpl[3] * view_var)
    likes = int(views * random.uniform(0.045, 0.075))
    comments = int(views * random.uniform(0.0035, 0.0085))
    duration = int(tmpl[4] * random.uniform(0.9, 1.15))

    video_rows.append({
        "video_id": vid_id,
        "title": tmpl[1],
        "published_at": pub_str,
        "duration_seconds": duration,
        "view_count": views,
        "like_count": likes,
        "comment_count": comments,
        "description": f"{tmpl[2]} Bersama Windah Basudara.",
        "category_id": tmpl[5],
        "collected_at": "2026-10-29T10:00:00Z"
    })

# Write videos seed CSV
out_videos = Path("/home/kerja/Documents/analisis-yt-windah/data/samples/videos_seed.csv")
with open(out_videos, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "video_id", "title", "published_at", "duration_seconds",
        "view_count", "like_count", "comment_count", "description",
        "category_id", "collected_at"
    ])
    writer.writeheader()
    writer.writerows(video_rows)

print(f"Successfully generated {len(video_rows)} seed videos at {out_videos}")

# Now build 360+ authentic seed comments with sentiment labels: Positif, Netral, Negatif
POSITIVE_COMMENTS = [
    "Bang Windah emang selalu bikin hari-hari gua ceria, terhibur banget!",
    "Salut banget sama Bang Brando, streaming sambil donasi ratusan juta untuk panti asuhan.",
    "Ngakak guling-guling pas adegan dikejar hantu wkwkwk kocak parah!",
    "Terima kasih Bang Windah sudah menemani masa-masa sulit pas kuliah, sehat selalu bang!",
    "Definisi konten kreator panutan, selalu ramah dan humble sama siapapun.",
    "Gameplay horor paling seru ya cuma nonton Bang Windah, ekspresinya dapet banget.",
    "Paling suka pas Bang Windah ngomong 'Halo teman-teman dan bocil kematian', auto senyum.",
    "Kualitas streaming makin keren, audionya jernih dan interaksi sama fans juara!",
    "Bocil kematian bangga punya panutan sebaik dan sehebat Bang Windah.",
    "Gua gak pernah main game ini, tapi nonton Bang Windah jadi ketagihan nonton sampai habis.",
    "Keren banget bang tamatnya, kerja keras berjam-jam akhirnya membuahkan hasil!",
    "Respect setinggi-tingginya buat Bang Brando dan tim, karyanya selalu berbobot.",
    "Nonton Bang Windah adalah obat paling ampuh setelah seharian capek kerja.",
    "Gila ekspresi terkejutnya natural banget wkwk, bikin satu rumah ikutan ketawa.",
    "Gokil bang, strategi lu di match ini jenius banget! GG WP!",
    "Semoga rezeki Bang Windah makin melimpah dan berkah terus ya bang.",
    "Konten yang wajib ditonton sebelum tidur, mood booster terbaik se-Indonesia.",
    "Salut konsistensinya bang, dari dulu sampai sekarang vibe lucunya gak pernah luntur.",
    "Lucu banget pas cosplay karakter game wkwk, totalitas tanpa batas!",
    "Terima kasih atas hiburannya Bang Windah, doa terbaik selalu buat lu dan keluarga."
]

NEUTRAL_COMMENTS = [
    "Game ini rilis di platform PC atau cuma di console aja ya bang?",
    "Judul lagunya pas outro apa ya teman-teman? Mau cari di Spotify.",
    "Kira-kira besok jadwal live streaming jam berapa ya?",
    "Spek PC Bang Windah buat main game ini pake VGA apa ya kira-kira?",
    "Bang, nama developernya game ini dari Indonesia atau luar negeri ya?",
    "Total durasi tamat game ini berapa jam bang kalau main normal?",
    "Ada yang tau part sebelumnya link-nya ada di playlist mana?",
    "Ini game berbayar di Steam atau game gratis ya gaes?",
    "Bang nanti coba main game indie yang kemarin viral di Twitter.",
    "Game ini support subtitle bahasa Indonesia gak ya di settingannya?",
    "Berapa harga game ini di Steam sekarang teman-teman?",
    "Format videonya 1080p 60fps ya bang? Kelihatan mulus banget.",
    "Part 2 kira-kira diupload besok malam atau lusa bang?",
    "Apakah game ini butuh koneksi internet atau bisa offline?",
    "Siapa nama karakter cewek yang tadi ketemu di awal cutscene ya?",
    "Ini gamenya single player atau bisa co-op bareng teman?",
    "Bang coba cek opsi grafisnya, ada fitur DLSS atau FSR gak di menu setting?",
    "Info donasi charity-nya masih dibuka sampai jam berapa ya min?",
    "Lagu background pas lagi eksplorasi judulnya apa ya guys?",
    "Ada rekomendasi game simulator mirip ini gak di Play Store atau Steam?"
]

NEGATIVE_COMMENTS = [
    "Audionya kok agak mendem dan delay ya bang, mic-nya tolong dicek lagi.",
    "Kecewa banget kok gamenya gak ditamatin bang, padahal nungguin endingnya.",
    "Videonya patah-patah terus di menit ke-15 bang, FPS drop parah.",
    "Kurang seru gamenya, alur ceritanya ngebosenin dan muter-muter terus.",
    "Bang facecam-nya nutupin peta mini di pojok kiri bawah layar, geser dong.",
    "Chatnya toxic banget dari tadi banyak spam gak jelas, mod tolong bersihin.",
    "Boring banget gameplay kali ini, terlalu banyak grinding gak ada aksinya.",
    "Sayang banget suaranya game lebih kenceng daripada suara mic Bang Windah.",
    "Kualitas videonya blur banget padahal udah disetel 1080p, ada kompresi aneh.",
    "Gak suka sama endingnya, ceritanya gantung banget dan karakternya ngeselin.",
    "Bang tolong jangan sering skip cutscene penting dong, jadi gak paham ceritanya.",
    "Terlalu banyak sponsor di awal video bikin males nontonnya.",
    "Grafis gamenya jelek banget patah-patah, mending ganti game lain bang.",
    "Streaming hari ini sering buffer dan koneksinya DC mulu, sayang banget.",
    "Bosen bang main game ini terus tiap hari, variasi game lainnya dong.",
    "Suara gamenya pecah di telinga pas adegan ledakan, tolong volumenya dikecilin.",
    "Gak recommended beli game ini, bug-nya parah banget bikin crash.",
    "Sayang banget kenapa pilih opsi dialog yang jahat bang, padahal opsi baik lebih bagus.",
    "Bang kenapa videonya dipotong-potong, enakan versi utuh unedited kayak biasa.",
    "Agak kecewa sama pacing videonya, terlalu lambat dan kepanjangan."
]

comment_rows = []
c_id = 1
# Generate 450 balanced comments mapped across seed videos
categories_pool = [
    ("Positif", POSITIVE_COMMENTS),
    ("Netral", NEUTRAL_COMMENTS),
    ("Negatif", NEGATIVE_COMMENTS)
]

for i in range(150):
    for label, texts in categories_pool:
        base_text = random.choice(texts)
        # Add slight natural comment variation
        suffixes = ["", " 👍", " 🙏", " mantap!", " wkwk", " min.", " bang.", " gokil sih."]
        full_text = base_text + random.choice(suffixes)
        assigned_vid = random.choice(video_rows)["video_id"]
        likes_count = random.randint(2, 3500) if label == "Positif" else random.randint(0, 450)
        
        pub_dt = datetime(2023, random.randint(1, 12), random.randint(1, 28), random.randint(0, 23), random.randint(0, 59))
        
        comment_rows.append({
            "comment_id": f"Ugx{c_id:06d}{random.randint(100,999)}",
            "video_id": assigned_vid,
            "comment_text": full_text,
            "like_count": likes_count,
            "published_at": pub_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "collected_at": "2026-10-29T10:00:00Z",
            "sentiment_label": label
        })
        c_id += 1

out_comments = Path("/home/kerja/Documents/analisis-yt-windah/data/samples/comments_seed.csv")
with open(out_comments, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "comment_id", "video_id", "comment_text", "like_count",
        "published_at", "collected_at", "sentiment_label"
    ])
    writer.writeheader()
    writer.writerows(comment_rows)

print(f"Successfully generated {len(comment_rows)} seed comments at {out_comments}")
