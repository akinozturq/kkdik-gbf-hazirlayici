"""
KKDİK (TR) ve REACH Annex II (EN) Dil & Çeviri Servisi
Tüm 16 Bölüm başlıkları, alt başlıkları, etiket unsurları ve standart ifadeleri içerir.
"""

from typing import Dict, Any, Optional, List

# REACH Annex II Resmi 16 Bölüm ve Alt Başlıkları
SECTIONS_EN = {
    "title": "SAFETY DATA SHEET",
    "subtitle": "According to Regulation (EC) No. 1907/2006 (REACH), Annex II and Regulation (EC) No. 1272/2008 (CLP)",
    "meta": {
        "compilation_date": "Compilation Date",
        "revision_date": "Revision Date",
        "revision_no": "Revision No",
        "form_no": "Document / Form No",
        "page": "Page",
        "of": "of",
    },
    "s1": {
        "title": "SECTION 1: Identification of the substance/mixture and of the company/undertaking",
        "s1_1": "1.1. Product identifier",
        "product_name": "Product Name / Identifier",
        "trade_code": "Trade / Stock Code",
        "cas_ec": "CAS & EC No",
        "reach_reg": "REACH Registration No",
        "s1_2": "1.2. Relevant identified uses of the substance or mixture and uses advised against",
        "identified_uses": "Identified relevant uses",
        "uses_advised_against": "Uses advised against",
        "s1_3": "1.3. Details of the supplier of the safety data sheet",
        "supplier_name": "Company / Supplier Name",
        "address": "Address",
        "phone": "Telephone",
        "email": "E-mail (Competent Person)",
        "website": "Web",
        "s1_4": "1.4. Emergency telephone number",
        "emergency_phone": "Emergency Phone Number",
        "emergency_info": "National Poison Information Center / Emergency Service"
    },
    "s2": {
        "title": "SECTION 2: Hazards identification",
        "s2_1": "2.1. Classification of the substance or mixture",
        "not_classified": "Not classified as hazardous according to Regulation (EC) No 1272/2008 [CLP].",
        "s2_2": "2.2. Label elements",
        "pictograms": "Hazard Pictograms",
        "no_pictogram": "No GHS Pictogram required",
        "signal_word": "Signal Word",
        "hazard_statements": "Hazard Statements (H)",
        "precautionary_statements": "Precautionary Statements (P)",
        "danger": "Danger",
        "warning": "Warning",
        "none": "None",
        "s2_3": "2.3. Other hazards",
        "pbt_vpvb": "Does not contain PBT or vPvB substances in accordance with REACH Annex XIII."
    },
    "s3": {
        "title": "SECTION 3: Composition/information on ingredients",
        "s3_1": "3.1. Substances",
        "chemical_identity": "Chemical Identity",
        "s3_2": "3.2. Mixtures",
        "table": {
            "comp_name": "Component Name",
            "cas_no": "CAS No",
            "ec_no": "EC No",
            "reg_no": "Registration No",
            "concentration": "Concentration (%)",
            "classification": "Classification (CLP / GHS)"
        },
        "no_hazardous_ingredients": "Contains no hazardous substances exceeding reporting thresholds."
    },
    "s4": {
        "title": "SECTION 4: First aid measures",
        "s4_1": "4.1. Description of first aid measures",
        "inhalation": "Following inhalation",
        "skin": "Following skin contact",
        "eye": "Following eye contact",
        "ingestion": "Following ingestion",
        "protection": "Self-protection of first aider",
        "s4_2": "4.2. Most important symptoms and effects, both acute and delayed",
        "s4_3": "4.3. Indication of any immediate medical attention and special treatment needed",
        "symptomatic_treatment": "Treat symptomatically and supportively."
    },
    "s5": {
        "title": "SECTION 5: Firefighting measures",
        "s5_1": "5.1. Extinguishing media",
        "suitable_media": "Suitable extinguishing media",
        "unsuitable_media": "Unsuitable extinguishing media",
        "s5_2": "5.2. Special hazards arising from the substance or mixture",
        "s5_3": "5.3. Advice for firefighters",
        "fire_protection": "Wear self-contained breathing apparatus (SCBA) and full protective gear."
    },
    "s6": {
        "title": "SECTION 6: Accidental release measures",
        "s6_1": "6.1. Personal precautions, protective equipment and emergency procedures",
        "non_emergency": "For non-emergency personnel",
        "emergency_responders": "For emergency responders",
        "s6_2": "6.2. Environmental precautions",
        "s6_3": "6.3. Methods and material for containment and cleaning up",
        "s6_4": "6.4. Reference to other sections",
        "see_sections": "See Section 8 for personal protective equipment and Section 13 for waste disposal."
    },
    "s7": {
        "title": "SECTION 7: Handling and storage",
        "s7_1": "7.1. Precautions for safe handling",
        "s7_2": "7.2. Conditions for safe storage, including any incompatibilities",
        "s7_3": "7.3. Specific end use(s)",
        "no_extra_uses": "No specific end uses other than those specified in Section 1.2."
    },
    "s8": {
        "title": "SECTION 8: Exposure controls/personal protection",
        "s8_1": "8.1. Control parameters",
        "table": {
            "substance": "Substance / Component",
            "limit_value": "Occupational Exposure Limit (TWA / STEL / Note)",
            "legal_basis": "Legal Basis / Standard"
        },
        "no_limits": "Contains no substances with occupational exposure limit values.",
        "s8_2": "8.2. Exposure controls",
        "engineering_controls": "Appropriate engineering controls",
        "ppe": "Individual protection measures, such as personal protective equipment (PPE)",
        "eye_protection": "Eye/face protection",
        "hand_protection": "Hand protection (Gloves)",
        "skin_protection": "Skin and body protection",
        "respiratory_protection": "Respiratory protection",
        "thermal_hazards": "Thermal hazards",
        "environmental_controls": "Environmental exposure controls"
    },
    "s9": {
        "title": "SECTION 9: Physical and chemical properties",
        "s9_1": "9.1. Information on basic physical and chemical properties",
        "props": {
            "appearance": "a) Appearance (Physical state, colour)",
            "odour": "b) Odour",
            "odour_threshold": "c) Odour threshold",
            "ph": "d) pH",
            "melting_point": "e) Melting point / Freezing point",
            "boiling_point": "f) Initial boiling point and boiling range",
            "flash_point": "g) Flash point",
            "evaporation_rate": "h) Evaporation rate",
            "flammability": "i) Flammability (solid, gas)",
            "explosive_limits": "j) Upper/lower flammability or explosive limits",
            "vapour_pressure": "k) Vapour pressure",
            "vapour_density": "l) Vapour density",
            "relative_density": "m) Relative density",
            "solubility": "n) Solubility(ies)",
            "partition_coeff": "o) Partition coefficient: n-octanol/water",
            "auto_ignition": "p) Auto-ignition temperature",
            "decomposition": "q) Decomposition temperature",
            "viscosity": "r) Viscosity",
            "explosive_props": "s) Explosive properties",
            "oxidising_props": "t) Oxidising properties"
        },
        "not_determined": "Not determined",
        "not_applicable": "Not applicable",
        "not_explosive": "Not explosive",
        "not_oxidising": "Not oxidising",
        "s9_2": "9.2. Other information"
    },
    "s10": {
        "title": "SECTION 10: Stability and reactivity",
        "s10_1": "10.1. Reactivity",
        "no_reactivity": "No hazardous reactions known under normal conditions of use.",
        "s10_2": "10.2. Chemical stability",
        "stable": "Stable under recommended storage and handling conditions.",
        "s10_3": "10.3. Possibility of hazardous reactions",
        "no_hazardous_reactions": "No dangerous reactions known under normal conditions of use.",
        "s10_4": "10.4. Conditions to avoid",
        "s10_5": "10.5. Incompatible materials",
        "s10_6": "10.6. Hazardous decomposition products",
        "no_decomp": "No hazardous decomposition products known under normal conditions of storage."
    },
    "s11": {
        "title": "SECTION 11: Toxicological information",
        "s11_1": "11.1. Information on hazard classes as defined in Regulation (EC) No 1272/2008",
        "acute_tox": "Acute toxicity",
        "skin_corr": "Skin corrosion/irritation",
        "eye_damage": "Serious eye damage/irritation",
        "sensitisation": "Respiratory or skin sensitisation",
        "mutagenicity": "Germ cell mutagenicity",
        "carcinogenicity": "Carcinogenicity",
        "repr_tox": "Reproductive toxicity",
        "stot_se": "STOT-single exposure",
        "stot_re": "STOT-repeated exposure",
        "aspiration": "Aspiration hazard",
        "s11_2": "11.2. Information on other hazards"
    },
    "s12": {
        "title": "SECTION 12: Ecological information",
        "s12_1": "12.1. Toxicity",
        "s12_2": "12.2. Persistence and degradability",
        "s12_3": "12.3. Bioaccumulative potential",
        "s12_4": "12.4. Mobility in soil",
        "s12_5": "12.5. Results of PBT and vPvB assessment",
        "s12_6": "12.6. Endocrine disrupting properties",
        "s12_7": "12.7. Other adverse effects"
    },
    "s13": {
        "title": "SECTION 13: Disposal considerations",
        "s13_1": "13.1. Waste treatment methods",
        "waste_advice": "Dispose of in accordance with European Directive on waste 2008/98/EC and local regulations."
    },
    "s14": {
        "title": "SECTION 14: Transport information",
        "s14_1": "14.1. UN number",
        "s14_2": "14.2. UN proper shipping name",
        "s14_3": "14.3. Transport hazard class(es)",
        "s14_4": "14.4. Packing group",
        "s14_5": "14.5. Environmental hazards",
        "s14_6": "14.6. Special precautions for user",
        "s14_7": "14.7. Maritime transport in bulk according to IMO instruments",
        "not_dangerous_goods": "Not dangerous goods according to transport regulations (ADR, RID, IMDG, IATA)."
    },
    "s15": {
        "title": "SECTION 15: Regulatory information",
        "s15_1": "15.1. Safety, health and environmental regulations/legislation specific for the substance or mixture",
        "s15_2": "15.2. Chemical safety assessment",
        "csa_not_carried_out": "No chemical safety assessment has been carried out for this substance/mixture."
    },
    "s16": {
        "title": "SECTION 16: Other information",
        "h_statements_full": "Full text of H- and EUH-statements referred to under sections 2 and 3",
        "abbreviations": "Abbreviations and acronyms",
        "training_advice": "Training advice",
        "disclaimer": "The information provided in this Safety Data Sheet is correct to the best of our knowledge, information and belief at the date of its publication."
    }
}

# H İfadeleri İngilizce Karşılıkları (CLP / GHS Regulation (EC) No 1272/2008)
H_STATEMENTS_EN = {
    "H200": "Unstable explosives.",
    "H201": "Explosive; mass explosion hazard.",
    "H202": "Explosive, severe projection hazard.",
    "H203": "Explosive; fire, blast or projection hazard.",
    "H204": "Fire or projection hazard.",
    "H205": "May mass explode in fire.",
    "H220": "Extremely flammable gas.",
    "H221": "Flammable gas.",
    "H222": "Extremely flammable aerosol.",
    "H223": "Flammable aerosol.",
    "H224": "Extremely flammable liquid and vapour.",
    "H225": "Highly flammable liquid and vapour.",
    "H226": "Flammable liquid and vapour.",
    "H228": "Flammable solid.",
    "H240": "Heating may cause an explosion.",
    "H241": "Heating may cause a fire or explosion.",
    "H242": "Heating may cause a fire.",
    "H250": "Catches fire spontaneously if exposed to air.",
    "H251": "Self-heating: may catch fire.",
    "H252": "Self-heating in large quantities; may catch fire.",
    "H260": "In contact with water releases flammable gases which may ignite spontaneously.",
    "H261": "In contact with water releases flammable gases.",
    "H270": "May cause or intensify fire; oxidiser.",
    "H271": "May cause fire or explosion; strong oxidiser.",
    "H272": "May intensify fire; oxidiser.",
    "H280": "Contains gas under pressure; may explode if heated.",
    "H281": "Contains refrigerated gas; may cause cryogenic burns or injury.",
    "H290": "May be corrosive to metals.",
    "H300": "Fatal if swallowed.",
    "H301": "Toxic if swallowed.",
    "H302": "Harmful if swallowed.",
    "H304": "May be fatal if swallowed and enters airways.",
    "H310": "Fatal in contact with skin.",
    "H311": "Toxic in contact with skin.",
    "H312": "Harmful in contact with skin.",
    "H314": "Causes severe skin burns and eye damage.",
    "H315": "Causes skin irritation.",
    "H317": "May cause an allergic skin reaction.",
    "H318": "Causes serious eye damage.",
    "H319": "Causes serious eye irritation.",
    "H330": "Fatal if inhaled.",
    "H331": "Toxic if inhaled.",
    "H332": "Harmful if inhaled.",
    "H334": "May cause allergy or asthma symptoms or breathing difficulties if inhaled.",
    "H335": "May cause respiratory irritation.",
    "H336": "May cause drowsiness or dizziness.",
    "H340": "May cause genetic defects.",
    "H341": "Suspected of causing genetic defects.",
    "H350": "May cause cancer.",
    "H350i": "May cause cancer by inhalation.",
    "H351": "Suspected of causing cancer.",
    "H360": "May damage fertility or the unborn child.",
    "H360D": "May damage the unborn child.",
    "H360F": "May damage fertility.",
    "H360FD": "May damage fertility. May damage the unborn child.",
    "H360Df": "May damage the unborn child. Suspected of damaging fertility.",
    "H361": "Suspected of damaging fertility or the unborn child.",
    "H361d": "Suspected of damaging the unborn child.",
    "H361f": "Suspected of damaging fertility.",
    "H362": "May cause harm to breast-fed children.",
    "H370": "Causes damage to organs.",
    "H371": "May cause damage to organs.",
    "H372": "Causes damage to organs through prolonged or repeated exposure.",
    "H373": "May cause damage to organs through prolonged or repeated exposure.",
    "H400": "Very toxic to aquatic life.",
    "H410": "Very toxic to aquatic life with long lasting effects.",
    "H411": "Toxic to aquatic life with long lasting effects.",
    "H412": "Harmful to aquatic life with long lasting effects.",
    "H413": "May cause long lasting harmful effects to aquatic life.",
    "EUH066": "Repeated exposure may cause skin dryness or cracking.",
    "EUH208": "Contains substance. May produce an allergic reaction.",
    "EUH210": "Safety data sheet available on request."
}

# P Önlem İfadeleri İngilizce Karşılıkları
P_STATEMENTS_EN = {
    "P101": "If medical advice is needed, have product container or label at hand.",
    "P102": "Keep out of reach of children.",
    "P103": "Read carefully and follow all instructions.",
    "P201": "Obtain special instructions before use.",
    "P202": "Do not handle until all safety precautions have been read and understood.",
    "P210": "Keep away from heat, hot surfaces, sparks, open flames and other ignition sources. No smoking.",
    "P211": "Do not spray on an open flame or other ignition source.",
    "P220": "Keep away from clothing and other combustible materials.",
    "P233": "Keep container tightly closed.",
    "P240": "Ground and bond container and receiving equipment.",
    "P241": "Use explosion-proof electrical/ventilating/lighting equipment.",
    "P242": "Use non-sparking tools.",
    "P243": "Take action to prevent static discharges.",
    "P260": "Do not breathe dust/fume/gas/mist/vapours/spray.",
    "P261": "Avoid breathing dust/fume/gas/mist/vapours/spray.",
    "P264": "Wash contaminated skin thoroughly after handling.",
    "P270": "Do not eat, drink or smoke when using this product.",
    "P271": "Use only outdoors or in a well-ventilated area.",
    "P273": "Avoid release to the environment.",
    "P280": "Wear protective gloves/protective clothing/eye protection/face protection.",
    "P301+P310": "IF SWALLOWED: Immediately call a POISON CENTER or doctor/physician.",
    "P301+P312": "IF SWALLOWED: Call a POISON CENTER or doctor/physician if you feel unwell.",
    "P301+P330+P331": "IF SWALLOWED: Rinse mouth. Do NOT induce vomiting.",
    "P302+P352": "IF ON SKIN: Wash with plenty of water and soap.",
    "P303+P361+P353": "IF ON SKIN (or hair): Take off immediately all contaminated clothing. Rinse skin with water [or shower].",
    "P304+P340": "IF INHALED: Remove person to fresh air and keep comfortable for breathing.",
    "P305+P351+P338": "IF IN EYES: Rinse cautiously with water for several minutes. Remove contact lenses, if present and easy to do. Continue rinsing.",
    "P308+P311": "IF exposed or concerned: Call a POISON CENTER or doctor/physician.",
    "P308+P313": "IF exposed or concerned: Get medical advice/attention.",
    "P312": "Call a POISON CENTER or doctor/physician if you feel unwell.",
    "P314": "Get medical advice/attention if you feel unwell.",
    "P321": "Specific treatment (see medical advice on this label).",
    "P331": "Do NOT induce vomiting.",
    "P332+P313": "If skin irritation occurs: Get medical advice/attention.",
    "P337+P313": "If eye irritation persists: Get medical advice/attention.",
    "P361+P364": "Take off immediately all contaminated clothing and wash it before reuse.",
    "P362+P364": "Take off contaminated clothing and wash it before reuse.",
    "P370+P378": "In case of fire: Use water spray, alcohol-resistant foam, dry chemical or carbon dioxide to extinguish.",
    "P391": "Collect spillage.",
    "P403+P233": "Store in a well-ventilated place. Keep container tightly closed.",
    "P403+P235": "Store in a well-ventilated place. Keep cool.",
    "P405": "Store locked up.",
    "P501": "Dispose of contents/container to hazardous or special waste collection point in accordance with local/regional/national regulations."
}


SECTIONS_TR = {
    "title": "GÜVENLİK BİLGİ FORMU",
    "subtitle": "Zararlı Maddeler ve Karışımlara İlişkin Güvenlik Bilgi Formları Hakkında Yönetmelik (13.12.2014 - 29204 Resmi Gazete) ve KKDİK Uyarınca",
    "meta": {
        "compilation_date": "Hazırlama Tarihi",
        "revision_date": "Yenileme Tarihi",
        "revision_no": "Revizyon No",
        "form_no": "Form / GBF No",
        "page": "Sayfa",
        "of": "/",
    },
    "s1": {
        "title": "1. MADDENİN / KARIŞIMIN VE ŞİRKETİN / DAĞITICININ KİMLİĞİ",
        "s1_1": "1.1. Madde / Karışımın Kimliği",
        "product_name": "Madde / Karışım Adı",
        "trade_code": "Ticari / Stok Kodu",
        "cas_ec": "CAS & EC No",
        "reach_reg": "Kayıt / Muafiyet No",
        "s1_2": "1.2. Madde veya Karışımın Belirlenmiş Kullanımları ve Tavsiye Edilmeyen Kullanımları",
        "identified_uses": "Belirlenmiş Kullanımlar",
        "uses_advised_against": "Tavsiye Edilmeyen Kullanımlar",
        "s1_3": "1.3. Güvenlik Bilgi Formu Tedarikçisinin Bilgileri",
        "supplier_name": "Şirket / Tedarikçi Adı",
        "address": "Adres",
        "phone": "Telefon",
        "email": "E-posta (Yetkili Kişi)",
        "website": "Web",
        "s1_4": "1.4. Acil Durum Telefon Numarası",
        "emergency_phone": "Acil Durum Telefonu",
        "emergency_info": "Ulusal Zehir Danışma Merkezi (UZEM): 114 | Acil Sağlık: 112"
    },
    "s2": {
        "title": "2. ZARARLILIK TANIMLANMASI",
        "s2_1": "2.1. Madde veya Karışımın Sınıflandırılması",
        "not_classified": "SEA Yönetmeliği kriterlerine göre zararlı olarak sınıflandırılmamıştır.",
        "s2_2": "2.2. Etiket Unsurları",
        "pictograms": "Tehlike Piktogramları",
        "no_pictogram": "GHS Piktogramı Yok",
        "signal_word": "Uyarı Kelimesi",
        "hazard_statements": "Zararlılık İfadeleri (H)",
        "precautionary_statements": "Önlem İfadeleri (P)",
        "danger": "Tehlike",
        "warning": "Dikkat",
        "none": "Yok",
        "s2_3": "2.3. Diğer Zararlar",
        "pbt_vpvb": "PBT veya vPvB kriterlerini karşılamaz."
    },
    "s3": {
        "title": "3. BİLEŞİMİ / İÇİNDEKİLER HAKKINDA BİLGİ",
        "s3_1": "3.1. Maddeler",
        "chemical_identity": "Kimyasal Kimliği",
        "s3_2": "3.2. Karışımlar",
        "table": {
            "comp_name": "Bileşen Adı",
            "cas_no": "CAS No",
            "ec_no": "EC No",
            "reg_no": "Kayıt No",
            "concentration": "Konsantrasyon (%)",
            "classification": "Sınıflandırma (SEA / GHS)"
        },
        "no_hazardous_ingredients": "Zararlı sınır değerini aşan bileşen bildirilmemiştir."
    },
    "s4": {
        "title": "4. İLK YARDIM ÖNLEMLERİ",
        "s4_1": "4.1. İlk Yardım Önlemlerinin Açıklanması",
        "inhalation": "Solunması Halinde",
        "skin": "Cilt ile Teması Halinde",
        "eye": "Göz ile Teması Halinde",
        "ingestion": "Yutulması Halinde",
        "protection": "İlk yardım görevlisinin korunması",
        "s4_2": "4.2. Akut ve Sonradan Görülen Önemli Belirtiler ve Etkiler",
        "s4_3": "4.3. Tıbbi Müdahale ve Özel Tedavi Gereği İçin İlk İşaretler",
        "symptomatic_treatment": "Semptomatik tedavi uygulayınız."
    },
    "s5": {
        "title": "5. YANGINLA MÜCADELE ÖNLEMLERİ",
        "s5_1": "5.1. Yangın Söndürücüler",
        "suitable_media": "Uygun söndürücü maddeler",
        "unsuitable_media": "Güvenlik sebebiyle uygun olmayan söndürücüler",
        "s5_2": "5.2. Madde veya Karışımdan Kaynaklanan Özel Zararlar",
        "s5_3": "5.3. Yangın Söndürme Ekipleri İçin Tavsiyeler",
        "fire_protection": "Tam koruyucu giysi ve bağımsız solunum aparatı (SCBA) kullanınız."
    },
    "s6": {
        "title": "6. KAZA SONUCU YAYILMAYA KARŞI ÖNLEMLER",
        "s6_1": "6.1. Kişisel Önlemler, Koruyucu Donanım ve Acil Durum Prosedürleri",
        "non_emergency": "Acil durum personeli olmayanlar için",
        "emergency_responders": "Acil durumda müdahale edenler için",
        "s6_2": "6.2. Çevresel Önlemler",
        "s6_3": "6.3. Muhafaza Etme ve Temizleme İçin Yöntemler ve Materyaller",
        "s6_4": "6.4. Diğer Bölümlere Atıflar",
        "see_sections": "Kişisel korunma için Bölüm 8'e, bertaraf için Bölüm 13'e bakınız."
    },
    "s7": {
        "title": "7. ELLEÇLEME VE DEPOLAMA",
        "s7_1": "7.1. Güvenli Elleçleme İçin Önlemler",
        "s7_2": "7.2. Uyuşmazlıkları da İçeren Güvenli Depolama Koşulları",
        "s7_3": "7.3. Belirli Son Kullanımlar",
        "no_extra_uses": "Bölüm 1.2'de belirtilen alanlar içindir."
    },
    "s8": {
        "title": "8. MARUZ KALMA KONTROLLERİ / KİŞİSEL KORUNMA",
        "s8_1": "8.1. Kontrol Parametreleri",
        "table": {
            "substance": "Madde / Bileşen",
            "limit_value": "Mesleki Maruziyet Sınır Değeri (TWA / STEL / Not)",
            "legal_basis": "Yasal Dayanak / Standart"
        },
        "no_limits": "Tanımlı mesleki maruziyet sınır değeri bulunmamaktadır.",
        "s8_2": "8.2. Maruz Kalma Kontrolleri",
        "engineering_controls": "Uygun Mühendislik Kontrolleri",
        "ppe": "Bireysel Koruyucu Önlemler (Kişisel Koruyucu Donanım - KKD)",
        "eye_protection": "Göz / Yüz Koruması",
        "hand_protection": "Ellerin Korunması (Eldiven)",
        "skin_protection": "Cilt ve Vücut Koruması",
        "respiratory_protection": "Solunum Sisteminin Korunması",
        "thermal_hazards": "Isıl Zararlar",
        "environmental_controls": "Çevresel Maruz Kalma Kontrolleri"
    },
    "s9": {
        "title": "9. FİZİKSEL VE KİMYASAL ÖZELLİKLER",
        "s9_1": "9.1. Temel Fiziksel ve Kimyasal Özellikler Hakkında Bilgi",
        "props": {
            "appearance": "a) Görünüm (Fiziksel hal, renk)",
            "odour": "b) Koku",
            "odour_threshold": "c) Koku eşiği",
            "ph": "ç) pH",
            "melting_point": "d) Erime / Donma noktası",
            "boiling_point": "e) İlk kaynama noktası ve kaynama aralığı",
            "flash_point": "f) Parlama noktası",
            "evaporation_rate": "g) Buharlaşma hızı",
            "flammability": "ğ) Alevlenirlik (katı, gaz)",
            "explosive_limits": "h) Üst / Alt alevlenirlik veya patlayıcı limitleri",
            "vapour_pressure": "ı) Buhar basıncı",
            "vapour_density": "i) Buhar yoğunluğu",
            "relative_density": "j) Bağıl yoğunluk",
            "solubility": "k) Çözünürlük",
            "partition_coeff": "l) Dağılım katsayısı (n-oktanol/su)",
            "auto_ignition": "m) Kendiliğinden tutuşma sıcaklığı",
            "decomposition": "n) Bozunma sıcaklığı",
            "viscosity": "o) Akışkanlık (Viskozite)",
            "explosive_props": "ö) Patlayıcı özellikler",
            "oxidising_props": "p) Oksitleyici özellikler"
        },
        "not_determined": "Belirlenmemiştir",
        "not_applicable": "Uygulanamaz",
        "not_explosive": "Patlayıcı değildir",
        "not_oxidising": "Oksitleyici değildir",
        "s9_2": "9.2. Diğer Bilgiler"
    },
    "s10": {
        "title": "10. KARARLILIK VE TEPKİME",
        "s10_1": "10.1. Tepkime",
        "no_reactivity": "Normal koşullarda tehlikeli tepkime vermez.",
        "s10_2": "10.2. Kimyasal Kararlılık",
        "stable": "Önerilen depolama ve kullanım koşullarında kararlıdır.",
        "s10_3": "10.3. Zararlı Tepkime Olasılığı",
        "no_hazardous_reactions": "Normal kullanım ve depolama koşullarında tehlikeli reaksiyon bilinmemektedir.",
        "s10_4": "10.4. Kaçınılması Gereken Durumlar",
        "s10_5": "10.5. Kaçınılması Gereken Maddeler",
        "s10_6": "10.6. Zararlı Bozunma Ürünleri",
        "no_decomp": "Normal depolama koşullarında tehlikeli bozunma ürünleri oluşmaz."
    },
    "s11": {
        "title": "11. TOKSİKOLOJİK BİLGİLER",
        "s11_1": "11.1. Toksik Etkiler Hakkında Bilgi",
        "acute_tox": "Akut toksisite",
        "skin_corr": "Cilt aşınması/tahrişi",
        "eye_damage": "Ciddi göz hasarları/tahrişi",
        "sensitisation": "Solunum yolları veya cilt hassaslaşması",
        "mutagenicity": "Eşey hücre mutajenitesi",
        "carcinogenicity": "Kanserojenite",
        "repr_tox": "Üreme sistemi toksisitesi",
        "stot_se": "Belirli Hedef Organ Toksisitesi (Tek maruz kalma)",
        "stot_re": "Belirli Hedef Organ Toksisitesi (Tekrarlı maruz kalma)",
        "aspiration": "Aspirasyon zararı",
        "s11_2": "11.2. Diğer Zararlar Hakkında Bilgiler"
    },
    "s12": {
        "title": "12. EKOLOJİK BİLGİLER",
        "s12_1": "12.1. Toksisite",
        "s12_2": "12.2. Kalıcılık ve Bozunabilirlik",
        "s12_3": "12.3. Biyobirikim Potansiyeli",
        "s12_4": "12.4. Toprakta Hareketlilik",
        "s12_5": "12.5. PBT ve vPvB Değerlendirmesinin Sonuçları",
        "s12_6": "12.6. Endokrin Bozucu Özellikler",
        "s12_7": "12.7. Diğer Olumsuz Etkiler"
    },
    "s13": {
        "title": "13. BERTARAF ETME BİLGİLERİ",
        "s13_1": "13.1. Atık İşleme Yöntemleri",
        "waste_advice": "Atık Yönetmeliği ve yerel mevzuat hükümlerine uygun olarak lisanslı bertaraf tesislerinde bertaraf edilmelidir."
    },
    "s14": {
        "title": "14. TAŞIMACILIK BİLGİLERİ",
        "s14_1": "14.1. UN Numarası",
        "s14_2": "14.2. Uygun UN Taşımacılık Adı",
        "s14_3": "14.3. Taşımacılık Zararlılık Sınıf(lar)ı",
        "s14_4": "14.4. Ambalajlama Grubu",
        "s14_5": "14.5. Çevresel Zararlar",
        "s14_6": "14.6. Kullanıcı İçin Özel Önlemler",
        "s14_7": "14.7. MARPOL 73/78 Ek II ve IBC Koduna Göre Dökme Taşımacılık",
        "not_dangerous_goods": "Taşımacılık yönetmeliklerine göre (ADR, RID, IMDG, IATA) tehlikeli madde değildir."
    },
    "s15": {
        "title": "15. MEVZUAT BİLGİLERİ",
        "s15_1": "15.1. Madde veya Karışıma Özgü Güvenlik, Sağlık ve Çevre Mevzuatı",
        "s15_2": "15.2. Kimyasal Güvenlik Değerlendirmesi",
        "csa_not_carried_out": "Bu karışım/madde için kimyasal güvenlik değerlendirmesi yapılmamıştır."
    },
    "s16": {
        "title": "16. DİĞER BİLGİLER",
        "h_statements_full": "2. ve 3. Bölümlerde atıfta bulunulan H-ifadelerinin tam metni",
        "abbreviations": "Kısaltmalar ve akronimler",
        "training_advice": "Eğitim tavsiyeleri",
        "disclaimer": "Bu Güvenlik Bilgi Formunda verilen bilgiler, yayınlandığı tarihteki en doğru ve güvenilir mevcut bilgilere dayanmaktadır."
    }
}


class TranslationService:
    @staticmethod
    def get_sections(lang: str = "tr") -> Dict[str, Any]:
        """Bölüm başlıklarını ve etiketlerini döner."""
        if lang.lower() == "en":
            return SECTIONS_EN
        return SECTIONS_TR

    @staticmethod
    def translate_h_code(code: str, lang: str = "tr") -> str:
        code_upper = code.strip().upper()
        if lang.lower() == "en":
            return H_STATEMENTS_EN.get(code_upper, code_upper)
        return code_upper

    @staticmethod
    def translate_p_code(code: str, lang: str = "tr") -> str:
        code_clean = code.strip().upper()
        if lang.lower() == "en":
            return P_STATEMENTS_EN.get(code_clean, code_clean)
        return code_clean

    @staticmethod
    def format_h_statements(h_codes: List[str], lang: str = "tr") -> List[str]:
        formatted = []
        for code in h_codes:
            code_u = code.strip().upper()
            if lang.lower() == "en":
                text = H_STATEMENTS_EN.get(code_u, "")
                if text:
                    formatted.append(f"{code_u}: {text}")
                else:
                    formatted.append(code_u)
            else:
                formatted.append(code_u)
        return formatted

    @staticmethod
    def format_p_statements(p_codes: List[str], lang: str = "tr") -> List[str]:
        formatted = []
        for code in p_codes:
            code_u = code.strip().upper()
            if lang.lower() == "en":
                text = P_STATEMENTS_EN.get(code_u, "")
                if text:
                    formatted.append(f"{code_u}: {text}")
                else:
                    formatted.append(code_u)
            else:
                formatted.append(code_u)
        return formatted

    @staticmethod
    def translate_signal_word(signal_word: str, lang: str = "tr") -> str:
        if lang.lower() == "en":
            if signal_word == "Tehlike":
                return "Danger"
            elif signal_word == "Dikkat":
                return "Warning"
            elif signal_word:
                return signal_word
            return "None"
        return signal_word or "Yok"


translation_service = TranslationService()
