import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../api/client';
import { SECTOR_PRESETS } from '../data/sectorPresets';

const AppContext = createContext();

export function AppProvider({ children }) {
  // Navigation
  const [currentView, setCurrentView] = useState('list'); // 'list' | 'wizard'
  const [activeStep, setActiveStep] = useState(1); // 1 to 16

  // Active Product & Form State
  const [activeProductId, setActiveProductId] = useState(null);
  const [product, setProduct] = useState(null);
  const [sdsData, setSdsData] = useState(null);

  // Autosave status: 'idle' | 'saving' | 'saved' | 'error'
  const [autosaveStatus, setAutosaveStatus] = useState('idle');
  const [lastSavedTime, setLastSavedTime] = useState(null);
  const debounceTimerRef = useRef(null);

  // Validation
  const [validationReport, setValidationReport] = useState(null);
  const [isValidationOpen, setIsValidationOpen] = useState(false);

  // Sector Presets Modal State
  const [isPresetModalOpen, setIsPresetModalOpen] = useState(false);

  // Reference Cache
  const [hStatements, setHStatements] = useState([]);
  const [pStatements, setPStatements] = useState([]);
  const [pictograms, setPictograms] = useState([]);

  // Load references on mount
  useEffect(() => {
    async function loadRefs() {
      try {
        const [hList, pList, picList] = await Promise.all([
          api.getHStatements(),
          api.getPStatements(),
          api.getPictograms(),
        ]);
        setHStatements(hList);
        setPStatements(pList);
        setPictograms(picList);
      } catch (err) {
        console.error('Referans verileri yüklenemedi:', err);
      }
    }
    loadRefs();
  }, []);

  // Open Product in Wizard
  const openProduct = async (id, step = 1) => {
    try {
      setAutosaveStatus('idle');
      const prod = await api.getProduct(id);
      setActiveProductId(id);
      setProduct(prod);
      setSdsData(prod.sds_data || {});
      setActiveStep(step);
      setCurrentView('wizard');

      // Fetch validation
      const valRes = await api.validateProduct(id);
      setValidationReport(valRes);
    } catch (err) {
      alert('Ürün yüklenirken hata oluştu: ' + err.message);
    }
  };

  // Return to List View
  const goToList = () => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    setCurrentView('list');
    setActiveProductId(null);
    setProduct(null);
    setSdsData(null);
  };

  // Perform Immediate Save
  const saveNow = async (customSdsData = null) => {
    if (!activeProductId) return;
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    const dataToSave = customSdsData || sdsData;
    setAutosaveStatus('saving');
    try {
      const updated = await api.updateProduct(activeProductId, {
        sds_data: dataToSave,
      });
      setProduct(updated);
      setSdsData(updated.sds_data || {});
      setAutosaveStatus('saved');
      setLastSavedTime(new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

      // Refresh validation
      const valRes = await api.validateProduct(activeProductId);
      setValidationReport(valRes);
    } catch (err) {
      console.error('Kaydetme hatası:', err);
      setAutosaveStatus('error');
    }
  };

  // Update SDS Field (Debounced Autosave)
  const updateSdsField = useCallback((pathArray, value) => {
    setSdsData((prev) => {
      if (!prev) return prev;
      const next = JSON.parse(JSON.stringify(prev));

      let current = next;
      for (let i = 0; i < pathArray.length - 1; i++) {
        const key = pathArray[i];
        if (!current[key] || typeof current[key] !== 'object') {
          current[key] = {};
        }
        current = current[key];
      }
      current[pathArray[pathArray.length - 1]] = value;

      // Trigger Debounced Autosave (750ms)
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
      setAutosaveStatus('saving');

      debounceTimerRef.current = setTimeout(async () => {
        try {
          const updated = await api.updateProduct(activeProductId, {
            sds_data: next,
          });
          setProduct(updated);
          setAutosaveStatus('saved');
          setLastSavedTime(new Date().toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

          // Refresh validation in background
          const valRes = await api.validateProduct(activeProductId);
          setValidationReport(valRes);
        } catch (err) {
          console.error('Autosave başarısız:', err);
          setAutosaveStatus('error');
        }
      }, 750);

      return next;
    });
  }, [activeProductId]);

  // Map step number to sds section key
  const getSectionKeyByStep = (step) => {
    const map = {
      1: 'b1_kimlik',
      2: 'b2_zarar_tanimi',
      3: 'b3_bilesim',
      4: 'b4_ilk_yardim',
      5: 'b5_yangin_mucadele',
      6: 'b6_kaza_sonucu_yayilma',
      7: 'b7_ellecme_depolama',
      8: 'b8_maruz_kalma_kontrolu',
      9: 'b9_fiziksel_kimyasal_ozellikler',
      10: 'b10_kararlilik_tepkime',
      11: 'b11_toksikolojik',
      12: 'b12_ekolojik',
      13: 'b13_bertaraf',
      14: 'b14_tasimacilik',
      15: 'b15_mevzuat',
      16: 'b16_diger_bilgiler',
    };
    return map[step];
  };

  // Apply Sector Preset
  const applySectorPreset = async (presetId, { scope = 'all', overwrite = false, targetStep = null } = {}) => {
    const preset = SECTOR_PRESETS.find((p) => p.id === presetId);
    if (!preset || !activeProductId) return;

    setSdsData((prev) => {
      const next = JSON.parse(JSON.stringify(prev || {}));

      let keysToApply = Object.keys(preset.sections);
      if (scope === 'current' && targetStep) {
        const singleKey = getSectionKeyByStep(targetStep);
        keysToApply = singleKey && preset.sections[singleKey] ? [singleKey] : [];
      }

      const mergeDeep = (target, source) => {
        for (const k in source) {
          if (typeof source[k] === 'object' && source[k] !== null && !Array.isArray(source[k])) {
            if (!target[k] || typeof target[k] !== 'object') {
              target[k] = {};
            }
            mergeDeep(target[k], source[k]);
          } else {
            const isEmpty = target[k] === undefined || target[k] === null || target[k] === '' || (Array.isArray(target[k]) && target[k].length === 0);
            if (overwrite || isEmpty) {
              target[k] = source[k];
            }
          }
        }
      };

      keysToApply.forEach((secKey) => {
        if (!next[secKey]) next[secKey] = {};
        mergeDeep(next[secKey], preset.sections[secKey]);
      });

      // Perform immediate save
      saveNow(next);
      return next;
    });
  };

  // Refresh validation
  const refreshValidation = async () => {
    if (!activeProductId) return;
    try {
      const valRes = await api.validateProduct(activeProductId);
      setValidationReport(valRes);
      return valRes;
    } catch (err) {
      console.error('Doğrulama yenilenemedi:', err);
    }
  };

  // Auto Fill H-Statements
  const autoFillHStatements = async () => {
    if (!activeProductId) return;
    try {
      const res = await api.autoFillHCodes(activeProductId, true);
      // Reload product
      const updated = await api.getProduct(activeProductId);
      setProduct(updated);
      setSdsData(updated.sds_data || {});
      await refreshValidation();
      return res;
    } catch (err) {
      alert('H-ifadeleri otomatik doldurulurken hata: ' + err.message);
    }
  };

  return (
    <AppContext.Provider
      value={{
        currentView,
        setCurrentView,
        activeStep,
        setActiveStep,
        activeProductId,
        product,
        setProduct,
        sdsData,
        setSdsData,
        autosaveStatus,
        lastSavedTime,
        validationReport,
        isValidationOpen,
        setIsValidationOpen,
        isPresetModalOpen,
        setIsPresetModalOpen,
        applySectorPreset,
        hStatements,
        pStatements,
        pictograms,
        openProduct,
        goToList,
        saveNow,
        updateSdsField,
        refreshValidation,
        autoFillHStatements,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
}
