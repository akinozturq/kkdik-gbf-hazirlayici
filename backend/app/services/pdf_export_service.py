import io
import os
import base64
from jinja2 import Environment, FileSystemLoader

# NOT: xhtml2pdf ve reportlab import'ları modül seviyesinden kaldırıldı.
# Bu kütüphaneler yalnızca PDF oluşturma anında (lazy import) yüklenir.
# Böylece bu paketler kurulu olmasa bile test collection ve diğer servisler etkilenmez.

_pdf_libs_loaded = False
_pisa = None
_xhtml2pdf_default = None
_rl_config = None
_pdfmetrics = None
_TTFont = None
_registerFontFamily = None


def _ensure_pdf_libs():
    """PDF kütüphanelerini ilk kullanımda yükler (lazy import)."""
    global _pdf_libs_loaded, _pisa, _xhtml2pdf_default
    global _rl_config, _pdfmetrics, _TTFont, _registerFontFamily
    if _pdf_libs_loaded:
        return
    try:
        from reportlab import rl_config as _rl_cfg
        from reportlab.pdfbase import pdfmetrics as _pm
        from reportlab.pdfbase.ttfonts import TTFont as _ttf
        from reportlab.pdfbase.pdfmetrics import registerFontFamily as _rff
        import xhtml2pdf.default as _xd
        from xhtml2pdf import pisa as _p

        _rl_config = _rl_cfg
        _pdfmetrics = _pm
        _TTFont = _ttf
        _registerFontFamily = _rff
        _xhtml2pdf_default = _xd
        _pisa = _p

        # Allow ReportLab to gracefully handle dynamic table padding
        _rl_config.allowTableBoundsErrors = 3
        _pdf_libs_loaded = True
    except ImportError as e:
        raise ImportError(
            f"PDF oluşturma için gerekli kütüphane yüklenemedi: {e}. "
            "Lütfen 'pip install xhtml2pdf reportlab' komutunu çalıştırınız."
        ) from e

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
FONTS_DIR = os.path.join(TEMPLATE_DIR, "fonts")
ASSETS_DIR = os.path.join(TEMPLATE_DIR, "docx_assets")
if not os.path.exists(ASSETS_DIR):
    ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "templates", "docx_assets")

# Register Google Sans TrueType Fonts for Turkish character encoding and strict typography
_FONTS_REGISTERED = False

def _register_fonts():
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return

    _ensure_pdf_libs()

    gs_reg = os.path.join(FONTS_DIR, "GoogleSans-Regular.ttf")
    gs_bold = os.path.join(FONTS_DIR, "GoogleSans-Bold.ttf")
    gs_italic = os.path.join(FONTS_DIR, "GoogleSans-Italic.ttf")
    gs_bi = os.path.join(FONTS_DIR, "GoogleSans-BoldItalic.ttf")

    # Fallback to Windows user fonts folder dynamically if not in template fonts
    if not os.path.exists(gs_reg):
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            win_fonts = os.path.join(local_app_data, "Microsoft", "Windows", "Fonts")
            if os.path.exists(os.path.join(win_fonts, "GoogleSans-Regular.ttf")):
                gs_reg = os.path.join(win_fonts, "GoogleSans-Regular.ttf")
                gs_bold = os.path.join(win_fonts, "GoogleSans-Bold.ttf")
                gs_italic = os.path.join(win_fonts, "GoogleSans-Italic.ttf")
                gs_bi = os.path.join(win_fonts, "GoogleSans-BoldItalic.ttf")

    if os.path.exists(gs_reg):
        _pdfmetrics.registerFont(_TTFont('GoogleSans', gs_reg))
        _pdfmetrics.registerFont(_TTFont('GoogleSans-Bold', gs_bold if os.path.exists(gs_bold) else gs_reg))
        _pdfmetrics.registerFont(_TTFont('GoogleSans-Italic', gs_italic if os.path.exists(gs_italic) else gs_reg))
        _pdfmetrics.registerFont(_TTFont('GoogleSans-BoldItalic', gs_bi if os.path.exists(gs_bi) else gs_reg))

        _registerFontFamily(
            'GoogleSans',
            normal='GoogleSans',
            bold='GoogleSans-Bold',
            italic='GoogleSans-Italic',
            boldItalic='GoogleSans-BoldItalic'
        )

        # Override all fallback font aliases to Google Sans
        for alias in [
            'googlesans', 'googlesans-bold',
            'arial', 'arial-bold',
            'helvetica', 'helvetica-bold',
            'sansserif', 'sans', 'sans-serif'
        ]:
            _xhtml2pdf_default.DEFAULT_FONT[alias] = 'GoogleSans' if 'bold' not in alias else 'GoogleSans-Bold'

        _FONTS_REGISTERED = True

class SafeDict(dict):
    """A dictionary that returns an empty SafeDict for missing keys and empty string on str conversion."""
    def __getitem__(self, key):
        val = super().get(key, None)
        if val is None:
            return SafeDict()
        if isinstance(val, dict) and not isinstance(val, SafeDict):
            return SafeDict(val)
        return val

    def __getattr__(self, key):
        return self[key]

    def __bool__(self):
        return len(self) > 0

    def __str__(self):
        return ""

def to_safe_dict(obj):
    if isinstance(obj, dict):
        return SafeDict({k: to_safe_dict(v) for k, v in obj.items()})
    elif isinstance(obj, list):
        return [to_safe_dict(x) for x in obj]
    return obj

from app.services.translation_service import translation_service
from app.services.reference_service import reference_service


class PdfExportService:
    """
    Renders 16-section KKDİK / REACH Annex II compliant HTML & PDF documents
    with clean monochrome design, Google Sans typography,
    and precise font scaling (12pt main, 11pt sub, 10pt th, 8pt td).
    """

    @classmethod
    def _load_base64_logo(cls, filename: str) -> str:
        paths = [
            os.path.join(ASSETS_DIR, filename),
            os.path.join(os.path.dirname(__file__), "..", "templates", "docx_assets", filename),
            os.path.join("templates", "docx_assets", filename)
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
        return ""

    @classmethod
    def _load_base64_pictogram(cls, code: str) -> str:
        if not code or not isinstance(code, str):
            return ""
        code_clean = code.strip()
        pictograms_dir = os.path.join(TEMPLATE_DIR, "pictograms")
        paths = [
            os.path.join(pictograms_dir, f"{code_clean.upper()}.png"),
            os.path.join(pictograms_dir, f"{code_clean.lower()}.png"),
            os.path.join("pictograms", "png", f"{code_clean.upper()}.png"),
            os.path.join("pictograms", "png", f"{code_clean.lower()}.png"),
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                    return f"data:image/png;base64,{b64}"
        return ""

    @classmethod
    def render_html(cls, product_dict: dict, lang: str = "tr") -> str:
        env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            auto_reload=True,
            cache_size=0
        )
        template = env.get_template("gbf_pdf_template.html")

        raw_sds = product_dict.get("sds_data") or {}
        lang_clean = (lang or "tr").lower()
        if lang_clean == "en":
            raw_sds = translation_service.translate_sds_dict(raw_sds, lang="en")
            trans_pname = raw_sds.get("b1_kimlik", {}).get("b1_1", {}).get("madde_karisim_adi")
            if trans_pname:
                product_dict["urun_adi"] = trans_pname
        safe_sds = to_safe_dict(raw_sds)
        t = translation_service.get_sections(lang_clean)

        # Load GHS Pictogram images
        raw_piks = []
        try:
            raw_piks = product_dict.get("sds_data", {}).get("b2_zarar_tanimi", {}).get("b2_2", {}).get("piktogramlar", []) or []
        except Exception:
            pass

        pictogram_images = []
        for pcode in raw_piks:
            if isinstance(pcode, str) and pcode.strip():
                src = cls._load_base64_pictogram(pcode)
                if src:
                    pictogram_images.append({"code": pcode.strip().upper(), "src": src})

        # Signal word translation
        raw_signal = safe_sds.get("b2_zarar_tanimi", {}).get("b2_2", {}).get("uyari_kelimesi") or ""
        translated_signal = translation_service.translate_signal_word(str(raw_signal), lang_clean)

        # Section 16 H-statements in requested language
        if lang_clean == "en":
            found_h_codes = reference_service.extract_h_codes_from_sds(product_dict.get("sds_data") or {})
            translated_h_full = translation_service.format_h_statements(found_h_codes, lang="en")
        else:
            translated_h_full = safe_sds.get("b16_diger_bilgiler", {}).get("tam_h_ifadeleri", [])

        context = {
            "product": product_dict,
            "sds": safe_sds,
            "lang": lang_clean,
            "t": t,
            "translated_signal": translated_signal,
            "translated_h_full": translated_h_full,
            "pictogram_images": pictogram_images,
            "logo_header": cls._load_base64_logo("image1.png"),
            "logo_footer_polchem": cls._load_base64_logo("image2.png"),
            "logo_footer_aypol": cls._load_base64_logo("image3.png"),
            "logo_footer_gokay": cls._load_base64_logo("image4.png"),
        }

        return template.render(context)

    @classmethod
    def generate_pdf(cls, product_dict: dict, lang: str = "tr") -> io.BytesIO:
        _ensure_pdf_libs()
        _register_fonts()
        _rl_config.allowTableBoundsErrors = 3
        html_content = cls.render_html(product_dict, lang=lang)
        pdf_stream = io.BytesIO()

        pisa_status = _pisa.CreatePDF(html_content, dest=pdf_stream, encoding='utf-8')
        if pisa_status.err:
            raise RuntimeError(f"PDF oluşturma sırasında hata meydana geldi (kod: {pisa_status.err})")

        pdf_stream.seek(0)
        return pdf_stream

