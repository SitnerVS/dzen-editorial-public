from __future__ import annotations

import html
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil
from xml.etree.ElementTree import Element, SubElement, ElementTree, register_namespace
from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parent
ARTICLES = ROOT / "articles"
OUT = ROOT / "_site"
BASE_URL = "https://sitnervs.github.io/dzen-editorial-public"
SITE_TITLE = "Редакционный журнал"
SITE_DESCRIPTION = "Аналитические материалы о комплаенсе, антифроде, OSINT и актуальных событиях."
MD = MarkdownIt("commonmark", {"html": False, "linkify": False, "typographer": False})
Y = "http://news.yandex.ru"
CONTENT = "http://purl.org/rss/1.0/modules/content/"
register_namespace("yandex", Y)
register_namespace("content", CONTENT)

def article_date(path: Path) -> datetime:
    match = re.match(r"(\d{8})T(\d{6})Z-", path.name)
    if match:
        return datetime.strptime("".join(match.groups()), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)

def slug_for(path: Path) -> str:
    # Keep article URLs short and ASCII-only for RSS compatibility.
    stem = path.stem
    stamp = re.match(r"^(\d{8})T\d{6}Z-", stem)
    date_part = stamp.group(1) if stamp else "article"
    name = re.sub(r"^\d{8}T\d{6}Z-", "", stem)
    category = re.match(r"^(compliance|antifraud|osint|russia_news|world_news)-", name)
    category_part = category.group(1) if category else "article"
    if category:
        name = name[category.end():]
    translit = str.maketrans({
        "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"yo","ж":"zh",
        "з":"z","и":"i","й":"y","к":"k","л":"l","м":"m","н":"n","о":"o",
        "п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"kh","ц":"ts",
        "ч":"ch","ш":"sh","щ":"shch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya",
    })
    ascii_name = name.lower().translate(translit)
    ascii_name = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-")
    # Timestamp + category prevent collisions between articles with similar titles.
    return f"{date_part}-{category_part}-{ascii_name[:48]}".strip("-")

def title_for(text: str, fallback: str) -> str:
    return next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), fallback)

def feed_body(markdown: str) -> str:
    # Keep source bibliography on the article page; Yandex forbids source names
    # inside yandex:full-text.
    return re.split(r"(?im)^##\\s+источники\\s*$", markdown, maxsplit=1)[0].strip()

def plain_text(markdown: str) -> str:
    body = re.sub(r"(?m)^#\s+.*$", "", markdown)
    body = re.sub(r"(?m)^##?\s+", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"[*_\x60]", "", body)
    body = re.sub(r"(?m)^\s*[-*+]\s+", "• ", body)
    body = re.sub(r"(?m)^\s*\d+\.\s+", "• ", body)
    return re.sub(r"\n{3,}", "\n\n", body).strip()

def render_page(title: str, body: str, url: str, date: datetime) -> str:
    rendered = MD.render(body)
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — {SITE_TITLE}</title><meta name="description" content="{html.escape(plain_text(body)[:220], quote=True)}">
<link rel="canonical" href="{url}"><link rel="alternate" type="application/rss+xml" title="RSS" href="{BASE_URL}/feed.xml">
<style>
:root{{--bg:#f5f6f8;--paper:#fff;--ink:#20242a;--muted:#68717d;--line:#e5e8ec;--accent:#b64a24}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:18px/1.75 Georgia,serif}}
header{{border-bottom:1px solid var(--line);background:#fff}}.top{{max-width:850px;margin:auto;padding:22px 24px;font:600 14px/1.4 Arial,sans-serif;letter-spacing:.04em}}
main{{max-width:850px;margin:42px auto;padding:48px 58px;background:var(--paper);border:1px solid var(--line);border-radius:10px}}
h1{{font:700 clamp(30px,5vw,42px)/1.2 Arial,sans-serif;letter-spacing:-.03em;margin:0 0 18px}}
h2,h3{{font-family:Arial,sans-serif;line-height:1.3;margin-top:1.8em}}p,li{{max-width:72ch}}a{{color:var(--accent)}}.meta{{color:var(--muted);font:14px Arial,sans-serif;margin-bottom:34px}}
footer{{max-width:850px;margin:0 auto 40px;padding:0 24px;color:var(--muted);font:13px Arial,sans-serif}}footer a{{margin-left:10px}}
@media(max-width:650px){{body{{font-size:17px}}main{{margin:16px 10px;padding:28px 22px}}}}
</style></head><body><header><div class="top"><a href="{BASE_URL}/" style="color:inherit;text-decoration:none">{SITE_TITLE}</a></div></header>
<main><h1>{html.escape(title)}</h1><div class="meta">{date.astimezone(timezone(timedelta(hours=3))).strftime("%d.%m.%Y · %H:%M (МСК)")}</div>{rendered}</main>
<footer>Материалы сайта. Информация носит аналитический и ознакомительный характер. <a href="{BASE_URL}/about.html">О редакции и контакты</a></footer></body></html>"""

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    items = []
    for path in sorted(ARTICLES.glob("*.md"), key=article_date, reverse=True):
        raw = path.read_text(encoding="utf-8")
        title = title_for(raw, path.stem)
        date = article_date(path)
        slug = slug_for(path)
        rel = f"articles/{slug}.html"
        url = f"{BASE_URL}/{rel}"
        body = re.sub(r"(?m)^#\s+.*(?:\n|$)", "", raw, count=1).strip()
        page = OUT / rel
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(render_page(title, body, url, date), encoding="utf-8")
        items.append({"title": title, "date": date, "url": url, "body": body, "raw": raw, "slug": slug})

    cards = []
    for item in items:
        excerpt = html.escape(plain_text(item["body"])[:260])
        cards.append(f'<article><div class="date">{item["date"].astimezone(timezone(timedelta(hours=3))).strftime("%d.%m.%Y")}</div><h2><a href="{item["url"]}">{html.escape(item["title"])}</a></h2><p>{excerpt}…</p><a class="more" href="{item["url"]}">Читать статью →</a></article>')
    index = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{SITE_TITLE}</title><link rel="alternate" type="application/rss+xml" title="RSS" href="{BASE_URL}/feed.xml"><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f5f6f8;color:#20242a;font:17px/1.65 Arial,sans-serif}}header{{background:#17212b;color:#fff;padding:56px 24px}}.hero{{max-width:900px;margin:auto}}h1{{font-size:clamp(32px,5vw,48px);line-height:1.12;margin:0 0 14px}}.hero p{{color:#cbd3dc;max-width:650px}}main{{max-width:900px;margin:36px auto;padding:0 20px}}article{{background:#fff;border:1px solid #e5e8ec;border-radius:10px;padding:28px 32px;margin:18px 0}}h2{{line-height:1.25;margin:8px 0}}a{{color:#a94322;text-decoration:none}}a:hover{{text-decoration:underline}}.date{{font-size:13px;color:#68717d}}.more{{font-size:14px;font-weight:700}}.rss{{color:#fff;text-decoration:underline}}footer{{max-width:900px;margin:40px auto;padding:0 20px;color:#68717d;font-size:13px}}footer a{{margin-left:12px;color:#a94322}}@media(max-width:600px){{article{{padding:22px}}}}
</style></head><body><header><div class="hero"><h1>{SITE_TITLE}</h1><p>{SITE_DESCRIPTION}</p><a class="rss" href="{BASE_URL}/feed.xml">RSS-лента</a></div></header><main>{''.join(cards) if cards else '<p>Первые материалы скоро появятся.</p>'}</main><footer>Независимые редакционные материалы. Все статьи доступны бесплатно. <a href="{BASE_URL}/about.html">О редакции и контакты</a></footer></body></html>"""
    (OUT / "index.html").write_text(index, encoding="utf-8")
    shutil.copyfile(ROOT / "about.html", OUT / "about.html")

    rss = Element("rss", {"version": "2.0"})
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = SITE_TITLE
    SubElement(channel, "link").text = BASE_URL + "/"
    SubElement(channel, "description").text = SITE_DESCRIPTION
    SubElement(channel, "language").text = "ru"
    if items:
        SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    for item in items[:100]:
        node = SubElement(channel, "item")
        SubElement(node, "title").text = item["title"]
        SubElement(node, "link").text = item["url"]
        SubElement(node, "guid", {"isPermaLink": "true"}).text = item["url"]
        SubElement(node, "pubDate").text = item["date"].strftime("%a, %d %b %Y %H:%M:%S +0000")
        SubElement(node, f"{{{Y}}}genre").text = "article"
        rss_body = feed_body(item["body"])
        SubElement(node, f"{{{Y}}}full-text").text = plain_text(rss_body)
        SubElement(node, f"{{{CONTENT}}}encoded").text = MD.render(rss_body)
        SubElement(node, "description").text = plain_text(rss_body)[:400]
        category_match = re.search(r"-(compliance|antifraud|osint|russia_news|world_news)-", path.name)
        if category_match:
            categories = {
                "compliance": "Комплаенс",
                "antifraud": "Антифрод",
                "osint": "OSINT",
                "russia_news": "Новости России",
                "world_news": "Мировые новости",
            }
            SubElement(node, "category").text = categories[category_match.group(1)]
    ElementTree(rss).write(OUT / "feed.xml", encoding="utf-8", xml_declaration=True)

    sitemap = Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    SubElement(sitemap, "{http://www.sitemaps.org/schemas/sitemap/0.9}url").append(
        Element("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
    )
    sitemap[0][0].text = BASE_URL + "/"
    for item in items:
        u = SubElement(sitemap, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")
        SubElement(u, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text = item["url"]
    ElementTree(sitemap).write(OUT / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")

if __name__ == "__main__":
    main()
