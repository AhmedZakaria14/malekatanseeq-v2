#!/usr/bin/env python3
"""Apply deterministic SEO and contact-data fixes to the static export."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://malekatanseeq-v2.vercel.app"
BRAND = "ملكة لتنسيق الحدائق"
LOCAL_PHONE = "0500000000"
INTERNATIONAL_PHONE = "966500000000"
OG_IMAGE = f"{BASE_URL}/wp-content/uploads/custom/logo.png"


PAGES = {
    "index.html": {
        "route": "/",
        "title": "شركة تنسيق حدائق بالرياض | ملكة لتنسيق الحدائق",
        "description": (
            "شركة ملكة لتنسيق الحدائق بالرياض تقدم تصميم وتنفيذ الحدائق المنزلية، "
            "الثيل، شبكات الري، الشلالات، المظلات والجلسات بجودة عالية."
        ),
        "h1": "شركة ملكة لتنسيق الحدائق بالرياض",
        "type": "home",
    },
    "الخدمات/index.html": {
        "route": "/الخدمات/",
        "title": "خدمات تنسيق حدائق بالرياض | ملكة لتنسيق الحدائق",
        "description": (
            "اكتشف خدمات تنسيق الحدائق بالرياض: تصميم اللاندسكيب، تركيب الثيل، "
            "المظلات والجلسات، الشلالات والنوافير، شبكات الري وقص الأشجار."
        ),
        "h1": "خدمات تنسيق الحدائق بالرياض",
        "type": "service",
        "service": "خدمات تصميم وتنسيق الحدائق",
    },
    "من-نحن/index.html": {
        "route": "/من-نحن/",
        "title": "ملكة لتنسيق الحدائق بالرياض | خبرة في اللاندسكيب",
        "description": (
            "تعرف على شركة ملكة لتنسيق الحدائق بالرياض وخبرتنا في تصميم وتنفيذ "
            "اللاندسكيب والحدائق المنزلية باحتراف وجودة تناسب مختلف المساحات."
        ),
        "h1": "عن ملكة لتنسيق الحدائق بالرياض",
        "type": "about",
    },
    "تواصل-معنا/index.html": {
        "route": "/تواصل-معنا/",
        "title": "تواصل مع شركة تنسيق حدائق بالرياض | ملكة",
        "description": (
            "تواصل مع ملكة لتنسيق الحدائق بالرياض لطلب استشارة أو عرض سعر لتصميم "
            "الحدائق والثيل والمظلات والشلالات وشبكات الري."
        ),
        "h1": "تواصل مع ملكة لتنسيق الحدائق بالرياض",
        "type": "contact",
    },
    "جلسات-الحديقة/index.html": {
        "route": "/جلسات-الحديقة/",
        "title": "تنسيق حدائق وتركيب ثيل بالرياض | ملكة",
        "description": (
            "تصميم وتنسيق حدائق بالرياض مع توريد وتركيب الثيل الطبيعي والصناعي "
            "وتنفيذ لاندسكيب متكامل للفلل والمنازل والاستراحات."
        ),
        "h1": "تنسيق حدائق وتركيب ثيل بالرياض",
        "type": "service",
        "service": "تنسيق الحدائق وتركيب الثيل",
    },
    "شلالات-ونوافير/index.html": {
        "route": "/شلالات-ونوافير/",
        "title": "تصميم شلالات ونوافير بالرياض | ملكة",
        "description": (
            "تصميم وتنفيذ شلالات ونوافير بالرياض للحدائق والفلل بأشكال منزلية "
            "وجدارية عصرية تضيف الفخامة والهدوء للمساحات الخارجية."
        ),
        "h1": "تصميم شلالات ونوافير بالرياض",
        "type": "service",
        "service": "تصميم وتنفيذ الشلالات والنوافير",
    },
    "مظلات-وجلسات/index.html": {
        "route": "/مظلات-وجلسات/",
        "title": "تركيب مظلات وجلسات حدائق بالرياض | ملكة",
        "description": (
            "تصميم وتركيب مظلات وجلسات حدائق بالرياض بخيارات خشبية وحديدية "
            "وعصرية تناسب الفلل والمنازل والاستراحات وتوفر الظل والخصوصية."
        ),
        "h1": "تركيب مظلات وجلسات حدائق بالرياض",
        "type": "service",
        "service": "تركيب مظلات وجلسات الحدائق",
    },
    "قص-اشجار-احواض-زراعية/index.html": {
        "route": "/قص-اشجار-احواض-زراعية/",
        "title": "قص وتقليم الأشجار بالرياض | ملكة لتنسيق الحدائق",
        "description": (
            "خدمة قص وتقليم الأشجار والنخيل بالرياض وتنظيف الحدائق باحتراف، "
            "لتحسين نمو النباتات والحفاظ على سلامة وجمال المساحات الخضراء."
        ),
        "h1": "قص وتقليم الأشجار والنخيل بالرياض",
        "type": "service",
        "service": "قص وتقليم الأشجار والنخيل",
    },
    "احواض-زراعية/index.html": {
        "route": "/احواض-زراعية/",
        "title": "تصميم أحواض زراعية بالرياض | ملكة لتنسيق الحدائق",
        "description": (
            "تصميم وتنفيذ أحواض زراعية بالرياض للحدائق والفلل بأحجام وخامات "
            "متنوعة، مع توزيع عملي للنباتات يرفع جمال المساحة الخارجية."
        ),
        "h1": "تصميم وتنفيذ أحواض زراعية بالرياض",
        "type": "service",
        "service": "تصميم وتنفيذ الأحواض الزراعية",
    },
    "ممرات-حجرية/index.html": {
        "route": "/ممرات-حجرية/",
        "title": "تصميم ممرات حجرية بالرياض | ملكة لتنسيق الحدائق",
        "description": (
            "تصميم وتنفيذ ممرات حجرية للحدائق بالرياض باستخدام الحجر الطبيعي "
            "والصناعي، بتنسيقات عملية وعصرية تناسب المداخل والساحات."
        ),
        "h1": "تصميم وتنفيذ ممرات حجرية بالرياض",
        "type": "service",
        "service": "تصميم وتنفيذ الممرات الحجرية",
    },
    "شبكه-رأي/index.html": {
        "route": "/شبكه-رأي/",
        "title": "تركيب شبكات ري حدائق بالرياض | ملكة",
        "description": (
            "تصميم وتركيب شبكات ري حديثة للحدائق بالرياض لضمان توزيع المياه "
            "بكفاءة وتقليل الهدر والحفاظ على النباتات والثيل طوال العام."
        ),
        "h1": "تركيب شبكات ري حدائق بالرياض",
        "type": "service",
        "service": "تصميم وتركيب شبكات الري",
    },
    "شبكه-رزاز/index.html": {
        "route": "/شبكه-رزاز/",
        "title": "تركيب شبكات رذاذ بالرياض | ملكة لتنسيق الحدائق",
        "description": (
            "تركيب شبكات رذاذ وتلطيف الأجواء بالرياض للحدائق والجلسات والمقاهي "
            "والاستراحات، مع توزيع مدروس وتغطية مناسبة للمساحة."
        ),
        "h1": "تركيب شبكات رذاذ وتلطيف بالرياض",
        "type": "service",
        "service": "تركيب شبكات الرذاذ",
    },
    "احواض-زراعة-صناعية/index.html": {
        "route": "/احواض-زراعة-صناعية/",
        "title": "تصميم أحواض زراعة صناعية بالرياض | ملكة للحدائق",
        "description": (
            "تصميم وتركيب أحواض زراعة صناعية بالرياض للحدائق والفلل والمشاريع "
            "التجارية بأشكال عصرية وخامات متينة قليلة الصيانة."
        ),
        "h1": "تصميم أحواض زراعة صناعية بالرياض",
        "type": "service",
        "service": "تصميم وتركيب أحواض الزراعة الصناعية",
    },
    "غرف-زجاج/index.html": {
        "route": "/غرف-زجاج/",
        "title": "تركيب غرف زجاجية للحدائق بالرياض | ملكة",
        "description": (
            "تصميم وتركيب غرف زجاجية للحدائق والجلسات بالرياض بطابع عصري، "
            "لتوفير مساحة مريحة وأنيقة للاستمتاع بالإطلالة في مختلف الأجواء."
        ),
        "h1": "تصميم وتركيب غرف زجاجية بالرياض",
        "type": "service",
        "service": "تصميم وتركيب الغرف الزجاجية",
    },
    "2025/11/16/أهمية-استخدام-النباتات-المحلية-في-تصم/index.html": {
        "route": "/2025/11/16/أهمية-استخدام-النباتات-المحلية-في-تصم/",
        "title": "مميزات تركيب الثيل الطبيعي للحدائق بالرياض | ملكة",
        "description": (
            "تعرف على مميزات الثيل الطبيعي للحدائق، وكيفية اختياره وتركيبه "
            "والعناية به للحصول على مساحة خضراء صحية وجذابة في مناخ الرياض."
        ),
        "h1": "مميزات تركيب الثيل الطبيعي للحدائق",
        "type": "article",
    },
    "2025/11/16/الفرق-بين-العشب-الطبيعي-والعشب-الصناع/index.html": {
        "route": "/2025/11/16/الفرق-بين-العشب-الطبيعي-والعشب-الصناع/",
        "title": "أهمية تنسيق الحدائق في جمال المنزل | ملكة",
        "description": (
            "تعرف على أهمية تنسيق الحدائق في تحسين جمال المنزل ورفع قيمة العقار، "
            "وأبرز عناصر التصميم التي تصنع مساحة خارجية مريحة وعملية."
        ),
        "h1": "أهمية تنسيق الحدائق في تحسين جمال المنزل",
        "type": "article",
    },
    "2025/11/16/تنسيق-اللاندسكيب-ودوره-في-تحسين-جودة-ا/index.html": {
        "route": "/2025/11/16/تنسيق-اللاندسكيب-ودوره-في-تحسين-جودة-ا/",
        "title": "الشلالات والنوافير وفخامة الحدائق | ملكة",
        "description": (
            "دليل لأهمية الشلالات والنوافير في تصميم الحدائق، وأبرز الأنواع "
            "والأفكار التي تضيف الهدوء والفخامة إلى المساحات الخارجية."
        ),
        "h1": "الشلالات والنوافير ودورها في فخامة الحدائق",
        "type": "article",
    },
}


def strip_tag(head: str, pattern: str) -> str:
    return re.sub(pattern, "", head, flags=re.IGNORECASE | re.DOTALL)


def breadcrumbs(route: str, title: str) -> dict:
    items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "الرئيسية",
            "item": f"{BASE_URL}/",
        }
    ]
    if route != "/":
        items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": title.split("|", 1)[0].strip(),
                "item": f"{BASE_URL}{route}",
            }
        )
    return {
        "@type": "BreadcrumbList",
        "@id": f"{BASE_URL}{route}#breadcrumb",
        "itemListElement": items,
    }


def build_schema(page: dict) -> dict:
    route = page["route"]
    url = f"{BASE_URL}{route}"
    organization = {
        "@type": ["LocalBusiness", "ProfessionalService"],
        "@id": f"{BASE_URL}/#business",
        "name": BRAND,
        "url": f"{BASE_URL}/",
        "logo": {
            "@type": "ImageObject",
            "url": OG_IMAGE,
            "width": 1024,
            "height": 1024,
        },
        "image": OG_IMAGE,
        "telephone": f"+{INTERNATIONAL_PHONE}",
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "الرياض",
            "addressRegion": "الرياض",
            "addressCountry": "SA",
        },
        "areaServed": {
            "@type": "City",
            "name": "الرياض",
        },
    }
    website = {
        "@type": "WebSite",
        "@id": f"{BASE_URL}/#website",
        "url": f"{BASE_URL}/",
        "name": BRAND,
        "inLanguage": "ar-SA",
        "publisher": {"@id": f"{BASE_URL}/#business"},
    }
    webpage_type = "Article" if page["type"] == "article" else "WebPage"
    webpage = {
        "@type": webpage_type,
        "@id": f"{url}#webpage",
        "url": url,
        "name": page["title"],
        "description": page["description"],
        "inLanguage": "ar-SA",
        "isPartOf": {"@id": f"{BASE_URL}/#website"},
        "breadcrumb": {"@id": f"{url}#breadcrumb"},
        "primaryImageOfPage": {"@id": f"{url}#primaryimage"},
    }
    if page["type"] == "article":
        webpage.update(
            {
                "headline": page["h1"],
                "author": {"@id": f"{BASE_URL}/#business"},
                "publisher": {"@id": f"{BASE_URL}/#business"},
                "datePublished": "2025-11-16",
                "dateModified": "2026-07-25",
            }
        )
    graph = [
        organization,
        website,
        {
            "@type": "ImageObject",
            "@id": f"{url}#primaryimage",
            "url": OG_IMAGE,
            "width": 1024,
            "height": 1024,
        },
        breadcrumbs(route, page["title"]),
        webpage,
    ]
    if page["type"] == "service":
        graph.append(
            {
                "@type": "Service",
                "@id": f"{url}#service",
                "name": page["service"],
                "description": page["description"],
                "url": url,
                "provider": {"@id": f"{BASE_URL}/#business"},
                "areaServed": {"@type": "City", "name": "الرياض"},
                "serviceType": page["service"],
            }
        )
    return {"@context": "https://schema.org", "@graph": graph}


def seo_block(page: dict) -> str:
    route = page["route"]
    url = f"{BASE_URL}{route}"
    title = html.escape(page["title"], quote=True)
    description = html.escape(page["description"], quote=True)
    schema = json.dumps(build_schema(page), ensure_ascii=False, separators=(",", ":"))
    og_type = "article" if page["type"] == "article" else "website"
    return f"""
<!-- BEGIN MANAGED SEO -->
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ar-SA" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
<meta property="og:locale" content="ar_SA">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:secure_url" content="{OG_IMAGE}">
<meta property="og:image:width" content="1024">
<meta property="og:image:height" content="1024">
<meta property="og:image:alt" content="{BRAND}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{OG_IMAGE}">
<script type="application/ld+json">{schema}</script>
<!-- END MANAGED SEO -->
"""


def optimize_page(path: Path, page: dict) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "/wp-content/uploads/2025/11/tools-pots-with-plants-soil-1.jpg",
        "/assets/new_images/turf.jpg",
    )
    text = re.sub(
        r"<link\b(?=[^>]*\btype=[\"']application/rss\+xml[\"'])[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"<script\b[^>]*\bsrc=[\"']/wp-includes/js/comment-reply\.min\.js[\"'][^>]*>\s*</script>",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"<!-- BEGIN MANAGED SEO -->.*?<!-- END MANAGED SEO -->",
        "",
        text,
        flags=re.DOTALL,
    )
    match = re.search(r"<head\b[^>]*>(.*?)</head>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        raise RuntimeError(f"No <head> found in {path}")
    head = match.group(1)
    for pattern in (
        r"<title\b[^>]*>.*?</title>",
        r"<meta\b(?=[^>]*\bname=[\"'](?:description|keywords|robots|google-site-verification)[\"'])[^>]*>",
        r"<link\b(?=[^>]*\brel=[\"']canonical[\"'])[^>]*>",
        r"<link\b(?=[^>]*\brel=[\"']alternate[\"'])(?=[^>]*\bhreflang=)[^>]*>",
        r"<meta\b(?=[^>]*\bproperty=[\"']og:[^\"']+[\"'])[^>]*>",
        r"<meta\b(?=[^>]*\bname=[\"']twitter:[^\"']+[\"'])[^>]*>",
        r"<script\b(?=[^>]*\btype=[\"']application/ld\+json[\"'])[^>]*>.*?</script>",
    ):
        head = strip_tag(head, pattern)
    head = "\n".join(line.rstrip() for line in head.splitlines()).rstrip()
    head = head + "\n" + seo_block(page)
    text = text[: match.start(1)] + head + text[match.end(1) :]

    if not re.search(r"<h1\b", text, flags=re.IGNORECASE):
        h2 = re.search(r"<h2\b([^>]*)>.*?</h2>", text, flags=re.IGNORECASE | re.DOTALL)
        if h2:
            replacement = f"<h1{h2.group(1)}>{html.escape(page['h1'])}</h1>"
            text = text[: h2.start()] + replacement + text[h2.end() :]
    path.write_text(text, encoding="utf-8")


def replace_contact_and_legacy_data() -> None:
    phone_replacements = (
        ("0532391307", LOCAL_PHONE),
        ("966532391307", INTERNATIONAL_PHONE),
        ("0536759014", LOCAL_PHONE),
    )
    visible_content_replacements = (
        ("https://zahraty.com", BASE_URL),
        ("http://zahraty.com", BASE_URL),
        ("zahraty.com", "malekatanseeq-v2.vercel.app"),
        ("الحدايق", "الحدائق"),
    )
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path == Path(__file__):
            continue
        raw = path.read_bytes()
        if b"\x00" in raw:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        updated = text
        for old, new in phone_replacements:
            updated = updated.replace(old, new)
        if path.suffix.lower() == ".html" and "wp-json" not in path.parts:
            for old, new in visible_content_replacements:
                updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")


def write_supporting_files() -> None:
    urls = []
    for page in PAGES.values():
        priority = "1.0" if page["route"] == "/" else ("0.8" if page["type"] == "service" else "0.7")
        changefreq = "weekly" if page["route"] == "/" else ("monthly" if page["type"] == "article" else "weekly")
        urls.append(
            "  <url>\n"
            f"    <loc>{BASE_URL}{page['route']}</loc>\n"
            "    <lastmod>2026-07-25</lastmod>\n"
            f"    <changefreq>{changefreq}</changefreq>\n"
            f"    <priority>{priority}</priority>\n"
            "  </url>"
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /wp-admin/\n"
        "Disallow: /wp-json/\n"
        "Disallow: /xmlrpc.php/\n"
        "Disallow: /feed/\n"
        "Disallow: /comments/feed/\n"
        "Disallow: /*?p=\n\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )
    (ROOT / "llms.txt").write_text(
        "# ملكة لتنسيق الحدائق\n\n"
        "شركة متخصصة في تصميم وتنسيق الحدائق واللاندسكيب في الرياض، المملكة العربية السعودية.\n\n"
        "## الخدمات الرئيسية\n"
        "- تصميم وتنسيق الحدائق المنزلية\n"
        "- تركيب الثيل الطبيعي والصناعي\n"
        "- تصميم الشلالات والنوافير\n"
        "- تركيب المظلات والجلسات الخارجية\n"
        "- تصميم الأحواض والممرات الحجرية\n"
        "- تركيب شبكات الري والرذاذ\n"
        "- قص وتقليم الأشجار\n"
        "- تركيب الغرف الزجاجية\n\n"
        f"الموقع: {BASE_URL}/\n"
        f"الهاتف: {LOCAL_PHONE}\n",
        encoding="utf-8",
    )


def main() -> None:
    replace_contact_and_legacy_data()
    for relative, page in PAGES.items():
        optimize_page(ROOT / relative, page)
    write_supporting_files()
    print(f"Optimized {len(PAGES)} indexable pages.")


if __name__ == "__main__":
    main()
