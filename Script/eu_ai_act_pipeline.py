import re
import json
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError as e:
    raise ImportError("Install PyMuPDF with: pip install pymupdf") from e


PDF_PATH = r"C:\Users\LENOVO\Downloads\official EU AI Act text.pdf"
OUTPUT_DIR = Path(r"C:\Users\LENOVO\ai-act-onto-pipeline\eu_ai_act_processed")
OUTPUT_DIR.mkdir(exist_ok=True)


def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        pages.append(text)
    doc.close()
    return "\n".join(pages)


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = text.replace("`", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_into_articles(text: str):
    lines = text.splitlines()
    articles = []

    current_article_number = None
    current_title = ""
    current_lines = []

    article_pattern = re.compile(r"^\s*Article\s+(\d+[A-Za-z\-]*)\s*$", re.IGNORECASE)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        match = article_pattern.match(line)

        if match:
            # Save previous article
            if current_article_number is not None:
                article_text = "\n".join(current_lines).strip()
                articles.append({
                    "id": f"Article_{current_article_number}",
                    "article_number": current_article_number,
                    "title": current_title,
                    "text": article_text
                })

            # Start new article
            current_article_number = match.group(1)
            current_lines = [line]

            # Next non-empty line is often the title
            title = ""
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                if next_line:
                    title = next_line
                    break
                j += 1

            current_title = title
        else:
            if current_article_number is not None:
                current_lines.append(lines[i])

        i += 1

    # Save last article
    if current_article_number is not None:
        article_text = "\n".join(current_lines).strip()
        articles.append({
            "id": f"Article_{current_article_number}",
            "article_number": current_article_number,
            "title": current_title,
            "text": article_text
        })

    return articles


def split_article_into_chunks(article_text: str, max_chars: int = 1800, overlap: int = 200):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", article_text) if p.strip()]
    chunks = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)

            if overlap > 0 and current:
                tail = current[-overlap:] if len(current) > overlap else current
                current = f"{tail}\n\n{para}".strip()
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def save_outputs(full_text: str, articles: list, chunked_articles: list):
    (OUTPUT_DIR / "eu_ai_act_full_text.txt").write_text(full_text, encoding="utf-8")

    with open(OUTPUT_DIR / "eu_ai_act_articles.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_DIR / "eu_ai_act_article_chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunked_articles, f, indent=2, ensure_ascii=False)


def main():
    print("Extracting text from PDF...")
    raw_text = extract_text_from_pdf(PDF_PATH)
    cleaned_text = clean_text(raw_text)

    print("Splitting into articles...")
    articles = split_into_articles(cleaned_text)
    print(f"Found {len(articles)} articles.")

    if articles:
        print("First 5 detected articles:")
        for art in articles[:5]:
            print(f"- Article {art['article_number']}: {art['title']}")

    chunked_articles = []
    for article in articles:
        chunks = split_article_into_chunks(article["text"], max_chars=1800, overlap=200)
        chunked_articles.append({
            "id": article["id"],
            "article_number": article["article_number"],
            "title": article["title"],
            "num_chunks": len(chunks),
            "chunks": chunks
        })

    save_outputs(cleaned_text, articles, chunked_articles)
    print(f"Saved files to: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
