import io
import os
import zipfile
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "GBF_ANTET_TEMPLATE.docx")
FONT_NAME = "Google Sans"

def set_cell_margins(cell, top=70, bottom=70, left=100, right=100):
    """Sets cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_cell_borders(cell, color="444444", sz="4", val="single"):
    """Sets clean border around a cell without background fill."""
    tcPr = cell._element.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

class DocxExportService:
    """
    Generates professional 16-section KKDİK compliant Word (.docx) documents
    with strictly separated subheadings according to KKDİK Ek-2 Bölüm B,
    Google Sans typography, and exact font sizes (12pt main, 11pt sub, 10pt normal text & table headers, 8pt table contents).
    """

    @classmethod
    def generate_docx(cls, product_dict: dict) -> io.BytesIO:
        sds = product_dict.get("sds_data") or {}
        meta = sds.get("meta") or {}
        urun_adi = product_dict.get("urun_adi") or "KİMYASAL ÜRÜN"
        ticari_kod = product_dict.get("ticari_kod") or "KOD-001"
        hazirlama_tarihi = meta.get("hazirlama_tarihi") or "01.01.2026"
        revizyon_no = str(meta.get("revizyon_no") or "00")
        revizyon_tarihi = meta.get("revizyon_tarihi") or hazirlama_tarihi

        # 1. Update Header XML in memory using zipfile
        with open(TEMPLATE_PATH, "rb") as f:
            template_bytes = f.read()

        zip_in = zipfile.ZipFile(io.BytesIO(template_bytes), "r")
        zip_buffer = io.BytesIO()
        zip_out = zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED)

        for item in zip_in.infolist():
            content = zip_in.read(item.filename)
            if item.filename == "word/header2.xml":
                text = content.decode("utf-8")
                text = re.sub(r'<w:t>16\.03\.2019</w:t>', f'<w:t>{hazirlama_tarihi}</w:t>', text)
                text = re.sub(r'<w:t>01</w:t>', f'<w:t>{revizyon_no}</w:t>', text)
                text = re.sub(r'<w:t>24\.06\.2026</w:t>', f'<w:t>{revizyon_tarihi}</w:t>', text)
                content = text.encode("utf-8")
            elif item.filename == "word/header1.xml":
                text = content.decode("utf-8")
                header_title = f"{ticari_kod} {urun_adi}"
                text = re.sub(r'<w:t>G\.TN\.20\.00 GÖKAY SELÜLOZİK EXTRA TİNER</w:t>', f'<w:t>{header_title}</w:t>', text)
                content = text.encode("utf-8")

            zip_out.writestr(item, content)

        zip_in.close()
        zip_out.close()
        zip_buffer.seek(0)

        # 2. Open modified docx with python-docx to populate the 16 sections
        doc = Document(zip_buffer)

        # Clear sample body paragraphs in template
        p_elements = list(doc.element.body)
        for p in p_elements:
            if p.tag.endswith("p") or p.tag.endswith("tbl"):
                if not p.tag.endswith("sectPr"):
                    p.getparent().remove(p)

        # 3. Add 16 Sections to Document Body
        cls._add_section_1(doc, sds, product_dict)
        cls._add_section_2(doc, sds)
        cls._add_section_3(doc, sds)
        cls._add_section_4(doc, sds)
        cls._add_section_5(doc, sds)
        cls._add_section_6(doc, sds)
        cls._add_section_7(doc, sds)
        cls._add_section_8(doc, sds)
        cls._add_section_9(doc, sds)
        cls._add_section_10(doc, sds)
        cls._add_section_11(doc, sds)
        cls._add_section_12(doc, sds)
        cls._add_section_13(doc, sds)
        cls._add_section_14(doc, sds)
        cls._add_section_15(doc, sds)
        cls._add_section_16(doc, sds)

        output_stream = io.BytesIO()
        doc.save(output_stream)
        output_stream.seek(0)
        return output_stream

    # Helper: Main Section Banner (12pt Bold, underline border)
    @classmethod
    def _add_section_banner(cls, doc, title: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(title)
        run.font.name = FONT_NAME
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)
        
        pPr = p._element.get_or_add_pPr()
        pBdr = parse_xml(
            f'<w:pBdr {nsdecls("w")}>'
            f'<w:bottom w:val="single" w:sz="8" w:space="2" w:color="000000"/>'
            f'</w:pBdr>'
        )
        pPr.append(pBdr)

    # Helper: Subsection Title (11pt Bold)
    @classmethod
    def _add_subsection_title(cls, doc, title: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(7)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(title)
        run.font.name = FONT_NAME
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 0, 0)

    # Helper: Clean Key-Value Paragraph Line (10pt Normal text, label bold)
    @classmethod
    def _add_kv_line(cls, doc, label: str, val: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(1.5)
        p.paragraph_format.line_spacing = 1.15

        run_lbl = p.add_run(f"{label}: ")
        run_lbl.font.name = FONT_NAME
        run_lbl.font.size = Pt(10)
        run_lbl.font.bold = True
        run_lbl.font.color.rgb = RGBColor(0, 0, 0)

        run_val = p.add_run(str(val or "—"))
        run_val.font.name = FONT_NAME
        run_val.font.size = Pt(10)
        run_val.font.color.rgb = RGBColor(20, 20, 20)

    # Helper: Text Paragraph Line (10pt Regular)
    @classmethod
    def _add_text_line(cls, doc, text: str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1.5)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(str(text or "—"))
        run.font.name = FONT_NAME
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(20, 20, 20)

    # 1. BÖLÜM
    @classmethod
    def _add_section_1(cls, doc, sds, prod):
        cls._add_section_banner(doc, "1. MADDENİN / KARIŞIMIN VE ŞİRKETİN / DAĞITICININ KİMLİĞİ")
        b1 = sds.get("b1_kimlik") or {}
        b1_1 = b1.get("b1_1") or {}
        b1_2 = b1.get("b1_2") or {}
        b1_3 = b1.get("b1_3") or {}
        b1_4 = b1.get("b1_4") or {}

        cls._add_subsection_title(doc, "1.1. Madde / Karışım Kimliği")
        cls._add_kv_line(doc, "Madde / Karışım Adı", b1_1.get("madde_karisim_adi") or prod.get("urun_adi"))
        cls._add_kv_line(doc, "Ticari Kod / Stok Kodu", prod.get("ticari_kod"))
        cls._add_kv_line(doc, "Kayıt Numarası", b1_1.get("kayit_numarasi") or "Kayıttan muaftır / Uygulanabilir değildir.")

        cls._add_subsection_title(doc, "1.2. Madde veya Karışımın Belirlenmiş Kullanımları ve Tavsiye Edilmeyen Kullanımları")
        cls._add_kv_line(doc, "Belirlenmiş Kullanımlar", ", ".join(b1_2.get("tanimlanmis_kullanimlar") or []) or "Sanayi / Endüstriyel kullanım")
        cls._add_kv_line(doc, "Tavsiye Edilmeyen Kullanımlar", ", ".join(b1_2.get("tavsiye_edilmeyen_kullanimlar") or []) or "Tavsiye edilen kullanımların dışında kullanılmamalıdır.")

        cls._add_subsection_title(doc, "1.3. Güvenlik Bilgi Formu Tedarikçisinin Bilgileri")
        cls._add_kv_line(doc, "Tedarikçi / İmalatçı Adı", b1_3.get("tedarikci_adi") or "Aypol Kimya Sanayi ve Ticaret A.Ş.")
        cls._add_kv_line(doc, "Adres", b1_3.get("adres") or "İstanbul / Türkiye")
        cls._add_kv_line(doc, "İletişim", f"Tel: {b1_3.get('telefon') or '—'} | E-Posta: {b1_3.get('eposta') or '—'}")
        cls._add_kv_line(doc, "Yetkili Kişi (KDU)", b1_3.get("yetkili_kisi") or "—")

        cls._add_subsection_title(doc, "1.4. Acil Durum Telefon Numarası")
        cls._add_kv_line(doc, "Acil Durum Telefonu", b1_4.get("acil_telefon") or "114 (UZEM - Ulusal Zehir Danışma Merkezi)")

    # 2. BÖLÜM
    @classmethod
    def _add_section_2(cls, doc, sds):
        cls._add_section_banner(doc, "2. ZARARLILIK TANIMI")
        b2 = sds.get("b2_zarar_tanimi") or {}
        b2_1 = b2.get("b2_1") or {}
        b2_2 = b2.get("b2_2") or {}
        b2_3 = b2.get("b2_3") or {}

        cls._add_subsection_title(doc, "2.1. Maddenin veya Karışımın Sınıflandırılması")
        siniflar = b2_1.get("siniflandirmalar") or []
        if siniflar:
            for s in siniflar:
                cls._add_text_line(doc, f"• {s.get('zararlilik_sinifi', '')} ({s.get('kategori', '')}): {s.get('h_kodu', '')}")
        else:
            cls._add_text_line(doc, b2_1.get("siniflandirilmama_gerekcesi") or "SEA Yönetmeliği kriterlerine göre zararlı olarak sınıflandırılmamıştır.")

        cls._add_subsection_title(doc, "2.2. Etiket Unsurları")
        
        # Piktogramlar with embedded images
        piks = b2_2.get("piktogramlar") or []
        p_pik = doc.add_paragraph()
        p_pik.paragraph_format.space_before = Pt(2)
        p_pik.paragraph_format.space_after = Pt(3)
        p_pik.paragraph_format.line_spacing = 1.15

        run_lbl = p_pik.add_run("Piktogramlar: ")
        run_lbl.font.name = FONT_NAME
        run_lbl.font.size = Pt(10)
        run_lbl.font.bold = True
        run_lbl.font.color.rgb = RGBColor(0, 0, 0)

        if piks:
            pictograms_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "pictograms")
            for pic_code in piks:
                if not pic_code:
                    continue
                p_code = pic_code.strip()
                png_candidates = [
                    os.path.join(pictograms_dir, f"{p_code.upper()}.png"),
                    os.path.join(pictograms_dir, f"{p_code.lower()}.png"),
                    os.path.join("pictograms", "png", f"{p_code.upper()}.png"),
                    os.path.join("pictograms", "png", f"{p_code.lower()}.png"),
                ]
                found_path = next((p for p in png_candidates if os.path.exists(p)), None)
                if found_path:
                    run_img = p_pik.add_run()
                    run_img.add_picture(found_path, width=Inches(0.65), height=Inches(0.65))
                    p_pik.add_run("  ")
                else:
                    run_txt = p_pik.add_run(f"[{p_code}] ")
                    run_txt.font.name = FONT_NAME
                    run_txt.font.size = Pt(10)
        else:
            run_none = p_pik.add_run("GHS Piktogramı Bulunmamaktadır")
            run_none.font.name = FONT_NAME
            run_none.font.size = Pt(10)

        cls._add_kv_line(doc, "Uyarı Kelimesi", b2_2.get("uyari_kelimesi") or "Yok")
        cls._add_kv_line(doc, "Zararlılık İfadeleri (H)", ", ".join(b2_2.get("h_ifadeleri") or []) or "—")
        cls._add_kv_line(doc, "Önlem İfadeleri (P)", ", ".join(b2_2.get("p_ifadeleri") or []) or "—")

        cls._add_subsection_title(doc, "2.3. Diğer Zararlar")
        cls._add_text_line(doc, b2_3.get("pbt_vpvb_degerlendirme") or "PBT / vPvB kriterlerini karşılamaz.")

    # 3. BÖLÜM (3.2 TABLO YAPISINDA)
    @classmethod
    def _add_section_3(cls, doc, sds):
        cls._add_section_banner(doc, "3. BİLEŞİMİ / İÇİNDEKİLER HAKKINDA BİLGİ")
        b3 = sds.get("b3_bilesim") or {}
        tip = b3.get("tip") or "karisim"

        if tip == "madde":
            madde = b3.get("madde") or {}
            cls._add_subsection_title(doc, "3.1. Maddeler")
            cls._add_kv_line(doc, "Kimyasal Kimliği", madde.get("kimyasal_kimlik") or "—")
            cls._add_kv_line(doc, "CAS & EC No", f"CAS: {madde.get('cas_no') or '—'} | EC: {madde.get('ec_no') or '—'}")
        else:
            karisim = b3.get("karisim") or {}
            bilesenler = karisim.get("bilesenler") or []
            cls._add_subsection_title(doc, "3.2. Karışımlar")
            if bilesenler:
                tbl = doc.add_table(rows=len(bilesenler)+1, cols=6)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                headers = ["Bileşen Adı", "CAS No", "EC No", "Kayıt No", "Konsantrasyon", "Sınıflandırma"]
                for i, h in enumerate(headers):
                    cell = tbl.cell(0, i)
                    set_cell_borders(cell, color="444444", sz="4")
                    set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
                    p = cell.paragraphs[0]
                    r = p.add_run(h)
                    r.font.name = FONT_NAME
                    r.font.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                    r.font.size = Pt(10)

                for r_idx, b in enumerate(bilesenler, start=1):
                    row = tbl.rows[r_idx]
                    vals = [
                        b.get("ad", ""),
                        b.get("cas_no", ""),
                        b.get("ec_no", ""),
                        b.get("kayit_no", ""),
                        b.get("konsantrasyon", ""),
                        b.get("siniflandirma", "")
                    ]
                    for c_idx, val in enumerate(vals):
                        c = row.cells[c_idx]
                        set_cell_borders(c, color="444444", sz="4")
                        set_cell_margins(c, top=60, bottom=60, left=80, right=80)
                        p = c.paragraphs[0]
                        r_v = p.add_run(str(val or "—"))
                        r_v.font.name = FONT_NAME
                        r_v.font.size = Pt(8)

                doc.add_paragraph()
            else:
                cls._add_text_line(doc, "Zararlı sınır değerini aşan bileşen bulunmamaktadır.")

    # 4. BÖLÜM
    @classmethod
    def _add_section_4(cls, doc, sds):
        cls._add_section_banner(doc, "4. İLK YARDIM ÖNLEMLERİ")
        b4 = sds.get("b4_ilk_yardim") or {}
        b4_1 = b4.get("b4_1") or {}

        cls._add_subsection_title(doc, "4.1. İlk Yardım Önlemlerinin Açıklanması")
        cls._add_kv_line(doc, "Solunması Halinde", b4_1.get("soluma") or "Kazazedeyi temiz havaya çıkarın.")
        cls._add_kv_line(doc, "Cilt ile Teması Halinde", b4_1.get("cilt_temasi") or "Bol su ve sabun ile yıkayınız.")
        cls._add_kv_line(doc, "Göz ile Teması Halinde", b4_1.get("goz_temasi") or "Bol su ile en az 15 dakika yıkayınız.")
        cls._add_kv_line(doc, "Yutulması Halinde", b4_1.get("yutma") or "Ağzı su ile çalkalayınız. Kusturmayınız.")

        cls._add_subsection_title(doc, "4.2. Akut ve Sonradan Görülen En Önemli Belirtiler ve Etkiler")
        cls._add_text_line(doc, b4.get("b4_2_belirtiler_etkiler") or "Önemli bir belirti bildirilmemiştir.")

        cls._add_subsection_title(doc, "4.3. Tıbbi Müdahale ve Özel Tedavi Gereği İçin İlk İşaretler")
        cls._add_text_line(doc, b4.get("b4_3_acil_tibbi_mudahale") or "Semptomatik tedavi uygulayınız.")

    # 5. BÖLÜM
    @classmethod
    def _add_section_5(cls, doc, sds):
        cls._add_section_banner(doc, "5. YANGINLA MÜCADELE ÖNLEMLERİ")
        b5 = sds.get("b5_yangin_mucadele") or {}
        b5_1 = b5.get("b5_1") or {}

        cls._add_subsection_title(doc, "5.1. Yangın Söndürücüler")
        cls._add_kv_line(doc, "Uygun Yangın Söndürücüler", b5_1.get("uygun_sondurucu") or "Köpük, kuru kimyevi toz, CO2, su sisi.")
        cls._add_kv_line(doc, "Uygun Olmayan Söndürücüler", b5_1.get("uygun_olmayan_sondurucu") or "Yüksek basınçlı tam su jeti.")

        cls._add_subsection_title(doc, "5.2. Madde veya Karışımdan Kaynaklanan Özel Zararlar")
        cls._add_text_line(doc, b5.get("b5_2_ozel_zararlar") or "Yanma halinde toksik karbon oksitler açığa çıkabilir.")

        cls._add_subsection_title(doc, "5.3. Yangın Söndürme Ekipleri İçin Tavsiyeler")
        cls._add_text_line(doc, b5.get("b5_3_sondurme_ekibi_tavsiyeleri") or "Tam koruyucu teçhizat ve solunum cihazı kullanınız.")

    # 6. BÖLÜM
    @classmethod
    def _add_section_6(cls, doc, sds):
        cls._add_section_banner(doc, "6. KAZA SONUCU YAYILMAYA KARŞI ÖNLEMLER")
        b6 = sds.get("b6_kaza_sonucu_yayilma") or {}
        b6_1 = b6.get("b6_1") or {}

        cls._add_subsection_title(doc, "6.1. Kişisel Önlemler, Koruyucu Donanım ve Acil Durum Prosedürleri")
        cls._add_text_line(doc, b6_1.get("kisisel_onlemler_acil_olmayan") or "Alanı havalandırın. Ateş kaynaklarını uzaklaştırın.")

        cls._add_subsection_title(doc, "6.2. Çevresel Önlemler")
        cls._add_text_line(doc, b6.get("b6_2_cevresel_onlemler") or "Kanalizasyon ve su yollarına karışmasını önleyiniz.")

        cls._add_subsection_title(doc, "6.3. Muhafaza Etme ve Temizleme İçin Yöntemler ve Materyaller")
        cls._add_text_line(doc, b6.get("b6_3_kontrol_temizleme_yontemleri") or "İnert emici materyal (kum vb.) ile toplayınız.")

        cls._add_subsection_title(doc, "6.4. Diğer Bölümlere Atıflar")
        cls._add_text_line(doc, b6.get("b6_4_diger_bolumlere_atif") or "Kişisel korunma için Bölüm 8'e, bertaraf için Bölüm 13'e bakınız.")

    # 7. BÖLÜM
    @classmethod
    def _add_section_7(cls, doc, sds):
        cls._add_section_banner(doc, "7. ELLEÇLEME VE DEPOLAMA")
        b7 = sds.get("b7_ellecme_depolama") or {}
        b7_2 = b7.get("b7_2") or {}

        cls._add_subsection_title(doc, "7.1. Güvenli Elleçleme İçin Önlemler")
        cls._add_text_line(doc, b7.get("b7_1_guvenli_ellecleme") or "İyi havalandırılan yerlerde kullanın. Temastan kaçının.")

        cls._add_subsection_title(doc, "7.2. Uyuşmazlıkları da İçeren Güvenli Depolama Koşulları")
        cls._add_text_line(doc, b7_2.get("guvenli_depolama_kosullari") or "Serin, kuru, iyi havalandırılan yerde saklayınız.")

        cls._add_subsection_title(doc, "7.3. Belirli Son Kullanımlar")
        cls._add_text_line(doc, b7.get("b7_3_belirli_son_kullanimlar") or "Bölüm 1.2'de belirtilen alanlar içindir.")

    # 8. BÖLÜM (8.1 TABLO YAPISINDA)
    @classmethod
    def _add_section_8(cls, doc, sds):
        cls._add_section_banner(doc, "8. MARUZ KALMA KONTROLLERİ / KİŞİSEL KORUNMA")
        b8 = sds.get("b8_maruz_kalma_kontrolu") or {}
        b8_1 = b8.get("b8_1_kontrol_parametreleri") or []
        b8_2 = b8.get("b8_2") or {}
        kkd = b8_2.get("kkd") or {}

        cls._add_subsection_title(doc, "8.1. Kontrol Parametreleri")
        if b8_1:
            tbl = doc.add_table(rows=len(b8_1)+1, cols=3)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            headers = ["Madde / Bileşen", "Mesleki Maruziyet Sınır Değeri", "Yasal Dayanak"]
            for i, h in enumerate(headers):
                cell = tbl.cell(0, i)
                set_cell_borders(cell, color="444444", sz="4")
                set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
                p = cell.paragraphs[0]
                r = p.add_run(h)
                r.font.name = FONT_NAME
                r.font.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
                r.font.size = Pt(10)

            for r_idx, exp in enumerate(b8_1, start=1):
                row = tbl.rows[r_idx]
                vals = [exp.get("madde", ""), exp.get("sinir_degeri", ""), exp.get("yasal_dayanak", "")]
                for c_idx, val in enumerate(vals):
                    c = row.cells[c_idx]
                    set_cell_borders(c, color="444444", sz="4")
                    set_cell_margins(c, top=60, bottom=60, left=80, right=80)
                    p = c.paragraphs[0]
                    r_v = p.add_run(str(val or "—"))
                    r_v.font.name = FONT_NAME
                    r_v.font.size = Pt(8)

            doc.add_paragraph()
        else:
            cls._add_text_line(doc, "Tanımlı mesleki maruziyet sınır değeri bulunmamaktadır.")

        cls._add_subsection_title(doc, "8.2. Maruz Kalma Kontrolleri")
        cls._add_kv_line(doc, "Uygun Mühendislik Kontrolleri", b8_2.get("muhendislik_kontrolleri") or "Yeterli genel ve lokal havalandırma sağlayınız.")
        cls._add_kv_line(doc, "Göz / Yüz Koruması", kkd.get("goz_yuz") or "EN 166 uyumlu koruyucu gözlük.")
        cls._add_kv_line(doc, "Ellerin Korunması", kkd.get("cilt_el") or "EN 374 uyumlu nitril eldiven.")
        cls._add_kv_line(doc, "Solunum Sisteminin Korunması", kkd.get("solunum") or "Gerekli hallerde A tipi filtreli solunum maskesi.")

    # 9. BÖLÜM
    @classmethod
    def _add_section_9(cls, doc, sds):
        cls._add_section_banner(doc, "9. FİZİKSEL VE KİMYASAL ÖZELLİKLER")
        b9 = sds.get("b9_fiziksel_kimyasal_ozellikler") or {}
        b9_1 = b9.get("b9_1") or {}

        cls._add_subsection_title(doc, "9.1. Temel Fiziksel ve Kimyasal Özellikler Hakkında Bilgi")
        props = [
            ("a) Görünüm (Fiziksel hal, renk)", b9_1.get("gorunum")),
            ("b) Koku", b9_1.get("koku")),
            ("c) Koku Eşiği", b9_1.get("koku_esigi")),
            ("ç) pH", b9_1.get("ph")),
            ("d) Erime / Donma Noktası", b9_1.get("erime_noktasi")),
            ("e) İlk Kaynama Noktası ve Kaynama Aralığı", b9_1.get("kaynama_noktasi")),
            ("f) Parlama Noktası", b9_1.get("parlama_noktasi")),
            ("g) Buharlaşma Hızı", b9_1.get("buharlasma_hizi")),
            ("ğ) Alevlenirlik (Katı, Gaz)", b9_1.get("alevlenirlik")),
            ("h) Üst / Alt Alevlenirlik veya Patlayıcı Limitleri", b9_1.get("ust_alt_limitler")),
            ("ı) Buhar Basıncı", b9_1.get("buhar_basinci")),
            ("i) Buhar Yoğunluğu", b9_1.get("buhar_yogunlugu")),
            ("j) Bağıl Yoğunluk", b9_1.get("bagil_yogunluk")),
            ("k) Çözünürlük", b9_1.get("cozunurluk")),
            ("l) Dağılım Katsayısı (n-oktanol/su)", b9_1.get("dagilim_katsayisi_log_kow")),
            ("m) Kendiliğinden Tutuşma Sıcaklığı", b9_1.get("kendiliginden_tutusma_sicakligi")),
            ("n) Bozunma Sıcaklığı", b9_1.get("bozunma_sicakligi")),
            ("o) Akışkanlık (Viskozite)", b9_1.get("akiskanlik")),
            ("ö) Patlayıcı Özellikler", b9_1.get("patlayici_ozellikler")),
            ("p) Oksitleyici Özellikler", b9_1.get("oksitleyici_ozellikler"))
        ]
        for k, v in props:
            cls._add_kv_line(doc, k, v or "Belirlenmemiştir / Uygulanabilir değildir.")

        cls._add_subsection_title(doc, "9.2. Diğer Bilgiler")
        cls._add_text_line(doc, b9.get("b9_2_diger_bilgiler") or "Ek bilgi bulunmamaktadır.")

    # 10. BÖLÜM
    @classmethod
    def _add_section_10(cls, doc, sds):
        cls._add_section_banner(doc, "10. KARARLILIK VE TEPKİME")
        b10 = sds.get("b10_kararlilik_tepkime") or {}

        cls._add_subsection_title(doc, "10.1. Tepkime")
        cls._add_text_line(doc, b10.get("b10_1_tepkime") or "Normal koşullarda tehlikeli bir reaksiyon vermez.")

        cls._add_subsection_title(doc, "10.2. Kimyasal Kararlılık")
        cls._add_text_line(doc, b10.get("b10_2_kimyasal_kararlilik") or "Normal depolama ve kullanım koşullarında kararlıdır.")

        cls._add_subsection_title(doc, "10.3. Zararlı Tepkime Olasılığı")
        cls._add_text_line(doc, b10.get("b10_3_zararli_reaksiyon_olasiligi") or "Tehlikeli reaksiyon beklenmez.")

        cls._add_subsection_title(doc, "10.4. Kaçınılması Gereken Durumlar")
        cls._add_text_line(doc, b10.get("b10_4_kacinilmasi_gereken_durumlar") or "Aşırı ısı, kıvılcım, açık alev.")

        cls._add_subsection_title(doc, "10.5. Kaçınılması Gereken Maddeler")
        cls._add_text_line(doc, b10.get("b10_5_kacinilmasi_gereken_maddeler") or "Kuvvetli asitler, bazlar ve oksitleyiciler.")

        cls._add_subsection_title(doc, "10.6. Zararlı Bozunma Ürünleri")
        cls._add_text_line(doc, b10.get("b10_6_zararli_bozunma_urunleri") or "Normal depolamada ayrışmaz. Yangında toksik gazlar açığa çıkar.")

    # 11. BÖLÜM
    @classmethod
    def _add_section_11(cls, doc, sds):
        cls._add_section_banner(doc, "11. TOKSİKOLOJİK BİLGİLER")
        b11 = sds.get("b11_toksikolojik") or {}
        b11_1 = b11.get("b11_1") or {}

        cls._add_subsection_title(doc, "11.1. Toksik Etkiler Hakkında Bilgi")
        cls._add_kv_line(doc, "a) Akut Toksisite", b11_1.get("akut_toksisite") or "Kriterleri karşılamamaktadır.")
        cls._add_kv_line(doc, "b) Cilt Aşınması / Tahrişi", b11_1.get("cilt_asinmasi_tahrisi") or "Mevcut bilgilere göre sınıflandırılmaz.")
        cls._add_kv_line(doc, "c) Ciddi Göz Hasarları / Tahrişi", b11_1.get("goz_hasari") or "Mevcut bilgilere göre sınıflandırılmaz.")
        cls._add_kv_line(doc, "ç) Solunum Yolları veya Cilt Hassaslaşması", b11_1.get("solunum_cilt_hassasiyeti") or "Hassaslaştırıcı etkisi bildirilmemiştir.")
        cls._add_kv_line(doc, "d) Eşey Hücre Mutajenitesi", b11_1.get("mutajenite") or "Mutajenik olarak sınıflandırılmaz.")
        cls._add_kv_line(doc, "e) Kanserojenite", b11_1.get("kanserojenite") or "Kanserojen madde içermez.")
        cls._add_kv_line(doc, "f) Üreme Toksisitesi", b11_1.get("ureme_toksisitesi") or "Üreme için toksik değildir.")
        cls._add_kv_line(doc, "g) Belirli Hedef Organ Toksisitesi (BHOT) - Tek Maruz Kalma", b11_1.get("bhot_tek_maruz") or "Kriterleri karşılamaz.")
        cls._add_kv_line(doc, "ğ) Belirli Hedef Organ Toksisitesi (BHOT) - Tekrarlı Maruz Kalma", b11_1.get("bhot_tekrarli") or "Organ hasarı beklenmez.")
        cls._add_kv_line(doc, "h) Aspirasyon Zararı", b11_1.get("aspirasyon_zarari") or "Aspirasyon tehlikesi oluşturmaz.")

    # 12. BÖLÜM
    @classmethod
    def _add_section_12(cls, doc, sds):
        cls._add_section_banner(doc, "12. EKOLOJİK BİLGİLER")
        b12 = sds.get("b12_ekolojik") or {}

        cls._add_subsection_title(doc, "12.1. Toksisite")
        cls._add_text_line(doc, b12.get("b12_1_toksisite") or "Sucul organizmalar için zararlı olarak sınıflandırılmamıştır.")

        cls._add_subsection_title(doc, "12.2. Kalıcılık ve Bozunabilirlik")
        cls._add_text_line(doc, b12.get("b12_2_kalicilik_bozunabilirlik") or "Bileşenleri biyolojik olarak ayrışabilir.")

        cls._add_subsection_title(doc, "12.3. Biyobirikim Potansiyeli")
        cls._add_text_line(doc, b12.get("b12_3_biyobirikim") or "Biyobirikim potansiyeli düşüktür.")

        cls._add_subsection_title(doc, "12.4. Toprakta Hareketlilik")
        cls._add_text_line(doc, b12.get("b12_4_topraktaki_hareketlilik") or "Topraktaki hareketliliği çözünürlüğe bağlıdır.")

        cls._add_subsection_title(doc, "12.5. PBT ve vPvB Değerlendirmesinin Sonuçları")
        cls._add_text_line(doc, b12.get("b12_5_pbt_vpvb_sonuclari") or "PBT / vPvB kriterlerini karşılamaz.")

        cls._add_subsection_title(doc, "12.6. Diğer Olumsuz Etkiler")
        cls._add_text_line(doc, b12.get("b12_6_diger_olumsuz_etkiler") or "Bilinen başka bir olumsuz etkisi yoktur.")

    # 13. BÖLÜM
    @classmethod
    def _add_section_13(cls, doc, sds):
        cls._add_section_banner(doc, "13. BERTARAF ETME BİLGİLERİ")
        b13 = sds.get("b13_bertaraf") or {}

        cls._add_subsection_title(doc, "13.1. Atık İşleme Yöntemleri")
        cls._add_kv_line(doc, "Atık İşleme", b13.get("b13_1_atik_isleme_yontemleri") or "Ulusal mevzuata uygun olarak lisanslı atık bertaraf tesislerine verilmelidir.")
        cls._add_kv_line(doc, "Ambalaj Atıkları", b13.get("b13_1_ambalaj_atik_isleme") or "Boş ambalajlar lisanslı geri kazanım/bertaraf firmalarına teslim edilmelidir.")
        cls._add_kv_line(doc, "Kanalizasyon Uyarısı", b13.get("b13_1_kanalizasyon_uyarisi") or "Kanalizasyona ve su kaynaklarına dökülmemelidir.")

    # 14. BÖLÜM
    @classmethod
    def _add_section_14(cls, doc, sds):
        cls._add_section_banner(doc, "14. TAŞIMACILIK BİLGİSİ")
        b14 = sds.get("b14_tasimacilik") or {}

        cls._add_subsection_title(doc, "14.1. UN Numarası")
        cls._add_text_line(doc, b14.get("b14_1_un_numarasi") or "Taşımacılıkta tehlikeli madde değildir.")

        cls._add_subsection_title(doc, "14.2. Uygun UN Taşımacılık Adı")
        cls._add_text_line(doc, b14.get("b14_2_un_tasimacilik_adi") or "Uygulanabilir değildir.")

        cls._add_subsection_title(doc, "14.3. Taşımacılık Zararlılık Sınıf(lar)ı")
        cls._add_text_line(doc, b14.get("b14_3_tasimacilik_sinifi") or "—")

        cls._add_subsection_title(doc, "14.4. Ambalajlama Grubu")
        cls._add_text_line(doc, b14.get("b14_4_ambalajlama_grubu") or "—")

        cls._add_subsection_title(doc, "14.5. Çevresel Zararlar")
        cls._add_text_line(doc, b14.get("b14_5_cevresel_zararlar") or "Deniz Kirletici değildir.")

        cls._add_subsection_title(doc, "14.6. Kullanıcı İçin Özel Önlemler")
        cls._add_text_line(doc, b14.get("b14_6_kullanici_ozel_onlemler") or "Taşımada devrilme ve hasara karşı emniyete alınız.")

        cls._add_subsection_title(doc, "14.7. MARPOL 73/78 Ek II ve IBC Koduna Göre Dökme Taşımacılık")
        cls._add_text_line(doc, b14.get("b14_7_marpol_ibc") or "Uygulanabilir değildir (Ambalajlı sevkiyat).")

    # 15. BÖLÜM
    @classmethod
    def _add_section_15(cls, doc, sds):
        cls._add_section_banner(doc, "15. MEVZUAT BİLGİSİ")
        b15 = sds.get("b15_mevzuat") or {}

        cls._add_subsection_title(doc, "15.1. Madde veya Karışıma Özel Güvenlik, Sağlık ve Çevre Mevzuatı")
        cls._add_text_line(doc, b15.get("b15_1_ozel_mevzuat_hukumleri") or "KKDİK Yönetmeliği (RG: 30105), SEA Yönetmeliği (RG: 28848).")

        cls._add_subsection_title(doc, "15.2. Kimyasal Güvenlik Değerlendirmesi")
        cls._add_text_line(doc, b15.get("b15_2_kimyasal_guvenlik_degerlendirmesi") or "Bu karışım için Kimyasal Güvenlik Değerlendirmesi (KGD) yapılmamıştır.")

    # 16. BÖLÜM
    @classmethod
    def _add_section_16(cls, doc, sds):
        cls._add_section_banner(doc, "16. DİĞER BİLGİLER")
        b16 = sds.get("b16_diger_bilgiler") or {}
        tam_h = b16.get("tam_h_ifadeleri") or []

        cls._add_subsection_title(doc, "16.1. Değişiklikler ve Revizyon Bilgisi")
        cls._add_text_line(doc, b16.get("revizyon_aciklamasi") or "İlk versiyon (KKDİK Ek-2 uyumlu).")

        cls._add_subsection_title(doc, "16.2. Kısaltmalar ve Akronimler")
        cls._add_text_line(doc, b16.get("kisaltmalar_anahtari") or "ADR: Karayolu Taşımacılığı; CAS: Chemical Abstracts Service; TWA: Zaman Ağırlıklı Ortalama; STEL: Kısa Süreli Maruziyet Sınırı.")

        cls._add_subsection_title(doc, "16.3. Önemli Literatür Referansları ve Bilgi Kaynakları")
        cls._add_text_line(doc, b16.get("literatur_referanslari") or "ECHA Veritabanı, T.C. Çevre, Şehircilik ve İklim Değişikliği Bakanlığı Mevzuatı.")

        cls._add_subsection_title(doc, "16.4. Zararlılık (H) İfadelerinin Tam Metinleri")
        if tam_h:
            for h in tam_h:
                cls._add_text_line(doc, f"• {h}")
        else:
            cls._add_text_line(doc, "H-ifadesi bulunmamaktadır.")

        cls._add_subsection_title(doc, "16.5. Eğitim Tavsiyeleri")
        cls._add_text_line(doc, b16.get("egitim_tavsiyeleri") or "Çalışanlar kimyasalların güvenli elleçlenmesi ve KKD kullanımı konusunda eğitilmelidir.")
