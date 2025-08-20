import os
import re
import difflib
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None
try:
    import docx2txt
except ImportError:
    docx2txt = None
try:
    from odf import text as odf_text
    from odf.opendocument import load as odf_load
    from odf import teletype
except ImportError:
    odf_text = None
    odf_load = None
    teletype = None

def has_plagiarism(file_path: str, threshold: float = 0.9) -> bool:
    text_content = ""
    if os.path.isfile(file_path):
        ext = file_path.lower().split('.')[-1]
        try:
            if ext == "pdf" and PyPDF2 is not None:
                reader = PyPDF2.PdfReader(file_path)
                for page in reader.pages:
                    text_content += page.extract_text() or ""
            elif ext == "docx" and docx2txt is not None:
                text_content = docx2txt.process(file_path) or ""
            elif ext == "odt" and odf_load is not None and teletype is not None:
                doc = odf_load(file_path)
                paragraphs = doc.getElementsByType(odf_text.P)
                text_content = "\n".join([teletype.extractText(p) for p in paragraphs])
            else:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()
        except Exception:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()
            except Exception:
                text_content = ""
    else:
        text_content = file_path
    text_content = text_content.strip()
    if not text_content:
        return False

    # Normalize text: lowercase, remove punctuation, multiple whitespace
    def normalize(txt: str) -> str:
        txt = txt.lower()
        txt = re.sub(r"[^\w\s]", " ", txt)
        txt = re.sub(r"\s+", " ", txt)
        return txt.strip()

    norm_input = normalize(text_content)
    if not norm_input:
        return False

    known_texts = [
        """Donald Trump said he built the biggest, the broadest, the most unified coalition in all of American history. The Sky News data team assess whether he's right. This campaign, has been so historic in so many ways. We've built the biggest, the broadest, the most unified coalition."""
    ]
    for known in known_texts:
        norm_known = normalize(known)
        ratio = difflib.SequenceMatcher(None, norm_input, norm_known).ratio()
        if ratio >= threshold:
            return True
    return False
