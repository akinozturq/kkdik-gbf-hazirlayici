"""
CLP / SEA Madde 26 Piktogram Öncelik ve Baskılama Matrisi (Pictogram Precedence Matrix)
Mevzuat: SEA Yönetmeliği Madde 26 & CLP Article 26 (Principles of precedence for hazard pictograms)

Bu modül piktogram öncelik ve eleme mantığını kod içerisindeki if-else zincirlerinden çıkarıp
merkezi, deklaratif ve veri güdümlü bir matris yapısına dönüştürür.
"""

import os
import json
import logging
from typing import List, Dict, Set, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict

logger = logging.getLogger(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
DEFAULT_MATRIX_PATH = os.path.join(DATA_DIR, "pictogram_precedence_matrix.json")


class PrecedenceRule(BaseModel):
    """
    Tekil bir piktogram öncelik ve baskılama kuralı.
    Örn: GHS06 (dominant) varken GHS07 (suppressed) elenir;
         ancak karışımda preserving_h_codes (H315, H319 vb.) varsa GHS07 korunur.
    """
    rule_id: str = Field(..., description="Kural tekil kodu (örn. 'PREC_01_GHS06_OVER_GHS07')")
    dominant_pictogram: str = Field(..., description="Baskılayan öncelikli piktogram (örn. 'GHS06')")
    suppressed_pictogram: str = Field(..., description="Baskılanacak piktogram (örn. 'GHS07')")
    trigger_h_codes: List[str] = Field(
        default_factory=list,
        description="Baskılamanın geçerli olması için karışımda bulunması gereken H-kodları (boşsa sadece dominant piktogram yeterlidir)"
    )
    preserving_h_codes: List[str] = Field(
        default_factory=list,
        description="Karışımda bu kodlardan herhangi biri varsa baskılama uygulanmaz, piktogram korunur"
    )
    legal_reference: str = Field("", description="Mevzuat maddesi referansı (SEA md. 26 / CLP Art. 26)")
    description: str = Field("", description="Kuralın insan tarafından okunabilir açıklaması")

    model_config = ConfigDict(populate_by_name=True)


class PrecedenceAuditEntry(BaseModel):
    """
    Piktogram baskılama denetim izi kaydı (Audit Trail).
    """
    rule_id: str
    dominant_pictogram: str
    suppressed_pictogram: str
    legal_reference: str
    reason: str


class PictogramPrecedenceMatrix:
    """
    Merkezi, veri güdümlü Piktogram Öncelik Matrisi motoru.
    """

    def __init__(self, rules: Optional[List[PrecedenceRule]] = None):
        self.rules: List[PrecedenceRule] = rules if rules is not None else self._load_or_default()

    @classmethod
    def _default_rules(cls) -> List[PrecedenceRule]:
        """Yerleşik varsayılan SEA Madde 26 kuralları (dosya bulunamadığında emniyet kemeri)."""
        return [
            PrecedenceRule(
                rule_id="PREC_01_GHS06_OVER_GHS07",
                dominant_pictogram="GHS06",
                suppressed_pictogram="GHS07",
                trigger_h_codes=["H300", "H301", "H310", "H311", "H330", "H331"],
                preserving_h_codes=["H315", "H319", "H317", "H335", "H336"],
                legal_reference="SEA Madde 26(1)(a) / CLP Article 26.1(a)",
                description="GHS06 (Kafatası) varsa, akut toksisiteden gelen GHS07 (Ünlem) elenir."
            ),
            PrecedenceRule(
                rule_id="PREC_02_GHS05_OVER_GHS07",
                dominant_pictogram="GHS05",
                suppressed_pictogram="GHS07",
                trigger_h_codes=["H314", "H318"],
                preserving_h_codes=["H302", "H312", "H332", "H317", "H335", "H336"],
                legal_reference="SEA Madde 26(1)(b) / CLP Article 26.1(b)",
                description="GHS05 (Aşındırıcı) varsa, cilt veya göz tahrişinden gelen GHS07 elenir."
            ),
            PrecedenceRule(
                rule_id="PREC_03_GHS08_OVER_GHS07",
                dominant_pictogram="GHS08",
                suppressed_pictogram="GHS07",
                trigger_h_codes=["H334"],
                preserving_h_codes=["H302", "H312", "H332", "H315", "H319", "H335", "H336"],
                legal_reference="SEA Madde 26(1)(c) / CLP Article 26.1(c)",
                description="GHS08 (Solunum Hassaslaştırma - H334) varsa, cilt hassaslaşmasından gelen GHS07 elenir."
            ),
            PrecedenceRule(
                rule_id="PREC_04_GHS01_OVER_GHS02",
                dominant_pictogram="GHS01",
                suppressed_pictogram="GHS02",
                trigger_h_codes=["H200", "H201", "H202", "H203", "H204", "H205"],
                preserving_h_codes=[],
                legal_reference="SEA Madde 26(1)(d) / CLP Article 26.1(d)",
                description="GHS01 (Patlayan bomba) varsa, GHS02 (Alev) etikette isteğe bağlıdır/baskılanır."
            ),
            PrecedenceRule(
                rule_id="PREC_05_GHS01_OVER_GHS03",
                dominant_pictogram="GHS01",
                suppressed_pictogram="GHS03",
                trigger_h_codes=["H200", "H201", "H202", "H203", "H204", "H205"],
                preserving_h_codes=[],
                legal_reference="SEA Madde 26(1)(d) / CLP Article 26.1(d)",
                description="GHS01 (Patlayan bomba) varsa, GHS03 (Alev çemberi) etikette isteğe bağlıdır/baskılanır."
            ),
        ]

    @classmethod
    def _load_or_default(cls) -> List[PrecedenceRule]:
        if os.path.exists(DEFAULT_MATRIX_PATH):
            try:
                with open(DEFAULT_MATRIX_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return [PrecedenceRule(**item) for item in data]
            except Exception as e:
                logger.warning(f"Piktogram öncelik matrisi yüklenemedi, varsayılan kurallar kullanılıyor: {e}")
        return cls._default_rules()

    def resolve(
        self,
        raw_pictograms: Set[str],
        raw_h_codes: Set[str]
    ) -> Tuple[Set[str], List[Dict[str, Any]]]:
        """
        Piktogram kümesini öncelik kurallarına göre değerlendirir.
        
        Döner:
            (filtered_pictograms, audit_log)
        """
        filtered_p = set(raw_pictograms)
        audit_log: List[Dict[str, Any]] = []

        for rule in self.rules:
            # 1. Dominant piktogram karışımda var mı?
            if rule.dominant_pictogram not in filtered_p:
                continue

            # 2. Baskılanacak piktogram karışımda var mı?
            if rule.suppressed_pictogram not in filtered_p:
                continue

            # 3. Tetikleyici H-kodu şartı var mı ve sağlanıyor mu?
            if rule.trigger_h_codes:
                if not any(c in raw_h_codes for c in rule.trigger_h_codes):
                    continue

            # 4. Koruyucu H-kodları var mı? (Eğer varsa piktogram elenmez!)
            if rule.preserving_h_codes and any(c in raw_h_codes for c in rule.preserving_h_codes):
                continue

            # 5. Baskılama uygula
            filtered_p.discard(rule.suppressed_pictogram)
            audit_log.append({
                "rule_id": rule.rule_id,
                "dominant_pictogram": rule.dominant_pictogram,
                "suppressed_pictogram": rule.suppressed_pictogram,
                "legal_reference": rule.legal_reference,
                "reason": rule.description
            })

        return filtered_p, audit_log
