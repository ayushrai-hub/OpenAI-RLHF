import requests

url = 'https://cdn.bookey.app/files/pdf/book/en/holier-than-thou.pdf'

resp = requests.get(url)
print(resp.status_code, len(resp.content))
from PyPDF2 import PdfReader
from io import BytesIO

reader = PdfReader(BytesIO(resp.content))
a = len(reader.pages)
print(a)

# Extract all pages' text
all_text = []
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    all_text.append((i+1, text))

# Let's find the text occurrences of the chapter headings
import re

chapters = [
    "Chapter 1 : The Perfection of God's Holiness - Understanding Absolute Moral Purity",
    "Chapter 2 : Confronting Our Misconceptions about Holiness",
    "Chapter 3 : The Intersection of Holiness and Love - God's Character in Full",
    "Chapter 4 : Transforming Lives Through Holiness - Personal and Spiritual Growth",
    "Chapter 5 : Living in Awe and Reverence of a Holy God",
    "Chapter 6 : The Eternal Promise of Holiness - Hope for the Future",
    "Chapter 7 : Holiness in Community - Reflecting God's Character Together"
]

# Remove maybe the extra spaces and colon? Or we can search a generic pattern.
# Let's look at each page and check for "Chapter" and a number.

for num, txt in all_text:
    if not txt:
        continue
    if 'Chapter' in txt:
        # Print beginning
        print(num, txt[:300].replace('\n',' '))

# Define chapters with start and end page numbers

chapter_pages = {
    1: (7, 8),  # starts at 7, ends before 9
    2: (9, 11), # 9 to 11
    3: (12, 14),
    4: (15, 18), # maybe includes pages 15-18 inclusive
    5: (19, 21),
    6: (22, 24),
    7: (25, 27)  # 25 to end (27)
}

# Extract text and count words per chapter:

import re

result = []

for chap_num, (start_page, end_page) in chapter_pages.items():
    parts = []
    for p in range(start_page, end_page+1):
        txt = reader.pages[p-1].extract_text()
        if txt:
            parts.append(txt)
    chap_text = "\n".join(parts)
    # Count words
    counts = {}
    for word in ['holiness', 'God', 'sin']:
        pattern = r'\b' + word + r'\b'
        num = len(re.findall(pattern, chap_text, flags=re.IGNORECASE))
        counts[word] = num
    result.append((chap_num, counts, chap_text[:200]))  # include snippet

result
# Create table data with names
chapter_names = [
    "The Perfection of God's Holiness",
    "Confronting Our Misconceptions about Holiness",
    "The Intersection of Holiness and Love",
    "Transforming Lives Through Holiness",
    "Living in Awe and Reverence of a Holy God",
    "The Eternal Promise of Holiness",
    "Holiness in Community"
]

# Combine counts
table_data = []
for i, name in enumerate(chapter_names, start=1):
    counts = next((r[1] for r in result if r[0] == i), {})
    table_data.append((f"Chapter {i}: {name}", counts['holiness'], counts['God'], counts['sin']))

table_data
