import difflib

document_1 = """Line one of document one
Line two of document one
Line three of document one"""

document_2 = """Line one of document two
Line two of document two
Line three of document two"""

# Split documents into lines
lines1 = document_1.splitlines()
lines2 = document_2.splitlines()

diff = difflib.unified_diff(lines1, lines2, lineterm='')
for line in diff:
    print(line)
