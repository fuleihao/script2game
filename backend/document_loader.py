from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def load_document_text(path: PathLike) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".docx":
        from docx import Document
        doc = Document(str(path))
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    if suffix == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(str(path))
        return "\n".join([(p.extract_text() or "") for p in reader.pages])
    raise ValueError("暂不支持的文件格式：{}".format(suffix))
