"""
Standart Cümle Kataloğu (Phrase Bank) Servisi
EuPhraC standardına uygun resmi çok dilli güvenlik ifadelerini yönetir.
"""

import os
import json
from typing import List, Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "standard_phrases.json")


class PhraseService:
    _phrases_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def _load_phrases(cls) -> List[Dict[str, Any]]:
        if cls._phrases_cache is None:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    cls._phrases_cache = json.load(f)
            else:
                cls._phrases_cache = []
        return cls._phrases_cache

    @classmethod
    def get_phrases(
        cls,
        section: Optional[str] = None,
        subfield: Optional[str] = None,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Bölüm, alt alan veya anahtar kelimelere göre standart cümleleri filtreler.
        """
        phrases = cls._load_phrases()
        results = phrases

        if section:
            clean_sec = section.strip().lower()
            results = [p for p in results if p.get("section", "").lower() == clean_sec]

        if subfield:
            clean_sub = subfield.strip().lower()
            results = [p for p in results if p.get("subfield", "").lower() == clean_sub]

        if query:
            q = query.strip().lower()
            filtered = []
            for p in results:
                title = p.get("title_tr", "").lower()
                text_tr = p.get("text_tr", "").lower()
                text_en = p.get("text_en", "").lower()
                keywords = [k.lower() for k in p.get("keywords", [])]
                if q in title or q in text_tr or q in text_en or any(q in kw for kw in keywords):
                    filtered.append(p)
            results = filtered

        return results


phrase_service = PhraseService()
