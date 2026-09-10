"""
KKDİK (TR) ve REACH Annex II (EN) Dil & Çeviri Servisi
Tüm 16 Bölüm başlıkları, alt başlıkları, etiket unsurları ve standart ifadeleri içerir.
"""

import re
import json
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
    "subtitle": "Bu belge, 23 Haziran 2017 tarihli ve 30105 sayılı Resmi Gazete’de yayımlanan Kimyasalların Kaydı, Değerlendirilmesi, İzni ve Kısıtlanmasına İlişkin Yönetmelik (KKDİK) uyarınca hazırlanmıştır.",
    "meta": {
        "compilation_date": "Hazırlama Tarihi",
        "revision_date": "Revizyon Tarihi",
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


# Standard Turkish to English SDS Phrases and Sentences (REACH Annex II / CLP)
PHRASE_TRANSLATIONS_TR_TO_EN = {
    # General & Identifiers
    "Sanayi / Endüstriyel kullanım": "Industrial / Professional use",
    "Endüstriyel kullanım": "Industrial use",
    "Profesyonel kullanım": "Professional use",
    "Tüketici kullanımı": "Consumer use",
    "Tavsiye edilen kullanımların dışında kullanılmamalıdır.": "Do not use for purposes other than those identified.",
    "Kayıttan muaftır / Uygulanabilir değildir.": "Exempt from registration / Not applicable.",
    "Kayıttan muaftır.": "Exempt from registration.",
    "Uygulanabilir değildir.": "Not applicable.",
    "Uygulanabilir değildir": "Not applicable",
    "Uygulanamaz": "Not applicable",
    "Belirlenmemiştir": "Not determined",
    "Belirlenmemiştir / Uygulanabilir değildir.": "Not determined / Not applicable.",
    "114 (UZEM - Ulusal Zehir Danışma Merkezi) | 112 Acil": "112 Emergency / National Poison Centre",
    "114 (UZEM - Ulusal Zehir Danışma Merkezi)": "114 National Poison Center / 112 Emergency",
    "114": "114 (UZEM) / 112 Emergency",
    "İstanbul / Türkiye": "Istanbul / Turkey",
    "Türkiye": "Turkey",
    "Aypol Kimya Sanayi ve Ticaret A.Ş.": "Aypol Kimya Sanayi ve Ticaret A.S.",

    # Section 2 Classification & Hazards
    "SEA Yönetmeliği kriterlerine göre zararlı olarak sınıflandırılmamıştır.": "Not classified as hazardous according to Regulation (EC) No 1272/2008 [CLP].",
    "Zararlı olarak sınıflandırılmamıştır.": "Not classified as hazardous according to Regulation (EC) No 1272/2008 [CLP].",
    "PBT / vPvB kriterlerini karşılamaz.": "Does not meet the criteria for PBT or vPvB in accordance with Annex XIII of Regulation (EC) No 1907/2006.",
    "PBT veya vPvB maddesi içermez.": "Does not contain PBT or vPvB substances.",
    "PBT/vPvB kriterlerini karşılamaz.": "Does not meet PBT/vPvB criteria.",
    "PBT/vPvB değerlendirmesi yapılmamıştır.": "PBT/vPvB assessment has not been conducted.",
    "Endokrin bozucu özellik göstermez.": "Does not contain substances with endocrine disrupting properties.",
    "Endokrin bozucu madde içermez.": "Does not contain endocrine disrupting substances.",
    "Zararlı sınır değerini aşan bileşen bulunmamaktadır.": "Contains no hazardous ingredients exceeding reporting thresholds.",
    "Zararlı sınır değerini aşan bileşen bildirilmemiştir.": "Contains no hazardous ingredients exceeding reporting thresholds.",
    "GHS Piktogramı Bulunmamaktadır": "No GHS Pictogram required",
    "GHS Piktogramı Yok": "No GHS Pictogram required",

    # Hazard Classes
    "Alevlenir Sıvı": "Flammable Liquid",
    "Alevlenir Gaz": "Flammable Gas",
    "Alevlenir Katı": "Flammable Solid",
    "Alevlenir Aerosol": "Flammable Aerosol",
    "Cilt Aşınması / Tahrişi": "Skin Corrosion / Irritation",
    "Cilt Aşınması": "Skin Corrosion",
    "Cilt Tahrişi": "Skin Irritation",
    "Cilt Tahriş": "Skin Irritation",
    "Ciddi Göz Hasarları / Tahrişi": "Serious Eye Damage / Eye Irritation",
    "Ciddi Göz Hasarı / Göz Tahrişi": "Serious Eye Damage / Eye Irritation",
    "Ciddi Göz Hasarı": "Serious Eye Damage",
    "Göz Hasarı": "Serious Eye Damage",
    "Göz Tahrişi": "Eye Irritation",
    "Solunum Yolları veya Cilt Hassaslaşması": "Respiratory or Skin Sensitisation",
    "Solunum Hassaslaşması": "Respiratory Sensitisation",
    "Solunum Hassasiyeti": "Respiratory Sensitisation",
    "Cilt Hassaslaşması": "Skin Sensitisation",
    "Cilt Hassasiyeti": "Skin Sensitisation",
    "Eşey Hücre Mutajenitesi": "Germ Cell Mutagenicity",
    "Mutajenite": "Germ Cell Mutagenicity",
    "Kanserojenite": "Carcinogenicity",
    "Üreme Toksisitesi": "Reproductive Toxicity",
    "Belirli Hedef Organ Toksisitesi (BHOT) - Tek Maruz Kalma": "Specific Target Organ Toxicity - Single Exposure (STOT SE)",
    "Belirli Hedef Organ Toksisitesi (BHOT) - Tekrarlı Maruz Kalma": "Specific Target Organ Toxicity - Repeated Exposure (STOT RE)",
    "Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma": "Specific Target Organ Toxicity - Single Exposure (STOT SE)",
    "Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma": "Specific Target Organ Toxicity - Repeated Exposure (STOT RE)",
    "Belirli Hedef Organ Toksisitesi": "Specific Target Organ Toxicity",
    "BHOT Tek Maruz": "STOT SE",
    "BHOT Tekrarlı Maruz": "STOT RE",
    "BHOT Tek": "STOT SE",
    "BHOT Tekr.": "STOT RE",
    "Aspirasyon Zararı": "Aspiration Hazard",
    "Aspirasyon Tehlikesi": "Aspiration Hazard",
    "Sucul Akut": "Hazardous to the aquatic environment - Acute",
    "Sucul Kronik": "Hazardous to the aquatic environment - Chronic",
    "Sucul Ortama Zararlı - Akut": "Hazardous to the aquatic environment - Acute",
    "Sucul Ortama Zararlı - Kronik": "Hazardous to the aquatic environment - Chronic",

    # Section 4 First Aid
    "Kazazedeyi temiz havaya çıkarın.": "Remove casualty to fresh air and keep at rest in a position comfortable for breathing.",
    "Kazazedeyi temiz havaya çıkarın. Nefes almıyorsa suni solunum yapın. Doktora başvurun.": "Remove casualty to fresh air and keep at rest in a position comfortable for breathing. If not breathing, give artificial respiration. Get medical attention.",
    "Bol su ve sabun ile yıkayınız.": "Wash thoroughly with plenty of soap and water. Remove contaminated clothing immediately.",
    "Bol su ve sabunla yıkayınız.": "Wash thoroughly with plenty of soap and water. Remove contaminated clothing.",
    "Bol su ile en az 15 dakika yıkayınız.": "Rinse cautiously with water for at least 15 minutes. Remove contact lenses if present and easy to do. Get medical attention if irritation persists.",
    "Bol suyla en az 15 dakika yıkayınız.": "Rinse cautiously with water for at least 15 minutes. Get medical attention.",
    "Gözleri bol su ile en az 15 dakika yıkayınız.": "Rinse cautiously with water for at least 15 minutes. Remove contact lenses if present and easy to do. Get medical attention if irritation persists.",
    "Gözleri bol suyla en az 15 dakika yıkayınız.": "Rinse cautiously with water for at least 15 minutes. Get medical attention.",
    "Gözleri bol su ile yıkayınız.": "Rinse eyes thoroughly with plenty of water.",
    "Ağzı su ile çalkalayınız. Kusturmayınız.": "Rinse mouth thoroughly with water. Do NOT induce vomiting. Seek medical advice immediately.",
    "Ağzı suyla çalkalayınız. Kusturmayınız.": "Rinse mouth thoroughly with water. Do NOT induce vomiting. Seek medical attention immediately.",
    "Önemli bir belirti bildirilmemiştir.": "No significant symptoms or effects are known under normal use.",
    "Önemli belirti bildirilmemiştir.": "No significant symptoms known.",
    "Semptomatik tedavi uygulayınız.": "Treat symptomatically and supportively.",

    # Section 5 Firefighting
    "Köpük, kuru kimyevi toz, CO2, su sisi.": "Water spray, alcohol-resistant foam, dry chemical powder, carbon dioxide (CO2).",
    "Köpük, kuru kimyevi toz, karbon dioksit (CO2), su spreyi.": "Alcohol-resistant foam, dry chemical powder, carbon dioxide (CO2), water spray.",
    "Yüksek basınçlı tam su jeti.": "High volume water jet (may scatter and spread fire).",
    "Doğrudan su jeti (yangını yayabilir).": "Direct water jet (may spread fire).",
    "Yanma halinde toksik karbon oksitler açığa çıkabilir.": "Thermal decomposition can lead to release of toxic carbon oxides (CO, CO2) and irritating fumes.",
    "Yanma halinde toksik karbon oksitler açığa çıkar.": "Thermal decomposition can lead to release of toxic carbon oxides (CO, CO2).",
    "Termal bozunma halinde toksik gazlar (karbon monoksit, karbon dioksit, azot oksitler) oluşabilir.": "Thermal decomposition may produce toxic gases (carbon monoxide, carbon dioxide, nitrogen oxides).",
    "Tam koruyucu teçhizat ve solunum cihazı kullanınız.": "Wear self-contained breathing apparatus (SCBA) and full protective gear.",
    "Tam koruyucu elbise ve solunum cihazı kullanınız.": "Wear self-contained breathing apparatus (SCBA) and full protective clothing.",
    "Yangın söndürme personeli bağımsız solunum aparatı (SCBA) ve tam koruyucu kıyafet giymelidir.": "Firefighting personnel must wear self-contained breathing apparatus (SCBA) and full protective suit.",

    # Section 6 Accidental Release
    "Alanı havalandırın. Ateş kaynaklarını uzaklaştırın.": "Evacuate area. Ensure adequate ventilation. Keep away all sources of ignition. Wear suitable PPE.",
    "Kanalizasyon ve su yollarına karışmasını önleyiniz.": "Prevent product from entering drains, surface water, groundwater or soil.",
    "Toprağa, kanalizasyona, yüzey ve yeraltı sularına karışmasını önleyiniz.": "Prevent product from entering soil, drains, surface water and groundwater.",
    "İnert emici materyal (kum vb.) ile toplayınız.": "Absorb with inert material (sand, silica gel, universal binder, sawdust) and collect in appropriate disposal containers.",
    "İnert emici materyal ile toplayınız.": "Absorb with inert material and collect for disposal.",
    "Dökülen materyali yanıcı olmayan emici bir madde (kum, toprak, diatomit, talaş vb.) ile toplayınız ve bertaraf için uygun bir kaba koyunuz.": "Absorb spillage with non-combustible absorbent material (sand, earth, diatomaceous earth, sawdust) and collect into suitable containers for disposal.",
    "Kişisel korunma için Bölüm 8'e, bertaraf için Bölüm 13'e bakınız.": "See Section 8 for personal protective equipment and Section 13 for waste disposal.",

    # Section 7 Handling & Storage
    "İyi havalandırılan yerlerde kullanın. Temastan kaçının.": "Use only in well-ventilated areas. Avoid contact with eyes, skin and clothing. Avoid breathing vapours.",
    "İyi havalandırılan yerlerde kullanın.": "Use only in well-ventilated areas.",
    "Serin, kuru, iyi havalandırılan yerde saklayınız.": "Store in original tightly closed container in a cool, dry, well-ventilated place away from heat, sparks and open flames.",
    "Orijinal ambalajında, kapağı sıkıca kapalı olarak serin, kuru ve iyi havalandırılan yerde, doğrudan güneş ışığından ve ateş kaynaklarından uzakta muhafaza ediniz.": "Store in original tightly closed container in a cool, dry and well-ventilated area, away from direct sunlight, heat and sources of ignition.",
    "Bölüm 1.2'de belirtilen alanlar içindir.": "No specific end uses other than those specified in Section 1.2.",
    "Ekstra bir son kullanım alanı bulunmamaktadır.": "No additional specific end use information available.",

    # Section 8 Exposure Controls & PPE
    "Tanımlı mesleki maruziyet sınır değeri bulunmamaktadır.": "Contains no substances with occupational exposure limit values.",
    "Yeterli genel ve lokal havalandırma sağlayınız.": "Provide adequate local exhaust and general room ventilation.",
    "Yeterli havalandırma sağlayınız.": "Provide adequate ventilation.",
    "İyi bir genel havalandırma ve yerel egzoz havalandırması sağlayınız.": "Provide good general ventilation and local exhaust ventilation.",
    "EN 166 uyumlu koruyucu gözlük.": "Safety glasses with side-shields conforming to EN 166.",
    "EN 166 onaylı, yan korumalı emniyet gözlükleri veya kimyasal siperlik.": "Safety goggles with side-shields or chemical face shield conforming to EN 166.",
    "EN 374 uyumlu nitril eldiven.": "Chemical resistant protective gloves conforming to EN 374 (e.g. Nitrile rubber).",
    "EN 374 uyumlu koruyucu eldiven.": "Protective gloves conforming to EN 374.",
    "EN 374 standardına uygun solvente/kimyasala dayanıklı nitril veya bütil kauçuk eldivenler.": "Solvent- and chemical-resistant nitrile or butyl rubber gloves conforming to EN 374.",
    "Gerekli hallerde A tipi filtreli solunum maskesi.": "In case of insufficient ventilation or prolonged exposure, wear suitable respirator with filter type A (EN 14387).",
    "Yetersiz havalandırma durumunda organik buharlara uygun A tipi kombine filtreli maske (EN 14387).": "In case of insufficient ventilation, wear respiratory mask with type A filter for organic vapours (EN 14387).",
    "Resmi Gazete: 28733": "TR OEL (RG: 28733) / EU IOELV",

    # Section 9 Physical & Chemical
    "Karakteristik": "Characteristic",
    "Karakteristik solvent kokusu": "Characteristic solvent odour",
    "Kokusuz": "Odourless",
    "Sıvı": "Liquid",
    "Viskoz sıvı": "Viscous liquid",
    "Katı": "Solid",
    "Gaz": "Gas",
    "Şeffaf": "Transparent / Clear",
    "Berrak": "Clear",
    "Berrak sıvı": "Clear liquid",
    "Renksiz": "Colourless",
    "Beyaz": "White",
    "Sarı": "Yellow",
    "Mavi": "Blue",
    "Kırmızı": "Red",
    "Gri": "Grey",
    "Siyah": "Black",
    "Patlayıcı değildir.": "Not explosive",
    "Patlayıcı değildir": "Not explosive",
    "Oksitleyici değildir.": "Not oxidising",
    "Oksitleyici değildir": "Not oxidising",
    "Suda çözünmez.": "Insoluble in water",
    "Suda çözünmez": "Insoluble in water",
    "Suda çözünür.": "Soluble in water",
    "Suda çözünür": "Soluble in water",
    "Suda kısmen çözünür.": "Partially soluble in water",
    "Organik solventlerde çözünür.": "Soluble in organic solvents",
    "Ek bilgi bulunmamaktadır.": "No further relevant information available.",

    # Section 10 Stability & Reactivity
    "Normal koşullarda tehlikeli bir reaksiyon vermez.": "No dangerous reactions known under normal conditions of use.",
    "Normal koşullarda tehlikeli tepkime vermez.": "No dangerous reactions known under normal conditions.",
    "Normal kullanım ve depolama koşullarında reaktif değildir.": "Non-reactive under normal conditions of use and storage.",
    "Normal depolama ve kullanım koşullarında kararlıdır.": "Stable under recommended storage and handling conditions.",
    "Tavsiye edilen depolama koşullarında kararlıdır.": "Stable under recommended storage conditions.",
    "Tehlikeli reaksiyon beklenmez.": "No hazardous reactions known.",
    "Normal kullanımda tehlikeli polimerizasyon veya reaksiyon meydana gelmez.": "No hazardous polymerization or reactions will occur under normal use.",
    "Aşırı ısı, kıvılcım, açık alev.": "Excessive heat, sparks, open flames, hot surfaces and direct sunlight.",
    "Aşırı ısı, açık alev, kıvılcım, doğrudan güneş ışığı ve statik elektrik.": "Excessive heat, open flames, sparks, direct sunlight and static discharge.",
    "Kuvvetli asitler, bazlar ve oksitleyiciler.": "Strong acids, strong bases and strong oxidising agents.",
    "Kuvvetli oksitleyici maddeler, kuvvetli asitler, kuvvetli alkaliler/bazlar.": "Strong oxidising agents, strong acids, strong alkalis/bases.",
    "Normal depolamada ayrışmaz. Yangında toksik gazlar açığa çıkar.": "No hazardous decomposition products known under normal storage. Thermal decomposition releases toxic carbon oxides (CO, CO2).",
    "Normal depolamada ayrışmaz.": "Does not decompose under normal storage conditions.",

    # Section 11 Toxicological
    "Kriterleri karşılamamaktadır.": "Based on available data, the classification criteria are not met.",
    "Kriterleri karşılamaz.": "Does not meet classification criteria.",
    "Mevcut bilgilere göre sınıflandırılmaz.": "Not classified based on available data.",
    "Hassaslaştırıcı etkisi bildirilmemiştir.": "No sensitising effects known.",
    "Mutajenik olarak sınıflandırılmaz.": "Not classified as a germ cell mutagen.",
    "Kanserojen madde içermez.": "Contains no substances classified as carcinogenic.",
    "Üreme için toksik değildir.": "Not classified as toxic for reproduction.",
    "Organ hasarı beklenmez.": "No specific target organ toxicity expected.",
    "Aspirasyon tehlikesi oluşturmaz.": "Not classified as an aspiration hazard.",
    "Aspirasyon tehlikesi oluşturur.": "May be fatal if swallowed and enters airways (Aspiration Hazard).",

    # Section 12 Ecological
    "Sucul organizmalar için zararlı olarak sınıflandırılmamıştır.": "Not classified as environmentally hazardous.",
    "Bileşenleri biyolojik olarak ayrışabilir.": "Components are expected to be biodegradable.",
    "Biyobirikim potansiyeli düşüktür.": "Bioaccumulation potential is low.",
    "Topraktaki hareketliliği çözünürlüğe bağlıdır.": "Mobility in soil depends on water solubility.",
    "Bilinen başka bir olumsuz etkisi yoktur.": "No other adverse environmental effects known.",

    # Section 13 Disposal
    "Ulusal mevzuata uygun olarak lisanslı atık bertaraf tesislerine verilmelidir.": "Dispose of in accordance with local, national and European regulations. Deliver to a licensed hazardous waste disposal contractor.",
    "Boş ambalajlar lisanslı geri kazanım/bertaraf firmalarına teslim edilmelidir.": "Empty contaminated packaging must be handed over to authorized recycling or disposal companies.",
    "Kanalizasyona ve su kaynaklarına dökülmemelidir.": "Do not allow product to enter sewer systems, drains or natural watercourses.",

    # Section 14 Transport
    "Taşımacılıkta tehlikeli madde değildir.": "Not classified as dangerous goods under transport regulations (ADR/RID, IMDG, ICAO/IATA).",
    "ADR / RID / IMDG / ICAO-IATA kapsamında tehlikeli madde değildir.": "Not classified as dangerous goods under transport regulations (ADR/RID, IMDG, ICAO/IATA).",
    "Deniz Kirletici değildir.": "Not a Marine Pollutant",
    "Deniz Kirletici (Marine Pollutant)": "Marine Pollutant",
    "Taşımada devrilme ve hasara karşı emniyete alınız.": "Secure packages against damage, falling and tilting during transport.",
    "Uygulanabilir değildir (Ambalajlı sevkiyat).": "Not applicable (Packaged goods transport).",

    # Section 15 Regulatory
    "KKDİK Yönetmeliği (RG: 30105), SEA Yönetmeliği (RG: 28848).": "Regulation (EC) No 1907/2006 (REACH), Regulation (EC) No 1272/2008 (CLP), and relevant national health & safety regulations.",
    "Bu karışım için Kimyasal Güvenlik Değerlendirmesi (KGD) yapılmamıştır.": "A Chemical Safety Assessment (CSA) has not been carried out for this mixture.",
    "Bu karışım/madde için kimyasal güvenlik değerlendirmesi yapılmamıştır.": "A Chemical Safety Assessment (CSA) has not been carried out for this substance/mixture.",

    # Section 16 Other Info
    "İlk versiyon (KKDİK Ek-2 uyumlu).": "Initial version (Compliant with REACH Annex II and Regulation (EU) 2020/878).",
    "İlk versiyon.": "Initial version.",
    "ADR: Karayolu Taşımacılığı; CAS: Chemical Abstracts Service; TWA: Zaman Ağırlıklı Ortalama; STEL: Kısa Süreli Maruziyet Sınırı.": "ADR: European Agreement concerning the International Carriage of Dangerous Goods by Road; CAS: Chemical Abstracts Service; TWA: Time Weighted Average; STEL: Short Term Exposure Limit; CLP: Classification, Labelling and Packaging; GHS: Globally Harmonized System.",
    "ECHA Veritabanı, T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı Mevzuatı.": "ECHA (European Chemicals Agency) database, safety data sheets of raw materials, CLP Regulation.",
    "Çalışanlar kimyasalların güvenli elleçlenmesi ve KKD kullanımı konusunda eğitilmelidir.": "Ensure operators are trained to minimize exposures, handle chemicals safely, and use appropriate personal protective equipment (PPE).",
    "H-ifadesi bulunmamaktadır.": "No H-statements."
}

# Chemical substance name translations
CHEMICAL_NAMES_TR_TO_EN = {
    "Aseton": "Acetone",
    "Toluen": "Toluene",
    "Ksilen": "Xylene",
    "Etil Asetat": "Ethyl Acetate",
    "Bütil Asetat": "Butyl Acetate",
    "İzopropil Alkol": "Isopropyl Alcohol (Isopropanol)",
    "İzopropanol": "Isopropanol",
    "Etanol": "Ethanol",
    "Metanol": "Methanol",
    "Stiren": "Styrene",
    "Metil Etil Keton": "Methyl Ethyl Ketone (MEK)",
    "Hekzan": "Hexane",
    "n-Hekzan": "n-Hexane",
    "Siklohekzan": "Cyclohexane",
    "Tetrahidrofuran": "Tetrahydrofuran",
    "Diklormetan": "Dichloromethane",
    "Titanyum Dioksit": "Titanium Dioxide",
    "Kalsiyum Karbonat": "Calcium Carbonate",
    "Talk": "Talc",
    "Baryum Sülfat": "Barium Sulfate",
    "Demir Oksit": "Iron Oxide",
    "Çinko Oksit": "Zinc Oxide",
    "Su": "Water",
}


class TranslationService:
    @staticmethod
    def get_sections(lang: str = "tr") -> Dict[str, Any]:
        """Bölüm başlıklarını ve etiketlerini döner."""
        if lang.lower() == "en":
            return SECTIONS_EN
        return SECTIONS_TR

    @staticmethod
    def translate_phrase(text: Optional[str]) -> str:
        """Çeviri sözlüğündeki veya standart kimyasal metinleri İngilizceye çevirir."""
        if not text or not isinstance(text, str):
            return text or ""
        trimmed = text.strip()
        if trimmed in PHRASE_TRANSLATIONS_TR_TO_EN:
            return PHRASE_TRANSLATIONS_TR_TO_EN[trimmed]

        # Türkçe emir kipi varyantları: "-ınız/-iniz" -> "-ın/-in" normalizasyonu
        # Örn: "çıkarınız" -> "çıkarın", "yıkayınız" -> "yıkayın", "başvurunuz" -> "başvurun"
        norm = re.sub(r'([a-zA-ZçÇğĞıİöÖşŞüÜ]+)(y?)(ınız|iniz|unuz|ünüz)\b', r'\1\2ın', trimmed)
        if norm in PHRASE_TRANSLATIONS_TR_TO_EN:
            return PHRASE_TRANSLATIONS_TR_TO_EN[norm]

        norm_in = re.sub(r'([a-zA-ZçÇğĞıİöÖşŞüÜ]+)(y?)(ınız|iniz|unuz|ünüz)\b', r'\1\2in', trimmed)
        if norm_in in PHRASE_TRANSLATIONS_TR_TO_EN:
            return PHRASE_TRANSLATIONS_TR_TO_EN[norm_in]

        norm_un = re.sub(r'([a-zA-ZçÇğĞıİöÖşŞüÜ]+)(y?)(ınız|iniz|unuz|ünüz)\b', r'\1\2un', trimmed)
        if norm_un in PHRASE_TRANSLATIONS_TR_TO_EN:
            return PHRASE_TRANSLATIONS_TR_TO_EN[norm_un]
        
        # Substring / pattern replacements for common terms
        res = trimmed
        for tr_phrase, en_phrase in PHRASE_TRANSLATIONS_TR_TO_EN.items():
            if len(tr_phrase) > 4 and tr_phrase in res:
                res = res.replace(tr_phrase, en_phrase)
        return res

    @staticmethod
    def translate_chemical_name(name: Optional[str]) -> str:
        if not name or not isinstance(name, str):
            return name or ""
        trimmed = name.strip()
        return CHEMICAL_NAMES_TR_TO_EN.get(trimmed, trimmed)

    @staticmethod
    def translate_component_classification(class_str: Optional[str]) -> str:
        """Bölüm 3.2 bileşen sınıflandırma kısaltmalarını CLP standardına çevirir."""
        if not class_str or not isinstance(class_str, str):
            return class_str or "—"
        s = class_str
        mappings = [
            ("Alev. Sıvı", "Flam. Liq."),
            ("Alev. Gaz", "Flam. Gas"),
            ("Alev. Katı", "Flam. Sol."),
            ("Alev. Aerosol", "Aerosol"),
            ("Cilt Aşın.", "Skin Corr."),
            ("Cilt Tah.", "Skin Irrit."),
            ("Göz Has.", "Eye Dam."),
            ("Göz Tah.", "Eye Irrit."),
            ("Akut Tok.", "Acute Tox."),
            ("Sol. Hassas.", "Resp. Sens."),
            ("Cilt Hassas.", "Skin Sens."),
            ("Mutajen.", "Muta."),
            ("Kanserojen.", "Carc."),
            ("Üreme Tok.", "Repr."),
            ("Ür. Sis.", "Repr."),
            ("Ür. Tok.", "Repr."),
            ("Üreme Sist.", "Repr."),
            ("BHOT Tek", "STOT SE"),
            ("BHOT Tekr.", "STOT RE"),
            ("BHOT Tek.", "STOT SE"),
            ("Asp. Zar.", "Asp. Tox."),
            ("Asp. Tok.", "Asp. Tox."),
            ("Sucul Akut", "Aquatic Acute"),
            ("Sucul Kronik", "Aquatic Chronic"),
            ("Kategori", "Cat."),
            ("Kat.", "Cat.")
        ]
        for tr_abbr, en_abbr in mappings:
            s = s.replace(tr_abbr, en_abbr)
        return s

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
        for item in h_codes:
            if not item:
                continue
            # Extract H code if string is like "H225: Açıklama" or "H225"
            item_str = str(item).strip()
            match = re.search(r'\b(H\d{3}[a-zA-Z]?|EUH\d{3}[a-zA-Z]?)\b', item_str, re.IGNORECASE)
            if match:
                h_code = match.group(1).upper()
                if lang.lower() == "en":
                    text = H_STATEMENTS_EN.get(h_code, "")
                    formatted.append(f"{h_code}: {text}" if text else item_str)
                else:
                    formatted.append(item_str)
            else:
                formatted.append(item_str)
        return formatted

    @staticmethod
    def format_p_statements(p_codes: List[str], lang: str = "tr") -> List[str]:
        formatted = []
        for item in p_codes:
            if not item:
                continue
            item_str = str(item).strip()
            match = re.search(r'\b(P\d{3}(?:\+P\d{3})*)\b', item_str, re.IGNORECASE)
            if match:
                p_code = match.group(1).upper()
                if lang.lower() == "en":
                    text = P_STATEMENTS_EN.get(p_code, "")
                    formatted.append(f"{p_code}: {text}" if text else item_str)
                else:
                    formatted.append(item_str)
            else:
                formatted.append(item_str)
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

    @classmethod
    def _is_non_translatable(cls, s: str) -> bool:
        """Metnin çevrilmeye ihtiyaç duyup duymadığını tespit eder."""
        if not isinstance(s, str):
            return True
        s = s.strip()
        if not s or s == "—" or s == "-" or s.isdigit():
            return True
        # CAS No, EC No, Tarih, Telefon, E-posta, URL, Piktogram / H-P kodlarını atla
        if re.match(r'^(CAS\s*:?\s*)?\d{2,7}-\d{2}-\d$', s, re.IGNORECASE):
            return True
        if re.match(r'^(EC\s*:?\s*)?\d{3}-\d{3}-\d$', s, re.IGNORECASE):
            return True
        if re.match(r'^[HhPp]\d{3}[a-zA-Z]?$', s):
            return True
        if re.match(r'^\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{2,4}$', s):
            return True
        if re.match(r'^[\d\s\+\-\(\)\.\,\%\/\:\;]+$', s):
            return True
        if "@" in s and "." in s and " " not in s:
            return True
        if s.startswith("http://") or s.startswith("https://") or s.startswith("www."):
            return True
        # GHS Kodları
        if s.startswith("GHS0") or s.startswith("GHS"):
            return True
        return False

    @classmethod
    def _collect_untranslated_strings(cls, data, prefix=""):
        """Tüm SDS yapısını özyinelemeli tarayarak çevrilmemiş serbest Türkçe metinleri toplar."""
        items = {}
        if isinstance(data, dict):
            for k, v in data.items():
                if k in ("cas_no", "ec_no", "kayit_no", "telefon", "eposta", "web", "h_kodu", "piktogramlar", "created_at", "updated_at", "konsantrasyon"):
                    continue
                path = f"{prefix}.{k}" if prefix else k
                if isinstance(v, str):
                    if not cls._is_non_translatable(v):
                        items[path] = v
                elif isinstance(v, (dict, list)):
                    items.update(cls._collect_untranslated_strings(v, path))
        elif isinstance(data, list):
            for i, v in enumerate(data):
                path = f"{prefix}[{i}]"
                if isinstance(v, str):
                    if not cls._is_non_translatable(v):
                        items[path] = v
                elif isinstance(v, (dict, list)):
                    items.update(cls._collect_untranslated_strings(v, path))
        return items

    @classmethod
    def _set_by_path(cls, data, path: str, value: Any):
        """Nokta ve dizi indeksli yollara (örn: b3_bilesim.karisim.bilesenler[0].ad) göre değeri günceller."""
        tokens = re.findall(r'[^.\[\]]+', path)
        if not tokens:
            return
        curr = data
        for i, token in enumerate(tokens[:-1]):
            next_token = tokens[i + 1]
            if token.isdigit():
                idx = int(token)
                while len(curr) <= idx:
                    curr.append({})
                curr = curr[idx]
            else:
                if token not in curr or not isinstance(curr[token], (dict, list)):
                    curr[token] = [] if next_token.isdigit() else {}
                curr = curr[token]

        last_token = tokens[-1]
        if last_token.isdigit():
            idx = int(last_token)
            if isinstance(curr, list) and idx < len(curr):
                curr[idx] = value
        else:
            if isinstance(curr, dict):
                curr[last_token] = value

    @classmethod
    def translate_sds_dict(cls, sds_data: dict, lang: str = "tr") -> dict:
        """
        SDS verilerini talep edilen dile (İngilizce REACH Annex II) derinlemesine çevirir.
        Hibrit: 1. Aşama Kural/Sözlük tabanlı anlık çeviri, 2. Aşama Kapsamlı Gemini AI çevirisi.
        """
        import json
        if not sds_data or (lang or "tr").lower() == "tr":
            return sds_data or {}

        try:
            sds = json.loads(json.dumps(dict(sds_data), default=str))
        except Exception:
            sds = dict(sds_data)
        
        # 1. Aşama: Deterministik REACH Annex II sözlüğü ve CLP kuralları ile anlık çevir
        b1 = sds.get("b1_kimlik") or {}
        b1_1 = b1.get("b1_1") or {}
        b1_2 = b1.get("b1_2") or {}
        b1_3 = b1.get("b1_3") or {}
        b1_4 = b1.get("b1_4") or {}

        if b1_1.get("kayit_numarasi"):
            b1_1["kayit_numarasi"] = cls.translate_phrase(b1_1["kayit_numarasi"])
        if b1_2.get("tanimlanmis_kullanimlar"):
            b1_2["tanimlanmis_kullanimlar"] = [cls.translate_phrase(u) for u in b1_2["tanimlanmis_kullanimlar"]]
        if b1_2.get("tavsiye_edilmeyen_kullanimlar"):
            b1_2["tavsiye_edilmeyen_kullanimlar"] = [cls.translate_phrase(u) for u in b1_2["tavsiye_edilmeyen_kullanimlar"]]
        if b1_3.get("adres"):
            b1_3["adres"] = cls.translate_phrase(b1_3["adres"])
        if b1_4.get("acil_telefon"):
            b1_4["acil_telefon"] = cls.translate_phrase(b1_4["acil_telefon"])

        b2 = sds.get("b2_zarar_tanimi") or {}
        b2_1 = b2.get("b2_1") or {}
        b2_2 = b2.get("b2_2") or {}
        b2_3 = b2.get("b2_3") or {}

        if b2_1.get("siniflandirmalar"):
            for item in b2_1["siniflandirmalar"]:
                if "zararlilik_sinifi" in item:
                    item["zararlilik_sinifi"] = cls.translate_phrase(item["zararlilik_sinifi"])
                if "kategori" in item:
                    item["kategori"] = cls.translate_phrase(item["kategori"])
        if b2_1.get("siniflandirilmama_gerekcesi"):
            b2_1["siniflandirilmama_gerekcesi"] = cls.translate_phrase(b2_1["siniflandirilmama_gerekcesi"])

        if b2_2.get("uyari_kelimesi"):
            b2_2["uyari_kelimesi"] = cls.translate_signal_word(b2_2["uyari_kelimesi"], "en")
        if b2_2.get("h_ifadeleri"):
            b2_2["h_ifadeleri"] = cls.format_h_statements(b2_2["h_ifadeleri"], "en")
        if b2_2.get("p_ifadeleri"):
            b2_2["p_ifadeleri"] = cls.format_p_statements(b2_2["p_ifadeleri"], "en")

        if b2_3.get("pbt_vpvb_degerlendirme"):
            b2_3["pbt_vpvb_degerlendirme"] = cls.translate_phrase(b2_3["pbt_vpvb_degerlendirme"])
        if b2_3.get("diger_zararlar"):
            b2_3["diger_zararlar"] = cls.translate_phrase(b2_3["diger_zararlar"])

        b3 = sds.get("b3_bilesim") or {}
        if b3.get("tip") == "karisim":
            bilesenler = b3.get("karisim", {}).get("bilesenler", [])
            for b in bilesenler:
                if "ad" in b:
                    b["ad"] = cls.translate_chemical_name(b["ad"])
                if "siniflandirma" in b:
                    b["siniflandirma"] = cls.translate_component_classification(b["siniflandirma"])

        b4 = sds.get("b4_ilk_yardim") or {}
        b4_1 = b4.get("b4_1") or {}
        for key in ("soluma", "cilt_temasi", "goz_temasi", "yutma", "korunma"):
            if b4_1.get(key):
                b4_1[key] = cls.translate_phrase(b4_1[key])
        if b4.get("b4_2_belirtiler_etkiler"):
            b4["b4_2_belirtiler_etkiler"] = cls.translate_phrase(b4["b4_2_belirtiler_etkiler"])
        if b4.get("b4_3_acil_tibbi_mudahale"):
            b4["b4_3_acil_tibbi_mudahale"] = cls.translate_phrase(b4["b4_3_acil_tibbi_mudahale"])

        b5 = sds.get("b5_yangin_mucadele") or {}
        b5_1 = b5.get("b5_1") or {}
        if b5_1.get("uygun_sondurucu"):
            b5_1["uygun_sondurucu"] = cls.translate_phrase(b5_1["uygun_sondurucu"])
        if b5_1.get("uygun_olmayan_sondurucu"):
            b5_1["uygun_olmayan_sondurucu"] = cls.translate_phrase(b5_1["uygun_olmayan_sondurucu"])
        if b5.get("b5_2_ozel_zararlar"):
            b5["b5_2_ozel_zararlar"] = cls.translate_phrase(b5["b5_2_ozel_zararlar"])
        if b5.get("b5_3_sondurme_ekibi_tavsiyeleri"):
            b5["b5_3_sondurme_ekibi_tavsiyeleri"] = cls.translate_phrase(b5["b5_3_sondurme_ekibi_tavsiyeleri"])

        b6 = sds.get("b6_kaza_sonucu_yayilma") or {}
        b6_1 = b6.get("b6_1") or {}
        if b6_1.get("kisisel_onlemler_acil_olmayan"):
            b6_1["kisisel_onlemler_acil_olmayan"] = cls.translate_phrase(b6_1["kisisel_onlemler_acil_olmayan"])
        if b6_1.get("kisisel_onlemler_acil_mudahale"):
            b6_1["kisisel_onlemler_acil_mudahale"] = cls.translate_phrase(b6_1["kisisel_onlemler_acil_mudahale"])
        if b6.get("b6_2_cevresel_onlemler"):
            b6["b6_2_cevresel_onlemler"] = cls.translate_phrase(b6["b6_2_cevresel_onlemler"])
        if b6.get("b6_3_kontrol_temizleme_yontemleri"):
            b6["b6_3_kontrol_temizleme_yontemleri"] = cls.translate_phrase(b6["b6_3_kontrol_temizleme_yontemleri"])
        if b6.get("b6_4_diger_bolumlere_atif"):
            b6["b6_4_diger_bolumlere_atif"] = cls.translate_phrase(b6["b6_4_diger_bolumlere_atif"])

        b7 = sds.get("b7_ellecme_depolama") or {}
        b7_2 = b7.get("b7_2") or {}
        if b7.get("b7_1_guvenli_ellecleme"):
            b7["b7_1_guvenli_ellecleme"] = cls.translate_phrase(b7["b7_1_guvenli_ellecleme"])
        if b7_2.get("guvenli_depolama_kosullari"):
            b7_2["guvenli_depolama_kosullari"] = cls.translate_phrase(b7_2["guvenli_depolama_kosullari"])
        if b7.get("b7_3_belirli_son_kullanimlar"):
            b7["b7_3_belirli_son_kullanimlar"] = cls.translate_phrase(b7["b7_3_belirli_son_kullanimlar"])

        b8 = sds.get("b8_maruz_kalma_kontrolu") or {}
        b8_2 = b8.get("b8_2") or {}
        kkd = b8_2.get("kkd") or {}
        for exp in b8.get("b8_1_kontrol_parametreleri", []):
            if "yasal_dayanak" in exp:
                exp["yasal_dayanak"] = cls.translate_phrase(exp["yasal_dayanak"])
            if "madde" in exp:
                exp["madde"] = cls.translate_chemical_name(exp["madde"])
        if b8_2.get("muhendislik_kontrolleri"):
            b8_2["muhendislik_kontrolleri"] = cls.translate_phrase(b8_2["muhendislik_kontrolleri"])
        for kkd_k in ("goz_yuz", "cilt_el", "cilt_vucut", "solunum", "termal_zararlar"):
            if kkd.get(kkd_k):
                kkd[kkd_k] = cls.translate_phrase(kkd[kkd_k])

        b9 = sds.get("b9_fiziksel_kimyasal_ozellikler") or {}
        b9_1 = b9.get("b9_1") or {}
        for prop_k in b9_1:
            if b9_1.get(prop_k):
                b9_1[prop_k] = cls.translate_phrase(b9_1[prop_k])
        if b9.get("b9_2_diger_bilgiler"):
            b9["b9_2_diger_bilgiler"] = cls.translate_phrase(b9["b9_2_diger_bilgiler"])

        b10 = sds.get("b10_kararlilik_tepkime") or {}
        for k10 in ("b10_1_tepkime", "b10_2_kimyasal_kararlilik", "b10_3_zararli_reaksiyon_olasiligi",
                    "b10_4_kacinilmasi_gereken_durumlar", "b10_5_kacinilmasi_gereken_maddeler", "b10_6_zararli_bozunma_urunleri"):
            if b10.get(k10):
                b10[k10] = cls.translate_phrase(b10[k10])

        b11 = sds.get("b11_toksikolojik") or {}
        b11_1 = b11.get("b11_1") or {}
        for tox_k in b11_1:
            if b11_1.get(tox_k):
                b11_1[tox_k] = cls.translate_phrase(b11_1[tox_k])

        b12 = sds.get("b12_ekolojik") or {}
        for eco_k in ("b12_1_toksisite", "b12_2_kalicilik_bozunabilirlik", "b12_3_biyobirikim",
                      "b12_4_topraktaki_hareketlilik", "b12_5_pbt_vpvb_sonuclari", "b12_6_diger_olumsuz_etkiler"):
            if b12.get(eco_k):
                b12[eco_k] = cls.translate_phrase(b12[eco_k])

        b13 = sds.get("b13_bertaraf") or {}
        for dis_k in ("b13_1_atik_isleme_yontemleri", "b13_1_ambalaj_atik_isleme", "b13_1_kanalizasyon_uyarisi"):
            if b13.get(dis_k):
                b13[dis_k] = cls.translate_phrase(b13[dis_k])

        b14 = sds.get("b14_tasimacilik") or {}
        for tr_k in ("b14_1_un_numarasi", "b14_2_un_tasimacilik_adi", "b14_3_tasimacilik_sinifi", "b14_5_cevresel_zararlar", "b14_6_kullanici_ozel_onlemler", "b14_7_marpol_ibc"):
            if b14.get(tr_k):
                b14[tr_k] = cls.translate_phrase(b14[tr_k])

        b15 = sds.get("b15_mevzuat") or {}
        if b15.get("b15_1_ozel_mevzuat_hukumleri"):
            b15["b15_1_ozel_mevzuat_hukumleri"] = cls.translate_phrase(b15["b15_1_ozel_mevzuat_hukumleri"])
        if b15.get("b15_2_kimyasal_guvenlik_degerlendirmesi"):
            b15["b15_2_kimyasal_guvenlik_degerlendirmesi"] = cls.translate_phrase(b15["b15_2_kimyasal_guvenlik_degerlendirmesi"])

        b16 = sds.get("b16_diger_bilgiler") or {}
        for oth_k in ("revizyon_aciklamasi", "kisaltmalar_anahtari", "literatur_referanslari", "egitim_tavsiyeleri"):
            if b16.get(oth_k):
                b16[oth_k] = cls.translate_phrase(b16[oth_k])
        if b16.get("tam_h_ifadeleri"):
            b16["tam_h_ifadeleri"] = cls.format_h_statements(b16["tam_h_ifadeleri"], "en")

        # 2. Aşama: Kapsamlı Evrensel Gemini AI Katmanı
        try:
            from app.services.gemini_service import gemini_service
            if gemini_service.is_configured():
                # Sözlükte karşılığı bulunmayan kalan tüm serbest Türkçe metinleri topla
                untranslated_map = cls._collect_untranslated_strings(sds)
                
                if untranslated_map:
                    translated_map = gemini_service.translate_texts_batch(untranslated_map, target_lang="en")
                    
                    # Çevrilen alanları tam olarak orijinal JSON ağacındaki yerlerine yaz
                    for path, trans_text in translated_map.items():
                        if trans_text and isinstance(trans_text, str) and trans_text.strip():
                            cls._set_by_path(sds, path, trans_text.strip())
        except Exception as e:
            pass

        return sds


translation_service = TranslationService()


