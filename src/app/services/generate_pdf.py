"""Service to generate PDF from JSON data."""
import io
from pathlib import Path
from fpdf import FPDF
from src.app.core.log_config import setup_logging

logger = setup_logging("JSON TO PDF")

def create_pdf_from_json(towing_document):
    """
    Creates a PDF report from the provided JSON data.
    
    Args:
        soap_notes_json (list): List of dictionaries containing SOAP notes data.

    Returns:
        io.BytesIO: A byte stream containing the generated PDF.
    """
    if not towing_document:
        logger.warning("[CREATE_PDF_FROM_JSON] No data to create PDF.")
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    project_root = Path(__file__).resolve().parents[3]
    image_path = project_root / "src/app/services/CCCIS_Logo.png"
    
    pdf.image(str(image_path), x=5, y=5, w=12, h=12)

    pdf.set_font("Arial", 'B', 19)
    pdf.set_xy(18, 9)
    pdf.cell(0, 0, "First Responder Intelligent Agent", align='L')
    pdf.set_font("Arial", 'I', size=10)
    pdf.set_xy(18, 11)
    pdf.cell(0, 5, "An AI-powered solution for first responders", align='L')

    insert_line(pdf, y_position=20)

    pdf.set_font("Arial", 'BU', 12)
    pdf.set_xy(4, 30)
    pdf.cell(0, 0, "User Details", align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(4, 35)
    pdf.cell(0, 10, "Name: ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(15, 35)
    pdf.cell(0, 10, towing_document["user_details"]["name"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(4, 45)
    pdf.cell(0, 10, "Contact number: ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(30, 45)
    pdf.cell(0, 10, towing_document["user_details"]["contact_number"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(110, 35)
    pdf.cell(0, 10, "Gender: ", ln=0)
    set_sub_heading_format(pdf)
    pdf.set_xy(125, 35)
    pdf.cell(0, 10, towing_document["user_details"]["gender"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(110, 45)
    pdf.cell(0, 10, "Email: ", ln=0)
    set_sub_heading_format(pdf)
    pdf.set_xy(125, 45)
    pdf.cell(0, 10, towing_document["user_details"]["email"], align='L', ln=1)

    insert_line(pdf)
    pdf.set_font("Arial", 'BU', 12)
    pdf.set_xy(4, 60)
    pdf.cell(0, 0, "Vehicle Information", align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(4, 70)
    pdf.cell(0, 10, "Vehicle Model: ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(35, 70)
    pdf.cell(0, 10, towing_document["vehicle_info"]["vehicle_model"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(110, 70)
    pdf.cell(0, 10, "Vehicle Year: ", ln=0)
    set_sub_heading_format(pdf)
    pdf.set_xy(135, 70)
    pdf.cell(0, 10, towing_document["vehicle_info"]["vehicle_year"], align='L', ln=1)

    insert_line(pdf)
    pdf.set_font("Arial", 'BU', 12)
    pdf.set_xy(4, 90)
    pdf.cell(0, 0, "Issues", align='L', ln=1) 

    set_heading_format(pdf)
    pdf.set_xy(4, 95)
    pdf.cell(0, 10, "Incident Description: ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(45, 95)
    pdf.multi_cell(0, 10, towing_document["incident"], align='L')

    set_heading_format(pdf)
    pdf.set_xy(4, 105)
    pdf.cell(0, 10, "Is the vehicle operable? ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(45, 105)
    pdf.cell(0, 10, towing_document["operability"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(4, 115)
    pdf.cell(0, 10, "Vehicle Condition: ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(45, 115)
    pdf.cell(0, 10, towing_document["vehicle_condition"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(4, 125)
    pdf.cell(0, 10, "Battery Status: ", align='L', ln=1)
    set_sub_heading_format(pdf)
    pdf.set_xy(45, 125)
    pdf.cell(0, 10, towing_document["battery_condition"], align='L', ln=1)

    set_heading_format(pdf)
    pdf.set_xy(4, 135)
    pdf.cell(0, 10, "Address: ", align='L', ln=1) 
    set_sub_heading_format(pdf)
    pdf.set_xy(45, 135)
    pdf.cell(0, 10, towing_document["address"], align='L', ln=1)

    pdf_Bffer = io.BytesIO()
    pdf_bytes = pdf.output()
    pdf_Bffer.write(pdf_bytes)
    pdf_Bffer.seek(0)
    logger.info("[CREATE_PDF_FROM_JSON] PDF created successfully.")
    return pdf_Bffer

def set_heading_format(pdf):
    """Set heading format for PDF."""
    pdf.set_font("Arial", 'B', 9)

def set_sub_heading_format(pdf):
    """Set sub-heading format for PDF."""
    pdf.set_font()

def insert_line(pdf, y_position=None):
    """Insert a horizontal line in the PDF at the current position or specified y_position."""
    if y_position:
        pdf.set_y(y_position)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.2)
    pdf.line(4, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
