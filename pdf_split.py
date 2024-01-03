from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
import re

def extract_text_from_pdf(filename, page_numbers=None, min_line_length=32):
    paragraphs = []
    resplit_paragraphs = []
    buffer = ''
    full_text = ''
    for i, page_layout in enumerate(extract_pages(filename)):
        if page_numbers is not None and i not in page_numbers:
            continue
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                full_text += element.get_text()
    lines = full_text.split('\n')
    for text in lines:
        buffer += text if not text.endswith('-') else text.strip('-')
        if len(text) <= min_line_length and buffer:
            if buffer:
                if len(buffer) > 50:
                    resplit_paragraphs.append(buffer)
                else:
                    paragraphs.append(buffer)
            buffer = ''


    for paragraph in resplit_paragraphs:
        sentences = re.split('(?<=[。！？])', paragraph)
        temp_paragraph = ''
        for sentence in sentences:
            temp_paragraph += sentence
            if len(temp_paragraph) >= 50:
                paragraphs.append(temp_paragraph)
                temp_paragraph = ''

        if temp_paragraph:
            paragraphs.append(temp_paragraph)

    return paragraphs
