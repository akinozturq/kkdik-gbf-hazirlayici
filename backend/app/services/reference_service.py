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
        self._load_data()

    def _load_data(self):
        h_path = os.path.join(DATA_DIR, "h_statements.json")
        p_path = os.path.join(DATA_DIR, "p_statements.json")
        pic_path = os.path.join(DATA_DIR, "pictograms.json")

        if os.path.exists(h_path):
            with open(h_path, "r", encoding="utf-8") as f:
                self._h_statements = json.load(f)

        if os.path.exists(p_path):
            with open(p_path, "r", encoding="utf-8") as f:
                self._p_statements = json.load(f)

        if os.path.exists(pic_path):
            with open(pic_path, "r", encoding="utf-8") as f:
                self._pictograms = json.load(f)

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


reference_service = ReferenceService()
