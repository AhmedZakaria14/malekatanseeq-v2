// Retire WordPress endpoints and resolve known legacy post IDs without query strings.
const pages = {
  "101": "/تواصل-معنا/",
  "108": "/احواض-زراعية/",
  "110": "/شلالات-ونوافير/",
  "112": "/مظلات-وجلسات/",
  "114": "/قص-اشجار-احواض-زراعية/",
  "116": "/جلسات-الحديقة/",
  "150": "/ممرات-حجرية/",
  "247": "/مقالات/أهمية-تنسيق-الحدائق-في-جمال-المنزل/",
  "609": "/غرف-زجاج/",
  "620": "/احواض-زراعة-صناعية/",
  "646": "/شبكه-رأي/",
  "658": "/شبكه-رزاز/",
  "97": "/من-نحن/",
  "99": "/الخدمات/",
  "245": "/مقالات/مميزات-تركيب-الثيل-الطبيعي/",
  "243": "/مقالات/الشلالات-والنوافير-وفخامة-الحدائق/",
  "95": "/"
};

module.exports = function handler(req, res) {
  const params = new URL(req.url, 'https://www.landscapingriyadh.com').searchParams;
  const id = params.get('p') || params.get('page_id');
  if (id && Object.hasOwn(pages, id)) {
    res.statusCode = 301;
    res.setHeader('Location', encodeURI(pages[id]));
    res.end();
    return;
  }
  res.statusCode = 410;
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('X-Robots-Tag', 'noindex');
  res.end('<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><title>الصفحة لم تعد متاحة</title><h1>الصفحة لم تعد متاحة</h1><p>تم إلغاء هذا الرابط القديم.</p><a href="/">العودة للرئيسية</a></html>');
};
