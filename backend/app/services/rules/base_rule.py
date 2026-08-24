"""
Temel Regülatif Kural Arayüzü (Base Regulatory Hazard Rule)
"""

from abc import ABC, abstractmethod
from typing import List
from app.models.regulatory import StructuredSubstance, CalculationContext, RuleResult


class BaseHazardRule(ABC):
    """
    SEA Yönetmeliği ve CLP uyarınca tek bir zararlılık sınıfını değerlendiren
    soyut kural stratejisi (Strategy Pattern).
    """

    @property
    @abstractmethod
    def rule_name(self) -> str:
        """Kuralın tekil adı"""
        pass

    @abstractmethod
    def evaluate(
        self,
        context: CalculationContext,
        substances: List[StructuredSubstance]
    ) -> RuleResult:
        """
        Karışım parametreleri ve yapılandırılmış bileşenleri değerlendirir.
        """
        pass
