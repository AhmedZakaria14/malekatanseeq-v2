#!/usr/bin/env python3
"""Validate the static site's SEO structure and optimize existing image bytes."""
import argparse
import hashlib
import io
import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
HOST = "www.landscapingriyadh.com"
PAGES = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "www.googletagmanager.com" not in p.parts)

def local_path(src):
    url = urlsplit(unescape(src))
    if url.netloc and url.netloc != HOST:
        return None
    if url.scheme and url.scheme not in ("http", "https"):
        return None
    path = (ROOT / unquote(url.path).lstrip("/")).resolve()
    return path if path.is_relative_to(ROOT) else None

def optimize():
    from PIL import Image
    saved, count, sizes = 0, 0, {}
    manifest_path = ROOT / "scripts/optimized-images.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    def blob_hash(data):
        return hashlib.sha1(b"blob " + str(len(data)).encode() + bytes([0]) + data).hexdigest()
    for folder in ("assets", "wp-content/uploads"):
        for path in sorted((ROOT / folder).rglob("*")):
            if path.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
                continue
            try:
                with Image.open(path) as image:
                    sizes[path.resolve()] = image.size
                    original = path.read_bytes()
                    relative = str(path.relative_to(ROOT))
                    if manifest.get(relative) == blob_hash(original):
                        continue
                    if len(original) <= 100000 or getattr(image, "is_animated", False):
                        continue
                    output = io.BytesIO()
                    if image.format == "JPEG":
                        image.convert("RGB").save(output, "JPEG", quality=80, optimize=True, progressive=True)
                    elif image.format == "WEBP":
                        image.save(output, "WEBP", quality=80, method=6)
                    elif image.format == "PNG":
                        image.save(output, "PNG", optimize=True)
                    else:
                        continue
                    optimized = output.getvalue()
                    if len(optimized) < len(original) * 0.92:
                        path.write_bytes(optimized)
                        saved += len(original) - len(optimized)
                        count += 1
            except (OSError, ValueError):
                continue
    def image_tag(match):
        tag = match.group(0)
        src = re.search(r'\bsrc=["\x27]([^"\x27]+)', tag)
        path = local_path(src.group(1)) if src else None
        if path in sizes:
            width, height = sizes[path]
            if not re.search(r'\bwidth\s*=', tag):
                tag = re.sub(r'\s*/?>$', f' width="{width}" height="{height}">', tag) if not re.search(r'\bheight\s*=', tag) else re.sub(r'\s*/?>$', f' width="{width}">', tag)
            elif not re.search(r'\bheight\s*=', tag):
                tag = re.sub(r'\s*/?>$', f' height="{height}">', tag)
            if "custom/logo.png" in src.group(1):
                tag = re.sub(r'\bwidth=["\x27][^"\x27]*["\x27]', f'width="{width}"', tag)
                tag = re.sub(r'\bheight=["\x27][^"\x27]*["\x27]', f'height="{height}"', tag)
        return tag
    for page in PAGES:
        source = page.read_text()
        updated = re.sub(r"<img\b[^>]*>", image_tag, source, flags=re.I)
        if updated != source:
            page.write_text(updated)
    for path in sizes:
        manifest[str(path.relative_to(ROOT))] = blob_hash(path.read_bytes())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + chr(10))
    return {"images_optimized": count, "bytes_saved": saved}

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.headings, self.links, self.canonicals, self.images = [], [], [], []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        if tag == "a":
            self.links.append(a)
        if tag == "link" and a.get("rel") == "canonical":
            self.canonicals.append(a.get("href", ""))
        if tag == "img":
            self.images.append(a)

def validate():
    errors, titles = [], set()
    for page in PAGES:
        source = page.read_text()
        rel = str(page.relative_to(ROOT))
        parsed = Inspector()
        parsed.feed(source)
        title = re.search(r"<title>(.*?)</title>", source, re.S)
        if not title or title.group(1) in titles:
            errors.append(f"{rel}: missing or duplicate title")
        else:
            titles.add(title.group(1))
            if len(unescape(title.group(1))) > 60:
                errors.append(f"{rel}: title exceeds 60 characters")
        if parsed.headings.count(1) != 1:
            errors.append(f"{rel}: expected one H1")
        previous = 0
        for level in parsed.headings:
            if level > previous + 1:
                errors.append(f"{rel}: heading jumps from H{previous} to H{level}")
            previous = level
        expected = "https://" + HOST + ("/" if rel == "index.html" else "/" + rel.removesuffix("index.html"))
        if parsed.canonicals != [expected]:
            errors.append(f"{rel}: incorrect canonical")
        for link in parsed.links:
            if link.get("target") == "_blank" and "noopener" not in link.get("rel", "").split():
                errors.append(f"{rel}: external tab lacks noopener")
        for image in parsed.images:
            path = local_path(image.get("src", ""))
            if path and path.is_file() and ("width" not in image or "height" not in image):
                errors.append(f"{rel}: image dimensions missing")
        for schema in re.findall(r'<script\b[^>]*type=["\x27]application/ld\+json["\x27][^>]*>(.*?)</script>', source, re.S):
            try:
                json.loads(schema)
            except ValueError:
                errors.append(f"{rel}: invalid JSON-LD")
    for url in re.findall(r"\]\((https://[^)]+)\)", (ROOT / "llms.txt").read_text()):
        path = local_path(url)
        target = path / "index.html" if path else None
        if not target or not target.is_file():
            errors.append(f"llms.txt: missing target {url}")
    config = json.loads((ROOT / "vercel.json").read_text())
    security = {h["key"]: h["value"] for rule in config["headers"] if rule["source"] == "/(.*)" for h in rule["headers"]}
    for header in ("Content-Security-Policy", "X-Frame-Options"):
        if header not in security:
            errors.append(f"Missing {header}")
    return {"pages_checked": len(PAGES), "errors": errors}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--optimize", action="store_true")
    args = parser.parse_args()
    report = optimize() if args.optimize else {}
    report.update(validate())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["errors"]:
        raise SystemExit(1)
