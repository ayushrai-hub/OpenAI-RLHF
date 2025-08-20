# ideal_completion.py

from langchain_community.tools import DuckDuckGoSearchRun
import spacy
import time
from sentence_transformers import SentenceTransformer


try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading en_core_web_sm model...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

search = DuckDuckGoSearchRun()

model = SentenceTransformer("dunzhang/stella_en_400M_v5", trust_remote_code=True).cuda()

query_prompt_name = "s2p_query"

def extract_text_from_docx(file_path):
    import docx
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    text = '.'.join(full_text)
    return text

def extract_text_from_pdf(file_path):
    import pypdf
    with open(file_path, 'rb') as pdf_file:
        read_pdf = pypdf.PdfReader(pdf_file)
        full_text = []
        for page_num in range(len(read_pdf.pages)):
            page = read_pdf.pages[page_num]
            full_text.append(page.extract_text().strip())
        text = '. '.join(full_text)
        return text

def extract_text_from_odt(file_path):
    from odf import text, teletype
    from odf.opendocument import load
    textdoc = load(file_path)
    allparas = textdoc.getElementsByType(text.P)
    full_text = []
    for para in allparas:
        full_text.append(teletype.extractText(para))
    text = '.'.join(full_text)
    return text

def has_plagiarism_from_text(query, threshold=0.9):
    query = nlp(query)
    queries = [sent.text for sent in query.sents]
    docs = []
    for query in queries:
        error = True
        while error:
            try:
                res = search.invoke(query)
                error = False
            except:
                time.sleep(5)
        res_ = nlp(res)
        sentences = [sent.text for sent in res_.sents]
        for sentence in sentences:
            docs.append(sentence)

    query_embeddings = model.encode(queries, prompt_name=query_prompt_name)
    doc_embeddings = model.encode(docs)
    similarities = model.similarity(query_embeddings, doc_embeddings)

    # Get max similarity score for each query
    max_similarities = similarities.max(dim=1)
    max_similarity = max_similarities.values.max()
    return max_similarity > threshold

def has_plagiarism(file_path, threshold=0.9):
    if file_path.endswith(".docx"):
        return has_plagiarism_from_text(extract_text_from_docx(file_path), threshold)
    elif file_path.endswith(".pdf"):
        return has_plagiarism_from_text(extract_text_from_pdf(file_path), threshold)
    elif file_path.endswith(".odt"):
        return has_plagiarism_from_text(extract_text_from_odt(file_path), threshold)
    else:
        return has_plagiarism_from_text(file_path, threshold)
