import re
import os
import json
from typing import List, Dict, Any, Tuple, Optional, Set

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
H_TO_P_PATH = os.path.join(DATA_DIR, "h_to_p_mapping.json")
H_STATEMENTS_PATH = os.path.join(DATA_DIR, "h_statements.json")
P_STATEMENTS_PATH = os.path.join(DATA_DIR, "p_statements.json")
PICTOGRAMS_PATH = os.path.join(DATA_DIR, "pictograms.json")

class ClassificationEngine:
    """
    SEA Yönetmeliği (RG: 28848) ve Ek-1 kurallarına dayalı Karışım Zararlılık Hesaplama
    ve H ➔ P Önlem İfadeleri Haritalama Motoru.
    """

    _H_TO_P_MAP: Optional[Dict[str, List[str]]] = None
    _H_STATEMENTS: Optional[Dict[str, Any]] = None
    _P_STATEMENTS: Optional[Dict[str, Any]] = None

    @classmethod
    def _load_data(cls):
        if cls._H_TO_P_MAP is None and os.path.exists(H_TO_P_PATH):
            with open(H_TO_P_PATH, "r", encoding="utf-8") as f:
                cls._H_TO_P_MAP = json.load(f)

        if cls._H_STATEMENTS is None and os.path.exists(H_STATEMENTS_PATH):
            with open(H_STATEMENTS_PATH, "r", encoding="utf-8") as f:
                cls._H_STATEMENTS = json.load(f)

        if cls._P_STATEMENTS is None and os.path.exists(P_STATEMENTS_PATH):
            with open(P_STATEMENTS_PATH, "r", encoding="utf-8") as f:
                cls._P_STATEMENTS = json.load(f)

    @classmethod
    def parse_concentration(cls, conc_str: Any) -> float:
        """
        Bölüm 3.2'deki '%10-25', '15%', '< 2.5%', '>= 50%' gibi metinlerden
        güvenlik ilkesi ve mevzuat eşitsizlik kuralları gereğince konsantrasyon (float) çeker.
        '<' operatörü durumunda katı eşitsizlik gereği eşik değerin hemen altı (örn. <0.1% -> 0.0999) döndürülür.
        """
        if isinstance(conc_str, (int, float)):
            return float(conc_str)
        if not conc_str or not isinstance(conc_str, str):
            return 0.0

        clean = conc_str.replace("%", "").replace(",", ".").strip()

        # Check for strict less than: e.g. "< 0.1", "<2.5%", "< 2.5"
        is_strict_less = bool(re.search(r"<\s*(\d+(?:\.\d+)?)", clean) and not "<=" in clean)

        # Check for range: e.g. "10 - 25" or "10-25"
        range_match = re.findall(r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)", clean)
        if range_match:
            try:
                # Return the upper bound for conservative hazard estimation
                return float(range_match[0][1])
            except ValueError:
                pass

        # Check for single numbers or comparisons: e.g. "< 2.5", ">= 10", "15.5"
        num_matches = re.findall(r"\d+(?:\.\d+)?", clean)
        if num_matches:
            try:
                val = float(num_matches[-1])
                if is_strict_less:
                    return max(0.0, val - 0.0001)
                return val
            except (ValueError, TypeError):
                pass

        return 0.0

    @classmethod
    def parse_float_safe(cls, val: Any, default: Optional[float] = None) -> Optional[float]:
        """
        Sayısal olmayan metinlerden (ör. '500 mg/kg', '100-200', '15.5') güvenli float çeker.
        Hata durumunda default değer döner (asla exception fırlatmaz).
        """
        if val is None or val == "":
            return default
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            clean = val.replace(",", ".").strip()
            matches = re.findall(r"[-+]?\d+(?:\.\d+)?", clean)
            if matches:
                try:
                    return float(matches[0])
                except (ValueError, TypeError):
                    pass
        return default

    @classmethod
    def resolve_repro_h_code(cls, found_codes: Set[str], prefix: str = "H360") -> str:
        """
        Birden fazla H360/H361 varyasyonu bulunduğunda en kapsayıcı ve deterministik kodu seçer.
        Öncelik: H360FD > H360Fd > H360Df > H360F > H360D > H360
        H361fd > H361f > H361d > H361
        """
        if prefix == "H360":
            priority = ["H360FD", "H360Fd", "H360Df", "H360F", "H360D", "H360"]
        else:
            priority = ["H361fd", "H361f", "H361d", "H361"]

        for p in priority:
            for c in found_codes:
                if c.upper() == p.upper():
                    return p
        return "H360D" if prefix == "H360" else "H361d"

    @classmethod
    def extract_h_codes(cls, text: str) -> List[str]:
        """
        Metin içerisindeki tüm H ve EUH kodlarını (ör. H225, H315, H361d, EUH066) ayıklar.
        """
        if not text or not isinstance(text, str):
            return []
        h_codes = re.findall(r"\bH[234]\d{2}[a-zA-Z]*\b", text, re.IGNORECASE)
        euh_codes = re.findall(r"\bEUH\d{3}\b", text, re.IGNORECASE)
        
        # Standardize uppercase
        all_codes = [c.upper() for c in (h_codes + euh_codes)]
        # Normalize specific variations like H361D -> H361d
        normalized = []
        for c in all_codes:
            if c.startswith("H361") and len(c) == 5:
                normalized.append("H361" + c[4].lower())
            elif c.startswith("H360") and len(c) > 4:
                normalized.append("H360" + c[4:])
            else:
                normalized.append(c)
        return list(dict.fromkeys(normalized))

    @classmethod
    def calculate_mixture_hazards(
        cls,
        bilesenler: List[Dict[str, Any]],
        parlama_noktasi: Optional[float] = None,
        kaynama_noktasi: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        SEA Yönetmeliği Ek-1 toplanabilirlik ve eşik değer kurallarına göre
        karışımın sınıflandırmasını, H-kodlarını, Piktogramlarını, Uyarı Kelimesini
        ve adım adım hesaplama açıklamalarını üretir.
        """
        cls._load_data()
        calculation_steps = []
        siniflandirmalar = []
        h_codes = set()
        euh_codes = set()
        piktogram_set = set()
        uyari_kelimesi = "Yok"

        if not bilesenler:
            return {
                "siniflandirmalar": [],
                "h_ifadeleri": [],
                "euh_ifadeleri": [],
                "piktogramlar": [],
                "uyari_kelimesi": "Yok",
                "p_ifadeleri": [],
                "calculation_steps": ["Karışım tablosunda (Bölüm 3.2) bileşen bulunamadı."]
            }

        # 1. Parse each component and aggregate hazard concentrations
        comp_summary = []
        
        # Flammables
        flam_components = []
        
        # Skin & Eye pools
        c_skin_corr_1a = 0.0     # H314 Kat 1A
        c_skin_corr_1b = 0.0     # H314 Kat 1B
        c_skin_corr_1c = 0.0     # H314 Kat 1C
        c_skin_corr_1_gen = 0.0  # H314 Generic Kat 1
        c_skin_irrit_2 = 0.0     # H315
        c_eye_dam_1 = 0.0        # H318
        c_eye_irrit_2 = 0.0      # H319
        
        # Sensitization pools
        c_skin_sens_1 = 0.0      # H317
        c_resp_sens_1 = 0.0      # H334
        has_isocyanates = False  # Explicit isocyanate indicator for EUH204
        
        # Aspiration
        c_asp_tox_1 = 0.0        # H304
        
        # STOT SE / RE
        c_stot_se1 = 0.0         # H370
        c_stot_se2 = 0.0         # H371
        c_stot_se3_335 = 0.0     # H335 (Respiratory irritation)
        c_stot_se3_336 = 0.0     # H336 (Narcotic / drowsiness)
        c_stot_re1 = 0.0         # H372
        c_stot_re2 = 0.0         # H373
        
        # CMR pools
        c_carc1a = 0.0           # H350 / H350i Kat 1A
        c_carc1b = 0.0           # H350 / H350i Kat 1B
        c_carc2 = 0.0            # H351
        c_muta1a = 0.0           # H340 Kat 1A
        c_muta1b = 0.0           # H340 Kat 1B
        c_muta2 = 0.0            # H341
        c_repr1a = 0.0           # H360... Kat 1A
        c_repr1b = 0.0           # H360... Kat 1B
        c_repr2 = 0.0            # H361...
        repr_h360_codes: Set[str] = set()
        repr_h361_codes: Set[str] = set()
        
        # Aquatic pools
        c_aq_acute1 = 0.0        # H400
        c_aq_chronic1 = 0.0      # H410
        c_aq_chronic2 = 0.0      # H411
        c_aq_chronic3 = 0.0      # H412
        c_aq_chronic4 = 0.0      # H413

        # Solvent indicators for EUH066
        c_solvent_total = 0.0
        has_explicit_euh066 = False

        for comp in bilesenler:
            ad = comp.get("ad") or "Bileşen"
            conc = cls.parse_concentration(comp.get("konsantrasyon"))
            sinif_str = comp.get("siniflandirma") or ""
            codes = cls.extract_h_codes(sinif_str)
            
            comp_summary.append(f"• {ad} (%{conc:.1f}): {', '.join(codes) if codes else 'Sınıflandırma yok'}")

            # Flammables
            if "H224" in codes or "Flam. Liq. 1" in sinif_str:
                flam_components.append(("Kat 1", conc, "H224"))
                c_solvent_total += conc
            elif "H225" in codes or "Flam. Liq. 2" in sinif_str:
                flam_components.append(("Kat 2", conc, "H225"))
                c_solvent_total += conc
            elif "H226" in codes or "Flam. Liq. 3" in sinif_str:
                flam_components.append(("Kat 3", conc, "H226"))
                c_solvent_total += conc

            # Skin & Eye (Subcategory detection 1A / 1B / 1C)
            if "H314" in codes or "Skin Corr." in sinif_str:
                if "1A" in sinif_str or "1a" in sinif_str:
                    c_skin_corr_1a += conc
                elif "1B" in sinif_str or "1b" in sinif_str:
                    c_skin_corr_1b += conc
                elif "1C" in sinif_str or "1c" in sinif_str:
                    c_skin_corr_1c += conc
                else:
                    c_skin_corr_1_gen += conc
                c_eye_dam_1 += conc # Skin Corr 1 automatically counts as Eye Dam 1
            if "H315" in codes:
                c_skin_irrit_2 += conc
            if "H318" in codes:
                c_eye_dam_1 += conc
            if "H319" in codes:
                c_eye_irrit_2 += conc

            # Sensitization & Isocyanates
            if "H317" in codes:
                c_skin_sens_1 += conc
            if "H334" in codes:
                c_resp_sens_1 += conc
                ad_l = ad.lower()
                sinif_l = sinif_str.lower()
                if any(iso in ad_l or iso in sinif_l for iso in ["izosiyanat", "isocyanate", "mdi", "tdi", "hdi", "ipdi"]) or comp.get("is_isocyanate"):
                    has_isocyanates = True

            # Aspiration
            if "H304" in codes:
                c_asp_tox_1 += conc
                c_solvent_total += conc

            # STOT SE / RE
            if "H370" in codes:
                c_stot_se1 += conc
            if "H371" in codes:
                c_stot_se2 += conc
            if "H335" in codes:
                c_stot_se3_335 += conc
            if "H336" in codes:
                c_stot_se3_336 += conc
                c_solvent_total += conc
            if "H372" in codes:
                c_stot_re1 += conc
            if "H373" in codes:
                c_stot_re2 += conc

            # CMR (Preserving 1A vs 1B)
            if "H350" in codes or "H350i" in codes:
                if "1A" in sinif_str or "1a" in sinif_str:
                    c_carc1a += conc
                else:
                    c_carc1b += conc
            if "H351" in codes:
                c_carc2 += conc

            if "H340" in codes:
                if "1A" in sinif_str or "1a" in sinif_str:
                    c_muta1a += conc
                else:
                    c_muta1b += conc
            if "H341" in codes:
                c_muta2 += conc

            if any(c.startswith("H360") for c in codes):
                if "1A" in sinif_str or "1a" in sinif_str:
                    c_repr1a += conc
                else:
                    c_repr1b += conc
                for c in codes:
                    if c.startswith("H360"):
                        repr_h360_codes.add(c)
            if any(c.startswith("H361") for c in codes):
                c_repr2 += conc
                for c in codes:
                    if c.startswith("H361"):
                        repr_h361_codes.add(c)

            # Aquatic — M-faktörü uygulaması (SEA Ek-1 Bölüm 4.1.3.5.5)
            m_akut_raw = comp.get("m_faktoru_akut")
            m_kronik_raw = comp.get("m_faktoru_kronik")
            m_akut = cls.parse_float_safe(m_akut_raw, 1.0) or 1.0
            m_kronik = cls.parse_float_safe(m_kronik_raw, 1.0) or 1.0
            if "H400" in codes:
                c_aq_acute1 += conc * m_akut
                if not m_akut_raw:
                    comp_summary.append(f"  ℹ️ [{ad}] Sucul Akut 1 M-faktörü belirtilmediği için varsayılan M=1 uygulandı.")
            if "H410" in codes:
                c_aq_chronic1 += conc * m_kronik
                if not m_kronik_raw:
                    comp_summary.append(f"  ℹ️ [{ad}] Sucul Kronik 1 M-faktörü belirtilmediği için varsayılan M=1 uygulandı.")
            if "H411" in codes:
                c_aq_chronic2 += conc
            if "H412" in codes:
                c_aq_chronic3 += conc
            if "H413" in codes:
                c_aq_chronic4 += conc

            if "EUH066" in codes:
                has_explicit_euh066 = True

        calculation_steps.append("=== 1. BİLEŞEN KONSANTRASYONLARI VE ZARARLILIKLARI ===")
        calculation_steps.extend(comp_summary)
        calculation_steps.append("\n=== 2. SEA EK-1 TOPLANABİLİRLİK VE SINIFLANDIRMA HESAPLAMALARI ===")

        # --- A. ALEVLENİR SIVILAR (FLAMMABLE LIQUIDS) ---
        if parlama_noktasi is not None:
            if parlama_noktasi < 23.0 and (kaynama_noktasi is not None and kaynama_noktasi <= 35.0):
                siniflandirmalar.append({"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 1", "h_kodu": "H224"})
                h_codes.add("H224")
                piktogram_set.add("GHS02")
                uyari_kelimesi = "Tehlike"
                calculation_steps.append(f"• Alevlenir Sıvı: Parlama Noktası ({parlama_noktasi}°C < 23°C) ve Kaynama Noktası ({kaynama_noktasi}°C <= 35°C) -> Kategori 1 (H224)")
            elif parlama_noktasi < 23.0:
                siniflandirmalar.append({"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 2", "h_kodu": "H225"})
                h_codes.add("H225")
                piktogram_set.add("GHS02")
                uyari_kelimesi = "Tehlike"
                calculation_steps.append(f"• Alevlenir Sıvı: Parlama Noktası ({parlama_noktasi}°C < 23°C) -> Kategori 2 (H225)")
            elif 23.0 <= parlama_noktasi <= 60.0:
                siniflandirmalar.append({"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 3", "h_kodu": "H226"})
                h_codes.add("H226")
                piktogram_set.add("GHS02")
                if uyari_kelimesi != "Tehlike":
                    uyari_kelimesi = "Dikkat"
                calculation_steps.append(f"• Alevlenir Sıvı: Parlama Noktası ({parlama_noktasi}°C, 23°C - 60°C arası) -> Kategori 3 (H226)")
            else:
                calculation_steps.append(f"• Alevlenir Sıvı: Parlama Noktası ({parlama_noktasi}°C > 60°C) -> Alevlenir sıvı sınıflandırma eşiği aşılmadı.")
        else:
            if flam_components:
                calculation_steps.append("• Alevlenir Sıvı: Karışımda alevlenir bileşenler bulunmaktadır ancak karışımın ölçülmüş parlama noktası girilmediğinden otomatik sınıflandırma yapılmamıştır (Fiziksel tehlikeler için test verisi zorunludur - SEA Ek-1).")
            else:
                calculation_steps.append("• Alevlenir Sıvı: Karışımda alevlenir bileşen veya parlama noktası verisi girilmemiştir.")

        # --- B. CİLT AŞINMASI VE TAHRİŞİ (SKIN CORROSION / IRRITATION) ---
        is_skin_corr_1 = False
        is_skin_irrit_2 = False
        total_skin_corr = c_skin_corr_1a + c_skin_corr_1b + c_skin_corr_1c + c_skin_corr_1_gen

        if total_skin_corr >= 5.0:
            is_skin_corr_1 = True
            corr_cat = "Kategori 1"
            if c_skin_corr_1a >= 5.0:
                corr_cat = "Kategori 1A"
            elif c_skin_corr_1b >= 5.0:
                corr_cat = "Kategori 1B"
            elif c_skin_corr_1c >= 5.0:
                corr_cat = "Kategori 1C"
            elif c_skin_corr_1a > 0 and (c_skin_corr_1a + c_skin_corr_1b + c_skin_corr_1c + c_skin_corr_1_gen >= 5.0):
                corr_cat = "Kategori 1A"
            elif c_skin_corr_1b > 0:
                corr_cat = "Kategori 1B"

            siniflandirmalar.append({"zararlilik_sinifi": "Cilt Aşınması / Tahrişi", "kategori": corr_cat, "h_kodu": "H314"})
            h_codes.add("H314")
            piktogram_set.add("GHS05")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Cilt Aşınması: ∑(Cilt Aşınması Kat 1) = %{total_skin_corr:.1f} >= %5.0 -> Sınıflandırıldı: {corr_cat} (H314)")
        else:
            skin_irrit_sum = (10.0 * total_skin_corr) + c_skin_irrit_2
            if skin_irrit_sum >= 10.0:
                is_skin_irrit_2 = True
                siniflandirmalar.append({"zararlilik_sinifi": "Cilt Aşınması / Tahrişi", "kategori": "Kategori 2", "h_kodu": "H315"})
                h_codes.add("H315")
                piktogram_set.add("GHS07")
                if uyari_kelimesi != "Tehlike":
                    uyari_kelimesi = "Dikkat"
                calculation_steps.append(f"• Cilt Tahrişi: (10 x ∑Cilt 1 [%{total_skin_corr:.1f}]) + ∑Cilt 2 [%{c_skin_irrit_2:.1f}] = %{skin_irrit_sum:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H315)")
            else:
                calculation_steps.append(f"• Cilt Aşınması/Tahrişi: Eşik değerler aşılmadı (Cilt 1: %{total_skin_corr:.1f} < %5, Tahriş toplamı: %{skin_irrit_sum:.1f} < %10)")

        # --- C. CİDDİ GÖZ HASARI / GÖZ TAHRİŞİ (SERIOUS EYE DAMAGE / EYE IRRITATION) ---
        if is_skin_corr_1:
            # Skin Corr 1 directly entails irreversible Eye Damage Cat 1
            calculation_steps.append("• Göz Hasarı: Cilt Aşınması Kat 1 (H314) mevcudiyeti nedeniyle Ciddi Göz Hasarı Kat 1 (H318) kapsama dahil edildi.")
        else:
            if c_eye_dam_1 >= 3.0:
                siniflandirmalar.append({"zararlilik_sinifi": "Ciddi Göz Hasarı / Göz Tahrişi", "kategori": "Kategori 1", "h_kodu": "H318"})
                h_codes.add("H318")
                piktogram_set.add("GHS05")
                uyari_kelimesi = "Tehlike"
                calculation_steps.append(f"• Ciddi Göz Hasarı: ∑(Cilt 1 + Göz 1) = %{c_eye_dam_1:.1f} >= %3.0 -> Sınıflandırıldı: Kategori 1 (H318)")
            else:
                eye_irrit_sum = (10.0 * c_eye_dam_1) + c_eye_irrit_2
                if eye_irrit_sum >= 10.0:
                    siniflandirmalar.append({"zararlilik_sinifi": "Ciddi Göz Hasarı / Göz Tahrişi", "kategori": "Kategori 2", "h_kodu": "H319"})
                    h_codes.add("H319")
                    piktogram_set.add("GHS07")
                    if uyari_kelimesi != "Tehlike":
                        uyari_kelimesi = "Dikkat"
                    calculation_steps.append(f"• Göz Tahrişi: (10 x ∑Göz 1 [%{c_eye_dam_1:.1f}]) + ∑Göz 2 [%{c_eye_irrit_2:.1f}] = %{eye_irrit_sum:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H319)")
                else:
                    calculation_steps.append(f"• Göz Hasarı/Tahrişi: Eşik değerler aşılmadı (Göz 1: %{c_eye_dam_1:.1f} < %3, Göz Tahriş toplamı: %{eye_irrit_sum:.1f} < %10)")

        # --- D. SOLUNUM VEYA CİLT HASSASLAŞMASI (SENSITIZATION) ---
        if c_resp_sens_1 >= 0.2:
            siniflandirmalar.append({"zararlilik_sinifi": "Solunum veya Cilt Hassaslaşması", "kategori": "Solunum Hassaslaştırıcı Kat 1", "h_kodu": "H334"})
            h_codes.add("H334")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Solunum Hassaslaşması: ∑(Solunum Hassaslaştırıcı) = %{c_resp_sens_1:.1f} >= %0.2 -> Sınıflandırıldı: Kategori 1 (H334)")
        elif 0.1 <= c_resp_sens_1 < 0.2:
            if has_isocyanates:
                euh_codes.add("EUH204")
                calculation_steps.append(f"• Solunum Hassaslaşması: %0.1 <= %{c_resp_sens_1:.1f} < %0.2 ve İzosiyanat bileşeni mevcut -> EUH204 (İzosiyanat içerir) eklendi.")
            else:
                calculation_steps.append(f"• Solunum Hassaslaşması: %0.1 <= %{c_resp_sens_1:.1f} < %0.2 (İzosiyanat tespit edilmediği için EUH204 uygulanmadı).")

        if c_skin_sens_1 >= 1.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Solunum veya Cilt Hassaslaşması", "kategori": "Cilt Hassaslaştırıcı Kat 1", "h_kodu": "H317"})
            h_codes.add("H317")
            piktogram_set.add("GHS07")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Cilt Hassaslaşması: ∑(Cilt Hassaslaştırıcı) = %{c_skin_sens_1:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 1 (H317)")
        elif 0.1 <= c_skin_sens_1 < 1.0:
            euh_codes.add("EUH208")
            calculation_steps.append(f"• Cilt Hassaslaşması: %0.1 <= %{c_skin_sens_1:.1f} < %1.0 -> EUH208 (Alerjik reaksiyona yol açabilir) tetiklendi.")

        # --- E. ASPİRASYON ZARARI (ASPIRATION TOXICITY) ---
        if c_asp_tox_1 >= 10.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Aspirasyon Zararı", "kategori": "Kategori 1", "h_kodu": "H304"})
            h_codes.add("H304")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Aspirasyon Toksisitesi: ∑(Asp. Tox. 1) = %{c_asp_tox_1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H304)")

        # --- F. BELİRLİ HEDEF ORGAN TOKSİSİTESİ (STOT SE & STOT RE) ---
        if c_stot_se1 >= 10.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma", "kategori": "Kategori 1", "h_kodu": "H370"})
            h_codes.add("H370")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• STOT SE: ∑(STOT SE 1) = %{c_stot_se1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H370)")
        elif 1.0 <= c_stot_se2 < 10.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma", "kategori": "Kategori 2", "h_kodu": "H371"})
            h_codes.add("H371")
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• STOT SE: %1.0 <= ∑(STOT SE 2) = %{c_stot_se2:.1f} < %10.0 -> Sınıflandırıldı: Kategori 2 (H371)")

        if c_stot_se3_335 >= 20.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma", "kategori": "Kategori 3 (Solunum)", "h_kodu": "H335"})
            h_codes.add("H335")
            piktogram_set.add("GHS07")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• STOT SE 3 (Solunum Tahrişi): ∑(H335) = %{c_stot_se3_335:.1f} >= %20.0 -> Sınıflandırıldı: Kategori 3 (H335)")

        if c_stot_se3_336 >= 20.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Belirli Hedef Organ Toksisitesi - Tek Maruz Kalma", "kategori": "Kategori 3 (Narkotik)", "h_kodu": "H336"})
            h_codes.add("H336")
            piktogram_set.add("GHS07")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• STOT SE 3 (Rehavet / Baş Dönmesi): ∑(H336) = %{c_stot_se3_336:.1f} >= %20.0 -> Sınıflandırıldı: Kategori 3 (H336)")

        if c_stot_re1 >= 10.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma", "kategori": "Kategori 1", "h_kodu": "H372"})
            h_codes.add("H372")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• STOT RE: ∑(STOT RE 1) = %{c_stot_re1:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 1 (H372)")
        elif c_stot_re2 >= 1.0 or (1.0 <= c_stot_re1 < 10.0):
            siniflandirmalar.append({"zararlilik_sinifi": "Belirli Hedef Organ Toksisitesi - Tekrarlı Maruz Kalma", "kategori": "Kategori 2", "h_kodu": "H373"})
            h_codes.add("H373")
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• STOT RE: ∑(STOT RE 2) = %{c_stot_re2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H373)")

        # --- G. CMR (MUTAJENİTE, KANSEROJENİTE, ÜREME TOKSİSİTESİ) ---
        total_muta1 = c_muta1a + c_muta1b
        if total_muta1 >= 0.1:
            muta_cat = "Kategori 1A" if c_muta1a >= 0.1 else "Kategori 1B"
            siniflandirmalar.append({"zararlilik_sinifi": "Eşey Hücre Mutajenitesi", "kategori": muta_cat, "h_kodu": "H340"})
            h_codes.add("H340")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Mutajenite: ∑(Muta 1) = %{total_muta1:.1f} >= %0.1 -> Sınıflandırıldı: {muta_cat} (H340)")
        elif c_muta2 >= 1.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Eşey Hücre Mutajenitesi", "kategori": "Kategori 2", "h_kodu": "H341"})
            h_codes.add("H341")
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Mutajenite: ∑(Muta 2) = %{c_muta2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H341)")

        total_carc1 = c_carc1a + c_carc1b
        if total_carc1 >= 0.1:
            carc_cat = "Kategori 1A" if c_carc1a >= 0.1 else "Kategori 1B"
            siniflandirmalar.append({"zararlilik_sinifi": "Kanserojenite", "kategori": carc_cat, "h_kodu": "H350"})
            h_codes.add("H350")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Kanserojenite: ∑(Carc 1) = %{total_carc1:.1f} >= %0.1 -> Sınıflandırıldı: {carc_cat} (H350)")
        elif c_carc2 >= 1.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Kanserojenite", "kategori": "Kategori 2", "h_kodu": "H351"})
            h_codes.add("H351")
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Kanserojenite: ∑(Carc 2) = %{c_carc2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H351)")

        total_repr1 = c_repr1a + c_repr1b
        if total_repr1 >= 0.3:
            repr_cat = "Kategori 1A" if c_repr1a >= 0.3 else "Kategori 1B"
            h_repr = cls.resolve_repro_h_code(repr_h360_codes, "H360")
            siniflandirmalar.append({"zararlilik_sinifi": "Üreme Sistemi Toksisitesi", "kategori": repr_cat, "h_kodu": h_repr})
            h_codes.add(h_repr)
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Üreme Toksisitesi: ∑(Repr 1) = %{total_repr1:.1f} >= %0.3 -> Sınıflandırıldı: {repr_cat} ({h_repr})")
        elif c_repr2 >= 3.0:
            h_repr = cls.resolve_repro_h_code(repr_h361_codes, "H361")
            siniflandirmalar.append({"zararlilik_sinifi": "Üreme Sistemi Toksisitesi", "kategori": "Kategori 2", "h_kodu": h_repr})
            h_codes.add(h_repr)
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Üreme Toksisitesi: ∑(Repr 2) = %{c_repr2:.1f} >= %3.0 -> Sınıflandırıldı: Kategori 2 ({h_repr})")

        # --- H. SUCUL ÇEVRE ZARARLARI (AQUATIC HAZARDS) ---
        # H.1 - Akut Kategori 1 (H400) — SEA Ek-1 Tablo 4.1.1 (M x ∑Akut 1 >= %25)
        if c_aq_acute1 >= 25.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Akut", "kategori": "Akut Kategori 1", "h_kodu": "H400"})
            h_codes.add("H400")
            piktogram_set.add("GHS09")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Sucul Çevre (Akut): ∑(M x Akut 1) = %{c_aq_acute1:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Akut 1 (H400)")
        elif c_aq_acute1 > 0:
            calculation_steps.append(f"• Sucul Çevre (Akut): ∑(M x Akut 1) = %{c_aq_acute1:.1f} < %25.0 -> Eşik değer aşılmadı.")

        # H.2 - Kronik Kategoriler (H410/H411/H412/H413) — SEA Ek-1 Tablo 4.1.2
        if c_aq_chronic1 >= 25.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 1", "h_kodu": "H410"})
            h_codes.add("H410")
            piktogram_set.add("GHS09")
            calculation_steps.append(f"• Sucul Çevre (Kronik): ∑(M x Kronik 1) = %{c_aq_chronic1:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 1 (H410)")
        elif (10.0 * c_aq_chronic1 + c_aq_chronic2) >= 25.0:
            chr2_sum = (10.0 * c_aq_chronic1 + c_aq_chronic2)
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 2", "h_kodu": "H411"})
            h_codes.add("H411")
            piktogram_set.add("GHS09")
            calculation_steps.append(f"• Sucul Çevre (Kronik): (10 x ∑M x Kronik 1) + ∑Kronik 2 = %{chr2_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 2 (H411)")
        elif (100.0 * c_aq_chronic1 + 10.0 * c_aq_chronic2 + c_aq_chronic3) >= 25.0:
            chr3_sum = (100.0 * c_aq_chronic1 + 10.0 * c_aq_chronic2 + c_aq_chronic3)
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 3", "h_kodu": "H412"})
            h_codes.add("H412")
            calculation_steps.append(f"• Sucul Çevre (Kronik): (100 x ∑M x Kronik 1) + (10 x ∑Kronik 2) + ∑Kronik 3 = %{chr3_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 3 (H412)")
        elif (c_aq_chronic1 + c_aq_chronic2 + c_aq_chronic3 + c_aq_chronic4) >= 25.0:
            chr4_sum = (c_aq_chronic1 + c_aq_chronic2 + c_aq_chronic3 + c_aq_chronic4)
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 4", "h_kodu": "H413"})
            h_codes.add("H413")
            calculation_steps.append(f"• Sucul Çevre (Kronik): Toplam Kronik = %{chr4_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 4 (H413)")

        # EUH066 check (Anlamlı solvent içeriği >= %10 veya açıkça EUH066 içeren bileşen)
        if (has_explicit_euh066 or c_solvent_total >= 10.0) and not is_skin_irrit_2 and not is_skin_corr_1:
            euh_codes.add("EUH066")
            calculation_steps.append(f"• İlave Bilgi: Anlamlı solvent içeriği (%{c_solvent_total:.1f}) mevcut olup Cilt Tahrişi Kat 2 sınırının altında kaldığı için EUH066 eklendi.")

        # --- I. AKUT TOKSİSİTE (ACUTE TOXICITY - ATE_mix HARMONİK FORMÜL) ---
        # SEA Ek-1 Bölüm 3.1.3.6: 100/ATE_mix = Σ(Ci/ATEi)
        # Dönüşüm değerleri (Tablo 3.1.2)
        ATE_CONVERSION_ORAL = {"H300": 5, "H301": 50, "H302": 500}
        ATE_CONVERSION_DERMAL = {"H310": 50, "H311": 200, "H312": 1100}
        ATE_CONVERSION_INHAL_VAPOUR = {"H330": 0.5, "H331": 3.0, "H332": 11.0}
        ATE_CONVERSION_INHAL_GAS = {"H330": 100, "H331": 700, "H332": 4500}
        ATE_CONVERSION_INHAL_DUST = {"H330": 0.05, "H331": 0.5, "H332": 1.5}

        ate_oral_sum = 0.0
        ate_dermal_sum = 0.0
        ate_inhal_vapour_sum = 0.0
        ate_inhal_gas_sum = 0.0
        ate_inhal_dust_sum = 0.0

        for comp in bilesenler:
            conc = cls.parse_concentration(comp.get("konsantrasyon"))
            if conc <= 0:
                continue
            sinif_str = comp.get("siniflandirma") or ""
            codes = cls.extract_h_codes(sinif_str)

            ate_oral_val = cls.parse_float_safe(comp.get("akut_toksisite_oral"))
            ate_dermal_val = cls.parse_float_safe(comp.get("akut_toksisite_dermal"))
            ate_inhal_val = cls.parse_float_safe(comp.get("akut_toksisite_soluma"))
            inhal_form = (comp.get("akut_toksisite_soluma_formu") or "buhar").lower()

            # Oral
            if ate_oral_val and ate_oral_val > 0:
                ate_oral_sum += conc / ate_oral_val
            else:
                for h_code, conv_ate in ATE_CONVERSION_ORAL.items():
                    if h_code in codes:
                        ate_oral_sum += conc / conv_ate
                        break

            # Dermal
            if ate_dermal_val and ate_dermal_val > 0:
                ate_dermal_sum += conc / ate_dermal_val
            else:
                for h_code, conv_ate in ATE_CONVERSION_DERMAL.items():
                    if h_code in codes:
                        ate_dermal_sum += conc / conv_ate
                        break

            # Soluma (İnhalasyon - Maruziyet Formlarına Göre Ayrım)
            if ate_inhal_val and ate_inhal_val > 0:
                if inhal_form == "gaz":
                    ate_inhal_gas_sum += conc / ate_inhal_val
                elif inhal_form in ["toz_sis", "toz", "sis"]:
                    ate_inhal_dust_sum += conc / ate_inhal_val
                else:
                    ate_inhal_vapour_sum += conc / ate_inhal_val
            else:
                for h_code in ["H330", "H331", "H332"]:
                    if h_code in codes:
                        if inhal_form == "gaz":
                            ate_inhal_gas_sum += conc / ATE_CONVERSION_INHAL_GAS[h_code]
                        elif inhal_form in ["toz_sis", "toz", "sis"]:
                            ate_inhal_dust_sum += conc / ATE_CONVERSION_INHAL_DUST[h_code]
                        else:
                            ate_inhal_vapour_sum += conc / ATE_CONVERSION_INHAL_VAPOUR[h_code]
                        break

        # CLP/SEA Akut Toksisite Kategori eşikleri
        ATE_ORAL_THRESHOLDS = [
            (5, "Kategori 1", "H300"),
            (50, "Kategori 2", "H300"),
            (300, "Kategori 3", "H301"),
            (2000, "Kategori 4", "H302"),
        ]
        ATE_DERMAL_THRESHOLDS = [
            (50, "Kategori 1", "H310"),
            (200, "Kategori 2", "H310"),
            (1000, "Kategori 3", "H311"),
            (2000, "Kategori 4", "H312"),
        ]
        ATE_INHAL_VAPOUR_THRESHOLDS = [
            (0.5, "Kategori 1", "H330"),
            (2.0, "Kategori 2", "H330"),
            (10.0, "Kategori 3", "H331"),
            (20.0, "Kategori 4", "H332"),
        ]
        ATE_INHAL_GAS_THRESHOLDS = [
            (100, "Kategori 1", "H330"),
            (500, "Kategori 2", "H330"),
            (2500, "Kategori 3", "H331"),
            (20000, "Kategori 4", "H332"),
        ]
        ATE_INHAL_DUST_THRESHOLDS = [
            (0.05, "Kategori 1", "H330"),
            (0.5, "Kategori 2", "H330"),
            (1.0, "Kategori 3", "H331"),
            (5.0, "Kategori 4", "H332"),
        ]

        calculation_steps.append("\n--- Akut Toksisite (ATE_mix Harmonik Formül — SEA Ek-1 Bölüm 3.1.3.6) ---")

        def _classify_ate(route_name: str, ate_sum: float, thresholds: list, unit_str: str):
            if ate_sum <= 0:
                calculation_steps.append(f"• Akut Toksisite ({route_name}): ATE verileri mevcut değil veya bileşenler akut toksik değil — hesaplama atlandı.")
                return None
            ate_mix = 100.0 / ate_sum
            calculation_steps.append(f"• Akut Toksisite ({route_name}): 100 / Σ(Ci/ATEi) = 100 / {ate_sum:.4f} = ATE_mix = {ate_mix:.1f} {unit_str}")
            for threshold, cat_name, h_code in thresholds:
                if ate_mix <= threshold:
                    calculation_steps.append(f"  → ATE_mix ({ate_mix:.1f} {unit_str}) ≤ {threshold} → Sınıflandırıldı: {cat_name} ({h_code})")
                    return {"cat": cat_name, "h_code": h_code, "ate_mix": ate_mix}
            calculation_steps.append(f"  → ATE_mix ({ate_mix:.1f} {unit_str}) > {thresholds[-1][0]} — Akut toksisite sınıflandırma eşiği aşılmadı.")
            return None

        oral_result = _classify_ate("Oral", ate_oral_sum, ATE_ORAL_THRESHOLDS, "mg/kg")
        if oral_result:
            siniflandirmalar.append({"zararlilik_sinifi": "Akut Toksisite - Oral", "kategori": oral_result["cat"], "h_kodu": oral_result["h_code"]})
            h_codes.add(oral_result["h_code"])
            if oral_result["h_code"] in ("H300", "H301"):
                piktogram_set.add("GHS06")
                uyari_kelimesi = "Tehlike"
            elif oral_result["h_code"] == "H302":
                piktogram_set.add("GHS07")
                if uyari_kelimesi != "Tehlike":
                    uyari_kelimesi = "Dikkat"

        dermal_result = _classify_ate("Dermal", ate_dermal_sum, ATE_DERMAL_THRESHOLDS, "mg/kg")
        if dermal_result:
            siniflandirmalar.append({"zararlilik_sinifi": "Akut Toksisite - Dermal", "kategori": dermal_result["cat"], "h_kodu": dermal_result["h_code"]})
            h_codes.add(dermal_result["h_code"])
            if dermal_result["h_code"] in ("H310", "H311"):
                piktogram_set.add("GHS06")
                uyari_kelimesi = "Tehlike"
            elif dermal_result["h_code"] == "H312":
                piktogram_set.add("GHS07")
                if uyari_kelimesi != "Tehlike":
                    uyari_kelimesi = "Dikkat"

        # Soluma: Buhar, Gaz ve Toz/Sis yolları
        inhal_vapour_res = _classify_ate("Soluma (Buhar)", ate_inhal_vapour_sum, ATE_INHAL_VAPOUR_THRESHOLDS, "mg/L")
        inhal_gas_res = _classify_ate("Soluma (Gaz)", ate_inhal_gas_sum, ATE_INHAL_GAS_THRESHOLDS, "ppmV")
        inhal_dust_res = _classify_ate("Soluma (Toz/Sis)", ate_inhal_dust_sum, ATE_INHAL_DUST_THRESHOLDS, "mg/L")

        for inhal_res, label in [(inhal_vapour_res, "Soluma (Buhar)"), (inhal_gas_res, "Soluma (Gaz)"), (inhal_dust_res, "Soluma (Toz/Sis)")]:
            if inhal_res:
                siniflandirmalar.append({"zararlilik_sinifi": f"Akut Toksisite - {label}", "kategori": inhal_res["cat"], "h_kodu": inhal_res["h_code"]})
                h_codes.add(inhal_res["h_code"])
                if inhal_res["h_code"] in ("H330", "H331"):
                    piktogram_set.add("GHS06")
                    uyari_kelimesi = "Tehlike"
                elif inhal_res["h_code"] == "H332":
                    piktogram_set.add("GHS07")
                    if uyari_kelimesi != "Tehlike":
                        uyari_kelimesi = "Dikkat"

        # --- 3. GHS PİKTOGRAM VE UYARI KELİMESİ ÖNCELİK KURALLARI (SEA MD. 26 & 28) ---
        filtered_piktogramlar = set(piktogram_set)

        # Rule 1: GHS06 vs GHS07
        if "GHS06" in filtered_piktogramlar and "GHS07" in filtered_piktogramlar:
            # If GHS07 is solely from acute tox (H302, H312, H332), it is dropped
            if not ("H315" in h_codes or "H319" in h_codes or "H317" in h_codes or "H335" in h_codes or "H336" in h_codes):
                filtered_piktogramlar.discard("GHS07")
                calculation_steps.append("• Piktogram Önceliği (Madde 26): GHS06 (Toksik) mevcut olduğu için Akut Toksisite (Kat 4) kaynaklı GHS07 elendi.")

        # Rule 2: GHS05 vs GHS07 for skin/eye
        if "GHS05" in filtered_piktogramlar and "GHS07" in filtered_piktogramlar:
            # If GHS07 only from skin/eye irritation, drop it
            if not ("H317" in h_codes or "H335" in h_codes or "H336" in h_codes or "H302" in h_codes or "H312" in h_codes or "H332" in h_codes):
                filtered_piktogramlar.discard("GHS07")
                calculation_steps.append("• Piktogram Önceliği (Madde 26): GHS05 (Aşındırıcı) mevcut olduğu için Cilt/Göz tahrişi kaynaklı GHS07 elendi.")

        # Rule 3: GHS08 (Resp Sens) vs GHS07 (Skin Sens / Irritation)
        if "H334" in h_codes and "GHS07" in filtered_piktogramlar:
            if not ("H335" in h_codes or "H336" in h_codes or "H302" in h_codes or "H312" in h_codes or "H332" in h_codes):
                filtered_piktogramlar.discard("GHS07")
                calculation_steps.append("• Piktogram Önceliği (Madde 26): GHS08 (Solunum Hassaslaştırıcı) mevcut olduğu için Cilt Hassaslaşması kaynaklı GHS07 elendi.")

        # Order pictograms logically (GHS02, GHS05, GHS06, GHS07, GHS08, GHS09)
        ordered_piktogramlar = sorted(list(filtered_piktogramlar))

        # --- 4. H ➔ P ÖNLEM İFADELERİ TÜRETME VE AKILLI AYIKLAMA ---
        all_h_for_p = sorted(list(h_codes))
        p_statements = cls.generate_p_statements(all_h_for_p)

        return {
            "siniflandirmalar": siniflandirmalar,
            "h_ifadeleri": sorted(list(h_codes)),
            "euh_ifadeleri": sorted(list(euh_codes)),
            "piktogramlar": ordered_piktogramlar,
            "uyari_kelimesi": uyari_kelimesi,
            "p_ifadeleri": p_statements,
            "calculation_steps": calculation_steps
        }

    @classmethod
    def generate_p_statements(cls, h_codes: List[str]) -> List[str]:
        """
        Verilen H-kodları listesine göre SEA Ek-4 standart eşleştirme tablosundan
        ilgili tüm geçerli P-kodlarını çeker, SEA Madde 30(1) uyarınca
        birbirini kapsayan/mükerrer olanları eler ve tam listeyi döndürür.
        """
        cls._load_data()
        if not cls._H_TO_P_MAP:
            return []

        raw_p_codes = []
        for h in h_codes:
            mapped = cls._H_TO_P_MAP.get(h, [])
            raw_p_codes.extend(mapped)

        # Remove duplicates while preserving order
        unique_p = list(dict.fromkeys(raw_p_codes))

        # SEA Madde 30(1) Akıllı Ayıklama Kuralları:
        # 1. Eğer P301+P310 (Hemen 114'ü arayın) varsa, daha zayıf olan P301+P312 elenir.
        if "P301+P310" in unique_p and "P301+P312" in unique_p:
            unique_p.remove("P301+P312")

        # 2. Eğer P301+P330+P331 (Ağzı çalkalayın, kusturmayın) varsa, yalın P330 ve P331 elenir.
        if "P301+P330+P331" in unique_p:
            if "P330" in unique_p:
                unique_p.remove("P330")
            if "P331" in unique_p:
                unique_p.remove("P331")

        # 3. Eğer P361+P364 (Tüm giysileri hemen çıkarın) varsa, P362 (Kirlenmiş giysileri çıkarın) elenir.
        if "P361+P364" in unique_p and "P362" in unique_p:
            unique_p.remove("P362")
        if "P362+P364" in unique_p and "P362" in unique_p:
            unique_p.remove("P362")

        # 4. Eğer P201 & P202 varsa, P202 daha kapsamlıdır ancak birlikte veya P202 tek tutulabilir.
        # Sıralama: Önlem (P2xx) -> Müdahale (P3xx) -> Depolama (P4xx) -> Bertaraf (P5xx)
        def p_sort_key(code: str) -> Tuple[int, str]:
            first = code.split("+")[0].strip()
            num_match = re.search(r"\d+", first)
            num = int(num_match.group(0)) if num_match else 999
            return (num, code)

        unique_p.sort(key=p_sort_key)
        return unique_p
