import docx
doc = docx.Document()
r = list(doc.part.rels.values())[0]
try:
    print(dir(r.target_part))
    print(hasattr(r.target_part, 'blob'))
    print(r.target_part.partname)
except Exception as e:
    print(e)
