"""Read back public deployment content and HTTP security headers."""
import json
import time
import urllib.request
from urllib.parse import quote

ORIGIN = "https://www.landscapingriyadh.com"
def read(path):
    request = urllib.request.Request(ORIGIN + quote(path, safe="/"), headers={"User-Agent": "Landscaping-SEO-Verification/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8"), dict(response.headers)

errors = []
for attempt in range(1, 7):
    errors = []
    try:
        llms, headers = read("/llms.txt")
        if "0500000000" in llms or "الروابط الأساسية" not in llms:
            errors.append("Reviewed llms.txt is not live yet")
        home, headers = read("/")
        headers = {key.lower(): value for key, value in headers.items()}
        for key in ("content-security-policy", "x-frame-options"):
            if key not in headers:
                errors.append("Live header missing: " + key)
        service, _ = read("/شبكه-رأي/")
        if "ما الذي يحدد تصميم شبكة الري؟" not in service:
            errors.append("Updated irrigation content is not live yet")
        print(json.dumps({"attempt": attempt, "host": ORIGIN, "server": headers.get("server"), "content_type": headers.get("content-type"), "security_headers": {key: headers.get(key) for key in ("content-security-policy", "x-frame-options")}, "errors": errors}, ensure_ascii=False), flush=True)
        if not errors:
            break
    except Exception as exc:
        errors = [str(exc)]
        print(json.dumps({"attempt": attempt, "errors": errors}), flush=True)
    if attempt < 6:
        time.sleep(10)
if errors:
    raise SystemExit(1)
