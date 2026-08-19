import re
import os
import json
from typing import List, Dict, Any, Tuple, Optional

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
        güvenlik ilkesi gereğince üst sınır konsantrasyonu (float) çeker.
        """
        if isinstance(conc_str, (int, float)):
            return float(conc_str)
        if not conc_str or not isinstance(conc_str, str):
            return 0.0

        clean = conc_str.replace("%", "").replace(",", ".").strip()

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
                return float(num_matches[-1])
            except ValueError:
                pass

        return 0.0

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
                suffix = c[4:]
                if suffix in ["D", "F", "FD"]:
                    normalized.append("H360" + suffix)
                else:
                    normalized.append("H360" + suffix)
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
        
        # Skin & Eye Additivity pools
        c_skin_corr_1 = 0.0      # H314
        c_skin_irrit_2 = 0.0     # H315
        c_eye_dam_1 = 0.0        # H318
        c_eye_irrit_2 = 0.0      # H319
        
        # Sensitization pools
        c_skin_sens_1 = 0.0      # H317
        c_resp_sens_1 = 0.0      # H334
        
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
        c_carc1 = 0.0            # H350 / H350i
        c_carc2 = 0.0            # H351
        c_muta1 = 0.0            # H340
        c_muta2 = 0.0            # H341
        c_repr1 = 0.0            # H360...
        c_repr2 = 0.0            # H361...
        repr_h_specific = None
        
        # Aquatic pools
        c_aq_acute1 = 0.0        # H400
        c_aq_chronic1 = 0.0      # H410
        c_aq_chronic2 = 0.0      # H411
        c_aq_chronic3 = 0.0      # H412
        c_aq_chronic4 = 0.0      # H413

        # Solvent indicators for EUH066
        has_solvents = False

        for comp in bilesenler:
            ad = comp.get("ad") or "Bileşen"
            conc = cls.parse_concentration(comp.get("konsantrasyon"))
            sinif_str = comp.get("siniflandirma") or ""
            codes = cls.extract_h_codes(sinif_str)
            
            comp_summary.append(f"• {ad} (%{conc:.1f}): {', '.join(codes) if codes else 'Sınıflandırma yok'}")

            # Flammables
            if "H224" in codes or "Flam. Liq. 1" in sinif_str:
                flam_components.append(("Kat 1", conc, "H224"))
                has_solvents = True
            elif "H225" in codes or "Flam. Liq. 2" in sinif_str:
                flam_components.append(("Kat 2", conc, "H225"))
                has_solvents = True
            elif "H226" in codes or "Flam. Liq. 3" in sinif_str:
                flam_components.append(("Kat 3", conc, "H226"))
                has_solvents = True

            # Skin & Eye
            if "H314" in codes:
                c_skin_corr_1 += conc
                c_eye_dam_1 += conc # Skin Corr 1 automatically counts as Eye Dam 1
            if "H315" in codes:
                c_skin_irrit_2 += conc
            if "H318" in codes:
                c_eye_dam_1 += conc
            if "H319" in codes:
                c_eye_irrit_2 += conc

            # Sensitization
            if "H317" in codes:
                c_skin_sens_1 += conc
            if "H334" in codes:
                c_resp_sens_1 += conc

            # Aspiration
            if "H304" in codes:
                c_asp_tox_1 += conc
                has_solvents = True

            # STOT SE / RE
            if "H370" in codes:
                c_stot_se1 += conc
            if "H371" in codes:
                c_stot_se2 += conc
            if "H335" in codes:
                c_stot_se3_335 += conc
            if "H336" in codes:
                c_stot_se3_336 += conc
                has_solvents = True
            if "H372" in codes:
                c_stot_re1 += conc
            if "H373" in codes:
                c_stot_re2 += conc

            # CMR
            if "H350" in codes or "H350i" in codes:
                c_carc1 += conc
            if "H351" in codes:
                c_carc2 += conc
            if "H340" in codes:
                c_muta1 += conc
            if "H341" in codes:
                c_muta2 += conc
            if any(c.startswith("H360") for c in codes):
                c_repr1 += conc
                repr_h_specific = next((c for c in codes if c.startswith("H360")), "H360")
            if any(c.startswith("H361") for c in codes):
                c_repr2 += conc
                repr_h_specific = next((c for c in codes if c.startswith("H361")), "H361")

            # Aquatic
            if "H400" in codes:
                c_aq_acute1 += conc
            if "H410" in codes:
                c_aq_chronic1 += conc
            if "H411" in codes:
                c_aq_chronic2 += conc
            if "H412" in codes:
                c_aq_chronic3 += conc
            if "H413" in codes:
                c_aq_chronic4 += conc

            if "EUH066" in codes:
                has_solvents = True

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
        elif flam_components:
            # Component based estimation if test data not provided
            if any(f[0] == "Kat 1" for f in flam_components):
                siniflandirmalar.append({"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 1", "h_kodu": "H224"})
                h_codes.add("H224")
                piktogram_set.add("GHS02")
                uyari_kelimesi = "Tehlike"
                calculation_steps.append("• Alevlenir Sıvı: Karışımda Alevlenir Sıvı Kat 1 bileşeni bulundu -> Kategori 1 (H224)")
            elif any(f[0] == "Kat 2" for f in flam_components):
                siniflandirmalar.append({"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 2", "h_kodu": "H225"})
                h_codes.add("H225")
                piktogram_set.add("GHS02")
                uyari_kelimesi = "Tehlike"
                calculation_steps.append("• Alevlenir Sıvı: Karışımda Alevlenir Sıvı Kat 2 bileşeni bulundu -> Kategori 2 (H225)")
            elif any(f[0] == "Kat 3" for f in flam_components):
                siniflandirmalar.append({"zararlilik_sinifi": "Alevlenir Sıvılar", "kategori": "Kategori 3", "h_kodu": "H226"})
                h_codes.add("H226")
                piktogram_set.add("GHS02")
                if uyari_kelimesi != "Tehlike":
                    uyari_kelimesi = "Dikkat"
                calculation_steps.append("• Alevlenir Sıvı: Karışımda Alevlenir Sıvı Kat 3 bileşeni bulundu -> Kategori 3 (H226)")

        # --- B. CİLT AŞINMASI VE TAHRİŞİ (SKIN CORROSION / IRRITATION) ---
        is_skin_corr_1 = False
        is_skin_irrit_2 = False

        if c_skin_corr_1 >= 5.0:
            is_skin_corr_1 = True
            siniflandirmalar.append({"zararlilik_sinifi": "Cilt Aşınması / Tahrişi", "kategori": "Kategori 1", "h_kodu": "H314"})
            h_codes.add("H314")
            piktogram_set.add("GHS05")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Cilt Aşınması: ∑(Cilt Aşınması Kat 1) = %{c_skin_corr_1:.1f} >= %5.0 -> Sınıflandırıldı: Kategori 1 (H314)")
        else:
            skin_irrit_sum = (10.0 * c_skin_corr_1) + c_skin_irrit_2
            if skin_irrit_sum >= 10.0:
                is_skin_irrit_2 = True
                siniflandirmalar.append({"zararlilik_sinifi": "Cilt Aşınması / Tahrişi", "kategori": "Kategori 2", "h_kodu": "H315"})
                h_codes.add("H315")
                piktogram_set.add("GHS07")
                if uyari_kelimesi != "Tehlike":
                    uyari_kelimesi = "Dikkat"
                calculation_steps.append(f"• Cilt Tahrişi: (10 x ∑Cilt 1 [%{c_skin_corr_1:.1f}]) + ∑Cilt 2 [%{c_skin_irrit_2:.1f}] = %{skin_irrit_sum:.1f} >= %10.0 -> Sınıflandırıldı: Kategori 2 (H315)")
            else:
                calculation_steps.append(f"• Cilt Aşınması/Tahrişi: Eşik değerler aşılmadı (Cilt 1: %{c_skin_corr_1:.1f} < %5, Tahriş toplamı: %{skin_irrit_sum:.1f} < %10)")

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
            euh_codes.add("EUH204")
            calculation_steps.append(f"• Solunum Hassaslaşması: %0.1 <= %{c_resp_sens_1:.1f} < %0.2 -> EUH204 (İzosiyanat içerir) tetiklendi.")

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
        if c_muta1 >= 0.1:
            siniflandirmalar.append({"zararlilik_sinifi": "Eşey Hücre Mutajenitesi", "kategori": "Kategori 1B", "h_kodu": "H340"})
            h_codes.add("H340")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Mutajenite: ∑(Muta 1) = %{c_muta1:.1f} >= %0.1 -> Sınıflandırıldı: Kategori 1B (H340)")
        elif c_muta2 >= 1.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Eşey Hücre Mutajenitesi", "kategori": "Kategori 2", "h_kodu": "H341"})
            h_codes.add("H341")
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Mutajenite: ∑(Muta 2) = %{c_muta2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H341)")

        if c_carc1 >= 0.1:
            siniflandirmalar.append({"zararlilik_sinifi": "Kanserojenite", "kategori": "Kategori 1B", "h_kodu": "H350"})
            h_codes.add("H350")
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Kanserojenite: ∑(Carc 1) = %{c_carc1:.1f} >= %0.1 -> Sınıflandırıldı: Kategori 1B (H350)")
        elif c_carc2 >= 1.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Kanserojenite", "kategori": "Kategori 2", "h_kodu": "H351"})
            h_codes.add("H351")
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Kanserojenite: ∑(Carc 2) = %{c_carc2:.1f} >= %1.0 -> Sınıflandırıldı: Kategori 2 (H351)")

        if c_repr1 >= 0.3:
            h_repr = repr_h_specific if repr_h_specific and repr_h_specific.startswith("H360") else "H360D"
            siniflandirmalar.append({"zararlilik_sinifi": "Üreme Sistemi Toksisitesi", "kategori": "Kategori 1B", "h_kodu": h_repr})
            h_codes.add(h_repr)
            piktogram_set.add("GHS08")
            uyari_kelimesi = "Tehlike"
            calculation_steps.append(f"• Üreme Toksisitesi: ∑(Repr 1) = %{c_repr1:.1f} >= %0.3 -> Sınıflandırıldı: Kategori 1B ({h_repr})")
        elif c_repr2 >= 3.0:
            h_repr = repr_h_specific if repr_h_specific and repr_h_specific.startswith("H361") else "H361d"
            siniflandirmalar.append({"zararlilik_sinifi": "Üreme Sistemi Toksisitesi", "kategori": "Kategori 2", "h_kodu": h_repr})
            h_codes.add(h_repr)
            piktogram_set.add("GHS08")
            if uyari_kelimesi != "Tehlike":
                uyari_kelimesi = "Dikkat"
            calculation_steps.append(f"• Üreme Toksisitesi: ∑(Repr 2) = %{c_repr2:.1f} >= %3.0 -> Sınıflandırıldı: Kategori 2 ({h_repr})")

        # --- H. SUCUL ÇEVRE ZARARLARI (AQUATIC HAZARDS) ---
        if c_aq_chronic1 >= 25.0:
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 1", "h_kodu": "H410"})
            h_codes.add("H410")
            piktogram_set.add("GHS09")
            calculation_steps.append(f"• Sucul Çevre: ∑(Kronik 1) = %{c_aq_chronic1:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 1 (H410)")
        elif (10.0 * c_aq_chronic1 + c_aq_chronic2) >= 25.0:
            chr2_sum = (10.0 * c_aq_chronic1 + c_aq_chronic2)
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 2", "h_kodu": "H411"})
            h_codes.add("H411")
            piktogram_set.add("GHS09")
            calculation_steps.append(f"• Sucul Çevre: (10 x ∑Kronik 1) + ∑Kronik 2 = %{chr2_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 2 (H411)")
        elif (100.0 * c_aq_chronic1 + 10.0 * c_aq_chronic2 + c_aq_chronic3) >= 25.0:
            chr3_sum = (100.0 * c_aq_chronic1 + 10.0 * c_aq_chronic2 + c_aq_chronic3)
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 3", "h_kodu": "H412"})
            h_codes.add("H412")
            calculation_steps.append(f"• Sucul Çevre: (100 x ∑Kronik 1) + (10 x ∑Kronik 2) + ∑Kronik 3 = %{chr3_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 3 (H412)")
        elif (c_aq_chronic1 + c_aq_chronic2 + c_aq_chronic3 + c_aq_chronic4) >= 25.0:
            chr4_sum = (c_aq_chronic1 + c_aq_chronic2 + c_aq_chronic3 + c_aq_chronic4)
            siniflandirmalar.append({"zararlilik_sinifi": "Sucul Ortama Zararlı - Kronik", "kategori": "Kronik Kategori 4", "h_kodu": "H413"})
            h_codes.add("H413")
            calculation_steps.append(f"• Sucul Çevre: Toplam Kronik = %{chr4_sum:.1f} >= %25.0 -> Sınıflandırıldı: Sucul Kronik 4 (H413)")

        # EUH066 check
        if has_solvents and not is_skin_irrit_2 and not is_skin_corr_1:
            euh_codes.add("EUH066")
            calculation_steps.append("• İlave Bilgi: Solvent içeriği mevcut olup Cilt Tahrişi Kat 2 sınırının altında kaldığı için EUH066 eklendi.")

        # --- 3. GHS PİKTOGRAM VE UYARI KELİMESİ ÖNCELİK KURALLARI (SEA MD. 26 & 28) ---
        filtered_piktogramlar = set(piktogram_set)

        # Rule 1: GHS06 vs GHS07
        if "GHS06" in filtered_piktogramlar and "GHS07" in filtered_piktogramlar:
            # If GHS07 is solely from acute tox, it is dropped
            calculation_steps.append("• Piktogram Önceliği (Madde 26): GHS06 (Toksik) mevcut olduğu için Akut Toksisite kaynaklı GHS07 elendi.")

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
