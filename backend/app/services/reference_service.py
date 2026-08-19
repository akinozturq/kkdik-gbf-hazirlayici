"""
Referans Veri Servisi (H-kodları, P-kodları, GHS Piktogramları)
"""

import json
import os
import re
from typing import Dict, List, Optional, Any, Union
from app.schemas.reference import HStatementItem, PStatementItem, PictogramItem
from app.schemas.sds_sections import SDSModel

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class ReferenceService:
    def __init__(self):
        self._h_statements: Dict[str, Dict[str, Any]] = {}
        self._p_statements: Dict[str, Dict[str, Any]] = {}
        self._pictograms: Dict[str, Dict[str, Any]] = {}
        self._exposure_limits: List[Dict[str, Any]] = []
        self._raw_materials: List[Dict[str, Any]] = []
        self._load_data()

    def _load_data(self):
        h_path = os.path.join(DATA_DIR, "h_statements.json")
        p_path = os.path.join(DATA_DIR, "p_statements.json")
        pic_path = os.path.join(DATA_DIR, "pictograms.json")
        exp_path = os.path.join(DATA_DIR, "exposure_limits.json")
        raw_path = os.path.join(DATA_DIR, "raw_materials.json")

        if os.path.exists(h_path):
            with open(h_path, "r", encoding="utf-8") as f:
                self._h_statements = json.load(f)

        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                self._p_statements = json.load(f)

        if os.path.exists(pic_path):
            with open(pic_path, "r", encoding="utf-8") as f:
                self._pictograms = json.load(f)

        if os.path.exists(exp_path):
            with open(exp_path, "r", encoding="utf-8") as f:
                self._exposure_limits = json.load(f)

        if os.path.exists(raw_path):
            with open(raw_path, "r", encoding="utf-8") as f:
                self._raw_materials = json.load(f)

    def get_all_h_statements(self, category: Optional[str] = None, search: Optional[str] = None) -> List[HStatementItem]:
        results = []
        for code, item in self._h_statements.items():
            if category and item.get("category", "").lower() != category.lower():
                continue
            if search:
                query = search.lower()
                if query not in code.lower() and query not in item.get("text", "").lower():
                    continue
            results.append(HStatementItem(
                code=code,
                category=item.get("category", ""),
                text=item.get("text", "")
            ))
        return sorted(results, key=lambda x: x.code)

    def get_h_statement(self, code: str) -> Optional[HStatementItem]:
        code = code.strip().upper()
        if code in self._h_statements:
            item = self._h_statements[code]
            return HStatementItem(code=code, category=item.get("category", ""), text=item.get("text", ""))
        return None

    def get_all_p_statements(self, type_filter: Optional[str] = None, search: Optional[str] = None) -> List[PStatementItem]:
        results = []
        for code, item in self._p_statements.items():
            if type_filter and item.get("type", "").lower() != type_filter.lower():
                continue
            if search:
                query = search.lower()
                if query not in code.lower() and query not in item.get("text", "").lower():
                    continue
            results.append(PStatementItem(
                code=code,
                type=item.get("type", ""),
                text=item.get("text", "")
            ))
        return sorted(results, key=lambda x: x.code)

    def get_p_statement(self, code: str) -> Optional[PStatementItem]:
        code = code.strip().upper()
        if code in self._p_statements:
            item = self._p_statements[code]
            return PStatementItem(code=code, type=item.get("type", ""), text=item.get("text", ""))
        return None

    def get_all_pictograms(self) -> List[PictogramItem]:
        results = []
        for code, item in self._pictograms.items():
            results.append(PictogramItem(
                code=code,
                name=item.get("name", ""),
                symbol=item.get("symbol", ""),
                description=item.get("description", "")
            ))
        return sorted(results, key=lambda x: x.code)

    def get_pictogram(self, code: str) -> Optional[PictogramItem]:
        code = code.strip().upper()
        if code in self._pictograms:
            item = self._pictograms[code]
            return PictogramItem(
                code=code,
                name=item.get("name", ""),
                symbol=item.get("symbol", ""),
                description=item.get("description", "")
            )
        return None

    def extract_h_codes_from_sds(self, sds: Union[SDSModel, Dict[str, Any]]) -> List[str]:
        """
        SDS verisindeki tüm bölümleri (özellikle B2 ve B3) tarayarak geçen H ve EUH kodlarını bulur.
        """
        if isinstance(sds, dict):
            sds_dict = sds
        else:
            sds_dict = sds.model_dump()

        found_codes = set()
        pattern = re.compile(r'\b(H\d{3}[a-zA-Z]*|EUH\d{3})\b', re.IGNORECASE)

        # 1. B2.1 sınıflandırmalar
        b2_1 = sds_dict.get("b2_zarar_tanimi", {}).get("b2_1", {})
        for item in b2_1.get("siniflandirmalar", []):
            if isinstance(item, dict):
                h_kodu = item.get("h_kodu", "")
                for match in pattern.findall(h_kodu):
                    found_codes.add(match.upper())

        # 2. B2.2 h_ifadeleri
        b2_2 = sds_dict.get("b2_zarar_tanimi", {}).get("b2_2", {})
        for h in b2_2.get("h_ifadeleri", []):
            for match in pattern.findall(str(h)):
                found_codes.add(match.upper())

        # 3. B3.2 Karışım bileşenleri sınıflandırmaları
        b3_2 = sds_dict.get("b3_bilesim", {}).get("karisim", {})
        if b3_2:
            for comp in b3_2.get("bilesenler", []):
                if isinstance(comp, dict):
                    sinif = comp.get("siniflandirma", "")
                    for match in pattern.findall(str(sinif)):
                        found_codes.add(match.upper())

        return sorted(list(found_codes))

    def get_all_exposure_limits(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Mesleki Maruziyet Sınır Değerleri tablosundaki (311 kimyasal) kayıtları döner.
        """
        if not search:
            return self._exposure_limits

        query = search.lower().strip()
        matched = []
        for item in self._exposure_limits:
            if (
                query in item.get("name", "").lower()
                or query in item.get("cas", "").lower()
                or query in item.get("einecs", "").lower()
            ):
                matched.append(item)
        return matched

    def find_exposure_limit(
        self,
        cas: Optional[str] = None,
        ec: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        CAS No, EC No veya Madde Adına göre mesleki maruziyet sınır değerini bulur.
        """
        clean_cas = cas.strip() if cas else ""
        clean_ec = ec.strip() if ec else ""
        clean_name = name.strip().lower() if name else ""

        # 1. Exact CAS match
        if clean_cas:
            for item in self._exposure_limits:
                item_cas = item.get("cas", "")
                if clean_cas in item_cas.split("\n") or clean_cas == item_cas:
                    return item

        # 2. Exact EC/EINECS match
        if clean_ec:
            for item in self._exposure_limits:
                if clean_ec == item.get("einecs", ""):
                    return item

        # 3. Substance name match
        if clean_name:
            # Exact or substring match
            for item in self._exposure_limits:
                item_name = item.get("name", "").lower()
                if clean_name == item_name or clean_name in item_name or item_name in clean_name:
                    return item

        return None

    def auto_match_exposure_limits_from_sds(self, sds: Union[SDSModel, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        SDS'in Bölüm 3'ündeki (3.1 madde veya 3.2 karışım bileşenleri) kimyasalları tarayarak
        Mesleki Maruziyet Sınır Değerleri tablosuyla eşleştirir ve Bölüm 8.1 için satırlar üretir.
        """
        if isinstance(sds, dict):
            sds_dict = sds
        else:
            sds_dict = sds.model_dump()

        components_to_check = []
        b3 = sds_dict.get("b3_bilesim", {})
        tip = b3.get("tip", "karisim")

        if tip == "madde":
            m = b3.get("madde", {})
            components_to_check.append({
                "ad": m.get("kimyasal_kimlik") or "",
                "cas_no": m.get("cas_no") or "",
                "ec_no": m.get("ec_no") or ""
            })
        else:
            for c in b3.get("karisim", {}).get("bilesenler", []):
                if isinstance(c, dict):
                    components_to_check.append({
                        "ad": c.get("ad") or "",
                        "cas_no": c.get("cas_no") or "",
                        "ec_no": c.get("ec_no") or ""
                    })

        results = []
        seen_keys = set()

        for comp in components_to_check:
            matched = self.find_exposure_limit(
                cas=comp.get("cas_no"),
                ec=comp.get("ec_no"),
                name=comp.get("ad")
            )
            if matched:
                item_key = matched.get("cas") or matched.get("name")
                if item_key in seen_keys:
                    continue
                seen_keys.add(item_key)

                # Format sinir_degeri string
                twa_parts = []
                if matched.get("twa_ppm"):
                    twa_parts.append(f"{matched['twa_ppm']} ppm")
                if matched.get("twa_mg_m3"):
                    twa_parts.append(f"{matched['twa_mg_m3']} mg/m³")
                twa_str = f"TWA (8 Saat): {', '.join(twa_parts)}" if twa_parts else ""

                stel_parts = []
                if matched.get("stel_ppm"):
                    stel_parts.append(f"{matched['stel_ppm']} ppm")
                if matched.get("stel_mg_m3"):
                    stel_parts.append(f"{matched['stel_mg_m3']} mg/m³")
                stel_str = f"STEL (15 Dak.): {', '.join(stel_parts)}" if stel_parts else ""

                ceiling_parts = []
                if matched.get("ceiling_ppm"):
                    ceiling_parts.append(f"{matched['ceiling_ppm']} ppm")
                if matched.get("ceiling_mg_m3"):
                    ceiling_parts.append(f"{matched['ceiling_mg_m3']} mg/m³")
                ceiling_str = f"Tavan Değer: {', '.join(ceiling_parts)}" if ceiling_parts else ""

                notes_str = f"[{matched['notes']}]" if matched.get("notes") else ""

                val_parts = [p for p in [twa_str, stel_str, ceiling_str, notes_str] if p]
                sinir_degeri = " | ".join(val_parts) if val_parts else "Mevzuatta sınır değer belirlenmiştir."

                madde_label = comp.get("ad") or matched.get("name")
                id_info = []
                if comp.get("cas_no") or matched.get("cas"):
                    id_info.append(f"CAS: {comp.get('cas_no') or matched.get('cas')}")
                if comp.get("ec_no") or matched.get("einecs"):
                    id_info.append(f"EC: {comp.get('ec_no') or matched.get('einecs')}")
                if id_info:
                    madde_label += f" ({', '.join(id_info)})"

                results.append({
                    "madde": madde_label,
                    "sinir_degeri": sinir_degeri,
                    "birim": "mg/m³ / ppm",
                    "yasal_dayanak": matched.get("yasal_dayanak") or "Kimyasal Maddelerle Çalışmalarda Sağlık ve Güvenlik Önlemleri Hakkında Yönetmelik (Ek-1)"
                })

        return results

    def format_h_statements(self, h_codes: List[str]) -> List[str]:
        """
        Verilen H-kodları listesini Bölüm 16 için standart tam metin haline dönüştürür.
        Örnek: 'H225: Kolay alevlenir sıvı ve buhar.'
        """
        formatted = []
        for code in h_codes:
            code_upper = code.strip().upper()
            item = self.get_h_statement(code_upper)
            if item:
                formatted.append(f"{item.code}: {item.text}")
            else:
                formatted.append(f"{code_upper}: [Metin sözlükte tanımlı değil]")
        return formatted

    def get_all_raw_materials(self, search: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Hammadde Kütüphanesindeki kimyasal maddeleri döner.
        """
        if not search:
            return self._raw_materials

        query = search.lower().strip()
        matched = []
        for item in self._raw_materials:
            if (
                query in item.get("ad", "").lower()
                or query in item.get("ticari_ad", "").lower()
                or query in item.get("cas_no", "").lower()
                or query in item.get("ec_no", "").lower()
                or query in item.get("kategori", "").lower()
            ):
                matched.append(item)
        return matched

    def get_raw_material_by_id(self, id_or_cas: str) -> Optional[Dict[str, Any]]:
        """
        ID veya CAS numarasına göre hammadde detayını döner.
        """
        clean = id_or_cas.strip().lower()
        for item in self._raw_materials:
            if item.get("id", "").lower() == clean or item.get("cas_no", "").lower() == clean:
                return item
        return None


reference_service = ReferenceService()

