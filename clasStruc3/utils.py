from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, color):
    """Sets a table-cell background color in a python-docx table."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), color)
    tcPr.append(shd)
