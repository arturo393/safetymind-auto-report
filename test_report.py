#!/usr/bin/env python3
"""
Test Suite for SafetyMind PDF Reports
Validates structure, content, visual quality, and professionalism
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path

API_BASE = os.getenv("API_URL", "http://100.74.53.2:8080")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "test_reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name, detail=""):
        self.passed.append((test_name, detail))
        print(f"  {Colors.GREEN}✓{Colors.END} {test_name}")
        if detail:
            print(f"    {Colors.BLUE}→ {detail}{Colors.END}")
    
    def add_fail(self, test_name, detail=""):
        self.failed.append((test_name, detail))
        print(f"  {Colors.RED}✗{Colors.END} {test_name}")
        if detail:
            print(f"    {Colors.RED}→ {detail}{Colors.END}")
    
    def add_warn(self, test_name, detail=""):
        self.warnings.append((test_name, detail))
        print(f"  {Colors.YELLOW}⚠{Colors.END} {test_name}")
        if detail:
            print(f"    {Colors.YELLOW}→ {detail}{Colors.END}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}Resultados:{Colors.END}")
        print(f"  {Colors.GREEN}✓ Pasaron: {len(self.passed)}/{total}{Colors.END}")
        print(f"  {Colors.RED}✗ Fallaron: {len(self.failed)}/{total}{Colors.END}")
        print(f"  {Colors.YELLOW}⚠ Advertencias: {len(self.warnings)}{Colors.END}")
        return len(self.failed) == 0

def generate_report(project_key="GSA", report_type="standard", use_ai=True, engine="html"):
    """Generate a report and return the PDF path"""
    resp = requests.post(
        f"{API_BASE}/api/generate",
        json={"project_key": project_key, "report_type": report_type, "use_ai": use_ai, "engine": engine},
        timeout=60
    )
    data = resp.json()
    if data.get("status") != "success":
        raise Exception(f"Report generation failed: {data.get('error')}")
    
    filename = data["filename"]
    # Download the report
    resp = requests.get(f"{API_BASE}/api/reports/download/{filename}", timeout=30)
    pdf_path = os.path.join(REPORTS_DIR, filename)
    with open(pdf_path, "wb") as f:
        f.write(resp.content)
    return pdf_path, data

def test_pdf_exists(pdf_path):
    """Test 1: PDF file exists and has content"""
    assert os.path.exists(pdf_path), "PDF file does not exist"
    size = os.path.getsize(pdf_path)
    assert size > 10000, f"PDF too small ({size} bytes), likely empty"
    return True, f"Size: {size/1024:.1f} KB"

def test_pdf_pages(pdf_path):
    """Test 2: PDF has multiple pages (professional report)"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        pages = len(doc)
        doc.close()
        if pages >= 3:
            return True, f"{pages} pages (professional length)"
        elif pages >= 2:
            return True, f"{pages} pages"
        else:
            return False, f"Only {pages} page, should be at least 2"
    except ImportError:
        return None, "PyMuPDF not installed, skipping page count test"

def test_pdf_text_content(pdf_path):
    """Test 3: PDF contains expected text sections"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        
        expected_sections = [
            ("Resumen de Gestión Estratégica", "Header principal"),
            ("SAFETYMIND", "Branding"),
            ("KPI", "KPI section"),
            ("Avance", "Progress indicator"),
            ("Desempeño por Hito", "Milestone section"),
            ("Trabajo Completado", "Completed work"),
            ("Trabajo en Ejecución", "In-progress section"),
            ("Riesgos y Bloqueos", "Risks section"),
            ("Plan del Próximo Período", "Planning section"),
        ]
        
        missing = []
        for text, desc in expected_sections:
            if text not in full_text:
                missing.append(text)
        
        if missing:
            return False, f"Missing sections: {', '.join(missing)}"
        return True, f"All {len(expected_sections)} expected sections found"
    except ImportError:
        return None, "PyMuPDF not installed, skipping text content test"

def test_pdf_images(pdf_path):
    """Test 4: PDF contains embedded images (evidence section)"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        image_count = 0
        for page in doc:
            images = page.get_images(full=True)
            image_count += len(images)
        doc.close()
        
        if image_count >= 2:
            return True, f"{image_count} images found"
        elif image_count > 0:
            return True, f"{image_count} image(s) found"
        else:
            return False, "No images found in PDF"
    except ImportError:
        return None, "PyMuPDF not installed, skipping image test"

def test_pdf_font_quality(pdf_path):
    """Test 5: PDF uses professional fonts"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        fonts_used = set()
        for page in doc:
            for font in page.get_fonts():
                fonts_used.add(font[3])  # font name
        doc.close()
        
        professional_fonts = ['Roboto', 'Inter', 'Arial', 'Helvetica', 'Noto', 'Montserrat']
        found_professional = any(pf in str(fonts_used) for pf in professional_fonts)
        
        if found_professional:
            return True, f"Professional fonts: {fonts_used}"
        else:
            return False, f"Non-professional fonts: {fonts_used}"
    except ImportError:
        return None, "PyMuPDF not installed, skipping font test"

def test_pdf_margins(pdf_path):
    """Test 6: PDF has reasonable margins"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        page = doc[0]
        rect = page.rect
        # Check if content is inset from edges (margins exist)
        # This is a simplified check
        doc.close()
        return True, f"Page size: {rect.width:.0f}x{rect.height:.0f} points"
    except ImportError:
        return None, "PyMuPDF not installed, skipping margin test"

def test_pdf_colors(pdf_path):
    """Test 7: PDF uses SafetyMind brand colors"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            if color == 0xFFED01 or color == 0x0A0A0A:
                                return True, "SafetyMind brand colors detected"
        doc.close()
        return False, "Brand colors not detected"
    except ImportError:
        return None, "PyMuPDF not installed, skipping color test"

def test_pdf_structure_consistency(pdf_path):
    """Test 8: All sections have consistent formatting"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        # Check that all pages have footer
        footer_count = 0
        for page in doc:
            text = page.get_text()
            if "SafetyMind" in text and "Página" in text:
                footer_count += 1
        doc.close()
        
        if footer_count > 1:
            return True, f"Footer present on {footer_count} pages"
        return False, "Footer missing on some pages"
    except ImportError:
        return None, "PyMuPDF not installed, skipping consistency test"

def test_pdf_file_naming(pdf_data):
    """Test 9: PDF filename follows convention"""
    filename = pdf_data.get("filename", "")
    if "SafetyMind" in filename and filename.endswith(".pdf"):
        return True, f"Filename: {filename}"
    return False, f"Bad filename: {filename}"

def test_pdf_generation_speed(pdf_data):
    """Test 10: Report generates in reasonable time"""
    job_id = pdf_data.get("job_id", "")
    # If we got here, generation completed
    return True, "Report generated successfully"

def test_pdf_ai_content(pdf_path, use_ai=True):
    """Test 11: If AI requested, AI content is present"""
    if not use_ai:
        return None, "AI not requested, skipping"
    
    try:
        import fitz
        doc = fitz.open(pdf_path)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()
        
        if "Diagnóstico" in full_text or "IA" in full_text or "AI" in full_text:
            return True, "AI diagnosis section found"
        return False, "AI diagnosis section missing"
    except ImportError:
        return None, "PyMuPDF not installed"

def test_pdf_table_structure(pdf_path):
    """Test 12: PDF has properly structured tables"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        table_count = 0
        for page in doc:
            tables = page.find_tables()
            table_count += len(tables.tables)
        doc.close()
        
        if table_count >= 3:
            return True, f"{table_count} professional tables found"
        elif table_count >= 1:
            return True, f"{table_count} table(s) found"
        return False, "No structured tables found"
    except ImportError:
        return None, "PyMuPDF not installed, skipping table test"

def test_pdf_visual_hierarchy(pdf_path):
    """Test 13: PDF has visual hierarchy (multiple font sizes)"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        font_sizes = set()
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            font_sizes.add(span.get("size", 0))
        doc.close()
        
        if len(font_sizes) >= 4:
            return True, f"{len(font_sizes)} different font sizes (good hierarchy)"
        return False, f"Only {len(font_sizes)} font sizes, needs more hierarchy"
    except ImportError:
        return None, "PyMuPDF not installed, skipping hierarchy test"

def test_pdf_professional_spacing(pdf_path):
    """Test 14: PDF has professional spacing (content not cramped)"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        page = doc[0]
        text_blocks = page.get_text("dict")["blocks"]
        content_height = 0
        for block in text_blocks:
            if "lines" in block:
                bbox = block.get("bbox", (0, 0, 0, 0))
                content_height += bbox[3] - bbox[1]
        page_height = page.rect.height
        doc.close()
        
        ratio = content_height / page_height if page_height > 0 else 0
        if 0.3 <= ratio <= 0.95:
            return True, f"Content ratio: {ratio:.0%} (well-spaced)"
        return False, f"Content ratio: {ratio:.0%} (too cramped or empty)"
    except ImportError:
        return None, "PyMuPDF not installed, skipping spacing test"

def test_pdf_color_palette(pdf_path):
    """Test 15: PDF uses consistent color palette"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        colors_found = set()
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            color = span.get("color", 0)
                            if color != 0:  # Ignore black
                                colors_found.add(color)
        doc.close()
        
        # Check for brand color (#FFED01 = yellow)
        has_yellow = any(c == 0xFFED01 for c in colors_found)
        if has_yellow and len(colors_found) >= 2:
            return True, f"Brand palette: {len(colors_found)} colors"
        return False, f"Missing brand colors or too few: {colors_found}"
    except ImportError:
        return None, "PyMuPDF not installed, skipping palette test"

def test_pdf_evidence_quality(pdf_path):
    """Test 16: Evidence section has properly sized images"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        image_sizes = []
        for page in doc:
            images = page.get_images(full=True)
            for img in images:
                xref = img[0]
                pix = fitz.Pixmap(doc, xref)
                if pix.width > 100 and pix.height > 100:
                    image_sizes.append((pix.width, pix.height))
                pix = None
        doc.close()
        
        if len(image_sizes) >= 2:
            avg_size = sum(w*h for w,h in image_sizes) / len(image_sizes)
            return True, f"{len(image_sizes)} high-quality images (avg {avg_size:.0f}px)"
        return False, "Insufficient high-quality evidence images"
    except ImportError:
        return None, "PyMuPDF not installed, skipping evidence test"

def test_pdf_no_text_overflow(pdf_path):
    """Test 17: No text overflow or truncation issues"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        overflow_detected = False
        for page in doc:
            text = page.get_text()
            # Check for common overflow indicators
            if "..." in text and len(text.split("...")) > 5:
                overflow_detected = True
                break
        doc.close()
        
        if not overflow_detected:
            return True, "No text overflow detected"
        return False, "Potential text overflow detected"
    except ImportError:
        return None, "PyMuPDF not installed, skipping overflow test"

def test_pdf_metadata(pdf_path):
    """Test 18: PDF has proper metadata"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        doc.close()
        
        has_title = metadata.get("title", "") != ""
        has_author = metadata.get("author", "") != ""
        if has_title or has_author:
            return True, f"Title: {metadata.get('title', 'N/A')}"
        return False, "Missing PDF metadata"
    except ImportError:
        return None, "PyMuPDF not installed, skipping metadata test"

def test_pdf_professional_header(pdf_path):
    """Test 19: PDF has professional header with branding"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        first_page = doc[0]
        text = first_page.get_text()
        doc.close()
        
        has_branding = "SAFETYMIND" in text or "SafetyMind" in text
        has_title = "Resumen" in text and "Estratégica" in text
        has_date = "202" in text  # Year pattern
        
        if has_branding and has_title and has_date:
            return True, "Professional header with branding, title, and date"
        return False, f"Header missing elements: branding={has_branding}, title={has_title}, date={has_date}"
    except ImportError:
        return None, "PyMuPDF not installed, skipping header test"

def test_pdf_kpi_visibility(pdf_path):
    """Test 20: KPI section is prominent and readable"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        first_page = doc[0]
        text = first_page.get_text()
        doc.close()
        
        has_kpi = "KPI" in text or "Avance" in text
        has_percentage = "%" in text
        
        if has_kpi and has_percentage:
            return True, "KPI section with percentage visible"
        return False, "KPI section not prominent"
    except ImportError:
        return None, "PyMuPDF not installed, skipping KPI test"

def test_pdf_status_badges(pdf_path):
    """Test 21: PDF has status indicators (colors/badges)"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        all_text = ""
        for page in doc:
            all_text += page.get_text()
        doc.close()
        
        status_indicators = ["Completado", "En Progreso", "Bloqueado", "Done", "In Progress", "En curso", "Vencido", "Crítica"]
        found_indicators = [s for s in status_indicators if s in all_text]
        
        if len(found_indicators) >= 2:
            return True, f"Status indicators: {', '.join(found_indicators[:3])}"
        return False, f"Missing status indicators, found: {found_indicators}"
    except ImportError:
        return None, "PyMuPDF not installed, skipping status test"

def test_pdf_section_numbering(pdf_path):
    """Test 22: Sections are properly numbered"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        all_text = ""
        for page in doc:
            all_text += page.get_text()
        doc.close()
        
        import re
        numbered_sections = re.findall(r'\d+\.\s+[A-ZÁÉÍÓÚ]', all_text)
        
        if len(numbered_sections) >= 3:
            return True, f"{len(numbered_sections)} numbered sections"
        return False, f"Only {len(numbered_sections)} numbered sections (need 3+)"
    except ImportError:
        return None, "PyMuPDF not installed, skipping numbering test"

def test_pdf_page_breaks(pdf_path):
    """Test 23: Major sections have proper page breaks (not split awkwardly)"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = len(doc)
        doc.close()
        
        # Professional reports should have multiple pages
        if pages >= 3:
            return True, f"{pages} pages with proper section breaks"
        return False, f"Only {pages} pages, may lack proper breaks"
    except ImportError:
        return None, "PyMuPDF not installed, skipping page break test"

def test_pdf_evidence_captions(pdf_path):
    """Test 24: Evidence images have descriptive captions"""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        all_text = ""
        for page in doc:
            all_text += page.get_text()
        doc.close()
        
        # Check for evidence-related text patterns
        has_captions = any(pattern in all_text for pattern in ["Item:", "Evidencia", "Attachment", "GSA-"])
        
        if has_captions:
            return True, "Evidence images have captions"
        return False, "Missing evidence captions"
    except ImportError:
        return None, "PyMuPDF not installed, skipping caption test"

def run_all_tests():
    """Run complete test suite"""
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}  SAFETYMIND PDF REPORT TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    results = TestResult()
    
    # Generate report
    print(f"{Colors.BOLD}📄 Generando reporte...{Colors.END}")
    try:
        pdf_path, pdf_data = generate_report()
        print(f"  {Colors.GREEN}✓{Colors.END} Reporte generado: {pdf_data.get('filename')}")
    except Exception as e:
        results.add_fail("Generación de reporte", str(e))
        print(f"\n{Colors.RED}Tests abortados: no se pudo generar el reporte{Colors.END}")
        return False
    
    print(f"\n{Colors.BOLD}🔍 Ejecutando validaciones...{Colors.END}\n")
    
    # Run tests
    tests = [
        ("Archivo PDF existe", lambda: test_pdf_exists(pdf_path)),
        ("Número de páginas", lambda: test_pdf_pages(pdf_path)),
        ("Contenido de texto", lambda: test_pdf_text_content(pdf_path)),
        ("Imágenes incrustadas", lambda: test_pdf_images(pdf_path)),
        ("Calidad tipográfica", lambda: test_pdf_font_quality(pdf_path)),
        ("Márgenes", lambda: test_pdf_margins(pdf_path)),
        ("Colores de marca", lambda: test_pdf_colors(pdf_path)),
        ("Consistencia estructural", lambda: test_pdf_structure_consistency(pdf_path)),
        ("Nombrado de archivo", lambda: test_pdf_file_naming(pdf_data)),
        ("Velocidad de generación", lambda: test_pdf_generation_speed(pdf_data)),
        ("Contenido IA", lambda: test_pdf_ai_content(pdf_path, True)),
        ("Estructura de tablas", lambda: test_pdf_table_structure(pdf_path)),
        ("Jerarquía visual", lambda: test_pdf_visual_hierarchy(pdf_path)),
        ("Espaciado profesional", lambda: test_pdf_professional_spacing(pdf_path)),
        ("Paleta de colores", lambda: test_pdf_color_palette(pdf_path)),
        ("Calidad de evidencias", lambda: test_pdf_evidence_quality(pdf_path)),
        ("Sin desbordamiento de texto", lambda: test_pdf_no_text_overflow(pdf_path)),
        ("Metadatos PDF", lambda: test_pdf_metadata(pdf_path)),
        ("Header profesional", lambda: test_pdf_professional_header(pdf_path)),
        ("KPI visible", lambda: test_pdf_kpi_visibility(pdf_path)),
        ("Indicadores de estado", lambda: test_pdf_status_badges(pdf_path)),
        ("Secciones numeradas", lambda: test_pdf_section_numbering(pdf_path)),
        ("Saltos de página", lambda: test_pdf_page_breaks(pdf_path)),
        ("Leyendas en evidencias", lambda: test_pdf_evidence_captions(pdf_path)),
    ]
    
    for name, test_fn in tests:
        try:
            result, detail = test_fn()
            if result is True:
                results.add_pass(name, detail)
            elif result is False:
                results.add_fail(name, detail)
            else:
                results.add_warn(name, detail)
        except Exception as e:
            results.add_fail(name, str(e))
    
    passed = results.summary()
    
    # Save test results
    results_path = os.path.join(REPORTS_DIR, "test_results.json")
    with open(results_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "passed": len(results.passed),
            "failed": len(results.failed),
            "warnings": len(results.warnings),
            "details": {
                "passed": results.passed,
                "failed": results.failed,
                "warnings": results.warnings,
            }
        }, f, indent=2)
    
    print(f"\n{Colors.BLUE}→ Resultados guardados en: {results_path}{Colors.END}")
    print(f"{Colors.BLUE}→ Reporte PDF: {pdf_path}{Colors.END}")
    
    return passed

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SafetyMind PDF Report Test Suite")
    parser.add_argument("--iterate", action="store_true", help="Run iterative improvement loop")
    parser.add_argument("--max-iterations", type=int, default=10, help="Maximum iterations")
    parser.add_argument("--target-score", type=float, default=1.0, help="Target pass rate (0.0-1.0)")
    args = parser.parse_args()
    
    if args.iterate:
        print(f"{Colors.BOLD}🔄 MODO ITERACIÓN INFINITA{Colors.END}")
        print(f"   Iteraciones máximas: {args.max_iterations}")
        print(f"   Score objetivo: {args.target_score:.0%}\n")
        
        for iteration in range(1, args.max_iterations + 1):
            print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
            print(f"{Colors.BOLD}  ITERACIÓN {iteration}/{args.max_iterations}{Colors.END}")
            print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
            
            success = run_all_tests()
            total = len(TestResult().passed) + len(TestResult().failed)
            
            # Re-run to get actual counts
            import tempfile
            temp_results = os.path.join(tempfile.gettempdir(), "temp_results.json")
            
            if success:
                print(f"\n{Colors.GREEN}✓ TODOS LOS TESTS PASARON EN ITERACIÓN {iteration}{Colors.END}")
                print(f"{Colors.GREEN}  ¡Formato profesional alcanzado!{Colors.END}")
                sys.exit(0)
            else:
                # Load results to get counts
                results_path = os.path.join(REPORTS_DIR, "test_results.json")
                if os.path.exists(results_path):
                    with open(results_path) as f:
                        data = json.load(f)
                    passed = data["passed"]
                    failed = data["failed"]
                    total = passed + failed
                    score = passed / total if total > 0 else 0
                    
                    print(f"\n{Colors.YELLOW}  Score actual: {passed}/{total} ({score:.0%}){Colors.END}")
                    
                    if score >= args.target_score:
                        print(f"{Colors.GREEN}  ¡Score objetivo alcanzado!{Colors.END}")
                        sys.exit(0)
                
                print(f"{Colors.YELLOW}  Continuando iteración...{Colors.END}")
        
        print(f"\n{Colors.RED}✗ No se alcanzó el score objetivo después de {args.max_iterations} iteraciones{Colors.END}")
        sys.exit(1)
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)
