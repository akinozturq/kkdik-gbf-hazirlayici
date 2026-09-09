"""
Otomatik ADR / UN Numarası ve Taşımacılık Karar Motoru (Transport Decision Engine)
Bölüm 9 fiziksel test verileri ve Bölüm 2 zararlılık sınıflarını analiz ederek
ADR / RID / IMDG / IATA kurallarına uygun Bölüm 14 alanlarını otomatik türetir.
"""

from typing import Dict, Any, Optional, List
from app.services.classification_engine import ClassificationEngine


class TransportDecisionEngine:
    """
    ADR 2.2.3 (Alevlenir Sıvılar), 2.2.8 (Aşındırıcı Maddeler) ve 2.2.9 (Muhtelif Çevre Zararlıları)
    hükümlerine göre otomatik taşımacılık sınıflandırma motoru.
    """

    @classmethod
    def evaluate_transport(cls, sds_data: Dict[str, Any], urun_adi: str = "") -> Dict[str, Any]:
        """
        SDS verilerini analiz ederek Bölüm 14 için önerilen taşımacılık bilgilerini döner.
        """
        b9 = sds_data.get("b9_fiziksel_kimyasal", {})
        b9_1 = b9.get("b9_1", {}) if isinstance(b9.get("b9_1"), dict) else b9
        b2 = sds_data.get("b2_zarar_tanimi", {})
        b2_1 = b2.get("b2_1", {}) if isinstance(b2.get("b2_1"), dict) else {}
        b2_2 = b2.get("b2_2", {}) if isinstance(b2.get("b2_2"), dict) else {}
        b3 = sds_data.get("b3_bilesim", {})
        b1 = sds_data.get("b1_kimlik", {})
        b1_1 = b1.get("b1_1", {}) if isinstance(b1.get("b1_1"), dict) else {}
        b1_2 = b1.get("b1_2", {}) if isinstance(b1.get("b1_2"), dict) else {}

        # 1. Test verilerini güvenli ayrıştır
        pn_val = ClassificationEngine.parse_float_safe(b9_1.get("parlama_noktasi"))
        kn_val = ClassificationEngine.parse_float_safe(b9_1.get("kaynama_noktasi_araligi"))

        # 2. H-Kodlarını topla
        h_codes = set(b2_2.get("h_ifadeleri") or [])
        siniflandirmalar = b2_1.get("siniflandirmalar") or []
        for s in siniflandirmalar:
            if isinstance(s, dict) and s.get("h_kodu"):
                h_codes.add(s["h_kodu"])

        # 3. Ürün adı, kullanım ve bileşen analizi
        effective_product_name = (
            urun_adi or
            b1_1.get("madde_karisim_adi") or
            b1_1.get("ticari_adi") or
            ""
        ).strip()

        # Bileşenleri b3_bilesim.karisim.bilesenler veya b3_bilesim.bilesenler'den al
        bilesenler = (
            b3.get("karisim", {}).get("bilesenler", []) or
            b3.get("bilesenler", []) or
            []
        )
        comp_names = []
        for c in bilesenler:
            if isinstance(c, dict):
                name = c.get("ad") or c.get("madde_adi") or c.get("kimyasal_adi") or ""
                if name:
                    comp_names.append(str(name).lower())

        kullanimlar = " ".join([str(k).lower() for k in (b1_2.get("tanimlanmis_kullanimlar") or [])])
        all_names = (effective_product_name.lower() + " " + kullanimlar + " " + " ".join(comp_names)).lower()

        # Boya, Tiner, Vernik veya Alevlenir Solvent Tespiti
        is_paint_related = any(kw in all_names for kw in [
            "tiner", "thinner", "boya", "paint", "vernik", "varnish", "astar", "primer",
            "solvent", "inceltici", "lak", "reçine", "resin", "selülozik", "poliüretan",
            "epoksi", "sentetik", "akrilik", "sertleştirici", "sertlestirici", "hardener",
            "aktivatör", "aktivator", "curing", "lake", "lacquer", "patina", "stain",
            # Tipik boya ve tiner solventleri:
            "toluen", "toluene", "ksilen", "xylene", "aseton", "acetone", "asetat", "acetate",
            "butil", "butyl", "etil", "ethyl", "metil", "methyl", "izopropil", "isopropanol",
            "ipa", "white spirit", "nafta", "naphtha", "heksan", "hexane", "metanol",
            "methanol", "etanol", "ethanol", "bütanol", "butanol", "glikol", "mek", "mibk", "pma"
        ])
        is_resin = any(kw in all_names for kw in ["reçine", "resin", "polyester"]) and not any(kw in all_names for kw in ["tiner", "thinner"])

        # Çevresel Zarar (Marine Pollutant) Kontrolü
        is_marine_pollutant = any(c in h_codes for c in ["H400", "H410", "H411"])
        env_hazards_tr = "Deniz Kirleticidir (Marine Pollutant - Evet)" if is_marine_pollutant else "Deniz Kirletici değildir (Hayır)"
        env_hazards_en = "Marine Pollutant (Yes)" if is_marine_pollutant else "Not a Marine Pollutant (No)"

        # =========================================================================
        # 1. ALEVLENİR SIVILAR (Sınıf 3)
        # =========================================================================
        has_flam_h = any(c in h_codes for c in ["H224", "H225", "H226"])
        is_flammable_by_flash = (pn_val is not None and pn_val <= 60.0)

        if has_flam_h or is_flammable_by_flash:
            # Paketleme Grubu Belirleme (ADR 2.2.3.1.3)
            # Kat 1: KN <= 35
            # Kat 2: PN < 23 ve KN > 35
            # Kat 3: 23 <= PN <= 60
            if (kn_val is not None and kn_val <= 35.0) or "H224" in h_codes:
                pg = "PG I"
                pg_label = "PG I (Çok tehlikeli)"
                tunnel = "(D/E)"
            elif (pn_val is not None and pn_val < 23.0) or "H225" in h_codes or pn_val is None:
                pg = "PG II"
                pg_label = "PG II (Orta tehlikeli)"
                tunnel = "(D/E)"
            else:
                pg = "PG III"
                pg_label = "PG III (Az tehlikeli)"
                tunnel = "(D/E)"

            # UN No ve Sevkiyat Adı (ADR Tablo A yalın resmi sevkiyat adları)
            if is_paint_related and not is_resin:
                un_no = "UN 1263"
                is_pure_paint = (
                    any(kw in all_names for kw in ["boya", "paint", "vernik", "varnish", "lake", "lacquer", "patina", "astar", "primer", "stain"])
                    and not any(kw in all_names for kw in ["tiner", "thinner", "inceltici", "çözücü", "sertleştirici", "hardener", "aktivatör"])
                )
                if is_pure_paint:
                    ship_tr = "BOYA"
                    ship_en = "PAINT"
                else:
                    ship_tr = "BOYA İLE İLGİLİ MALZEME"
                    ship_en = "PAINT RELATED MATERIAL"
            elif is_resin:
                un_no = "UN 1866"
                ship_tr = "REÇİNE ÇÖZELTİSİ, alevlenebilir"
                ship_en = "RESIN SOLUTION, flammable"
            else:
                un_no = "UN 1993"
                ship_tr = "ALEVLENİR SIVI, B.B.B."
                ship_en = "FLAMMABLE LIQUID, N.O.S."

            return {
                "b14_1_un_numarasi": un_no,
                "b14_2_un_tasimacilik_adi": ship_tr,
                "b14_2_un_tasimacilik_adi_en": ship_en,
                "b14_3_tasimacilik_sinifi": "3 (Alevlenir Sıvılar)",
                "b14_4_ambalajlama_grubu": pg,
                "b14_4_ambalajlama_grubu_label": pg_label,
                "b14_5_cevresel_zararlar": env_hazards_tr,
                "b14_5_cevresel_zararlar_en": env_hazards_en,
                "b14_6_kullanici_ozel_onlemler": f"ADR / RID kurallarına uygun kapalı ve havalandırmalı araçlarda taşınmalıdır. Ateş ve kıvılcım kaynaklarından uzak tutunuz. Tünel Kısıtlama Kodu: {tunnel}",
                "sinif": "3",
                "tunnel_code": tunnel,
                "aciklama": f"Alevlenir sıvı kriterleri (Parlama Noktası: {pn_val}°C, Kaynama Noktası: {kn_val}°C) ve tehlike sınıfları gereği Sınıf 3 olarak belirlendi."
            }

        # =========================================================================
        # 2. AŞINDIRICI MADDELER (Sınıf 8)
        # =========================================================================
        if "H314" in h_codes:
            # 1A -> PG I, 1B -> PG II, 1C -> PG III
            pg = "PG II"
            for s in siniflandirmalar:
                cat = str(s.get("kategori") or "")
                if "1A" in cat:
                    pg = "PG I"
                    break
                elif "1C" in cat:
                    pg = "PG III"

            return {
                "b14_1_un_numarasi": "UN 1760",
                "b14_2_un_tasimacilik_adi": "AŞINDIRICI SIVI, B.B.B.",
                "b14_2_un_tasimacilik_adi_en": "CORROSIVE LIQUID, N.O.S.",
                "b14_3_tasimacilik_sinifi": "8 (Aşındırıcı Maddeler)",
                "b14_4_ambalajlama_grubu": pg,
                "b14_4_ambalajlama_grubu_label": f"{pg} (Aşındırıcı)",
                "b14_5_cevresel_zararlar": env_hazards_tr,
                "b14_5_cevresel_zararlar_en": env_hazards_en,
                "b14_6_kullanici_ozel_onlemler": "Aşındırıcıya dayanıklı ambalajlarda taşınmalıdır. Cilt ve göz temasından koruyunuz. Tünel Kısıtlama Kodu: (E)",
                "sinif": "8",
                "tunnel_code": "(E)",
                "aciklama": "Cilt aşınması (H314) kriterleri gereğince Sınıf 8 Aşındırıcı Madde olarak belirlendi."
            }

        # =========================================================================
        # 3. ÇEVRE İÇİN TEHLİKELİ MADDELER (Sınıf 9)
        # =========================================================================
        if is_marine_pollutant:
            return {
                "b14_1_un_numarasi": "UN 3082",
                "b14_2_un_tasimacilik_adi": "ÇEVRE İÇİN TEHLİKELİ MADDE, SIVI, B.B.B.",
                "b14_2_un_tasimacilik_adi_en": "ENVIRONMENTALLY HAZARDOUS SUBSTANCE, LIQUID, N.O.S.",
                "b14_3_tasimacilik_sinifi": "9 (Muhtelif Tehlikeli Maddeler)",
                "b14_4_ambalajlama_grubu": "PG III",
                "b14_4_ambalajlama_grubu_label": "PG III (Az tehlikeli)",
                "b14_5_cevresel_zararlar": "Deniz Kirleticidir (Marine Pollutant - Evet)",
                "b14_5_cevresel_zararlar_en": "Marine Pollutant (Yes)",
                "b14_6_kullanici_ozel_onlemler": "Su kaynaklarına ve çevreye karışmasını engelleyecek sızdırmaz ambalajlarda taşınmalıdır. Tünel Kısıtlama Kodu: (-)",
                "sinif": "9",
                "tunnel_code": "(-)",
                "aciklama": "Sucul ortama zararlılık (H400/H410/H411) nedeniyle Sınıf 9 Çevre Zararlısı olarak belirlendi."
            }

        # =========================================================================
        # 4. TEHLİKELİ MADDE KAPSAMINDA OLMAYAN ÜRÜNLER
        # =========================================================================
        return {
            "b14_1_un_numarasi": "Taşımacılık mevzuatına göre tehlikeli madde değildir.",
            "b14_2_un_tasimacilik_adi": "Uygulanabilir değildir.",
            "b14_2_un_tasimacilik_adi_en": "Not applicable.",
            "b14_3_tasimacilik_sinifi": "—",
            "b14_4_ambalajlama_grubu": "Uygulanabilir değildir",
            "b14_4_ambalajlama_grubu_label": "Uygulanabilir değildir",
            "b14_5_cevresel_zararlar": "Deniz Kirletici değildir (Hayır)",
            "b14_5_cevresel_zararlar_en": "Not a Marine Pollutant (No)",
            "b14_6_kullanici_ozel_onlemler": "Taşıma sırasında devrilmesini ve ambalaj hasarını önleyecek tedbirleri alınız.",
            "sinif": "—",
            "tunnel_code": "—",
            "aciklama": "Fiziksel, sağlık veya çevresel kriterler taşımacılık tehlike sınıflarına (Sınıf 1-9) girmemektedir."
        }


transport_engine = TransportDecisionEngine()
