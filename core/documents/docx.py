import zipfile
from xml.etree.ElementTree import XML


class Docx:
    def __init__(self, fullpath):
        self.fullpath = fullpath;

    def get_text(self):
        with zipfile.ZipFile(self.fullpath) as document:
            xml_content = document.read("word/document.xml").decode(encoding="UTF-8", errors="replace");

        tree = XML(xml_content);
        namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}";

        paragraphs = [];
        for paragraph in tree.getiterator(namespace + "p"):
            texts = [node.text for node in paragraph.getiterator(namespace + "t") if node.text];
            
            if texts:
                paragraphs.append(''.join(texts));

        return "\n\n".join(paragraphs);
