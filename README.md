# API Mock Studio

A small, dependency-free Python HTTP mock server driven by JSON route definitions. It helps frontend developers, integration tests, demos, and offline development reproduce predictable API responses without running a real backend.

## Why it exists
Real APIs may be unfinished, slow, rate-limited, unavailable offline, or unsafe to exercise during UI development. API Mock Studio provides deterministic local endpoints with almost no setup and no runtime packages beyond Python.

## Features
- GET, POST, PUT, PATCH, DELETE, HEAD and OPTIONS.
- Dynamic path parameters such as `/users/:id` and `{{params.id}}` response templates.
- Query parsing and request-body echo for integration testing.
- Custom status codes and response headers.
- Optional latency simulation (`delay_ms`, capped at 30 seconds).
- Optional permissive CORS for local frontend development.
- Threaded request handling, 1 MiB request-body limit, useful 404 JSON responses.
- Strict configuration validation and duplicate-route detection.
- Safe localhost binding by default; no telemetry, accounts, API keys, or network dependencies.
- Standard-library runtime only.

## Requirements
Python 3.10 or newer.

## Installation
```bash
git clone https://github.com/rad03i2/api-mock-studio.git
cd api-mock-studio
python -m pip install .
```

For development use `python -m pip install -e .`.

## Quick start
Validate the bundled example:
```bash
api-mock-studio examples/api.json --check
```
Run it:
```bash
api-mock-studio examples/api.json --port 8080
```
Then try `curl http://127.0.0.1:8080/health`, `curl http://127.0.0.1:8080/users/42`, or:
```bash
curl -X POST http://127.0.0.1:8080/echo -H "Content-Type: application/json" -d '{"hello":"world"}'
```

## Configuration
```json
{
  "routes": [
    {"method":"GET", "path":"/users/:id", "status":200,
     "headers":{"X-Mock":"yes"}, "body":{"id":"{{params.id}}"}},
    {"method":"POST", "path":"/echo", "status":201, "body":{"$echo":true}}
  ]
}
```
`{"$echo": true}` returns the request method, path, dynamic parameters, parsed query parameters, and JSON/text body. Use `--cors` only when a local browser app needs cross-origin access. `--host 0.0.0.0` is supported but intentionally not the default.

## Preview / screenshot guidance
Start the bundled example and capture a terminal showing the startup log beside successful `/health` and `/users/42` requests. No screenshot is committed because terminal rendering differs by platform.

## Project structure
```text
src/api_mock_studio/core.py    route validation, matching and templates
src/api_mock_studio/server.py  threaded HTTP server
src/api_mock_studio/cli.py     command-line interface
examples/api.json              runnable safe example
tests/test_core.py             unit and HTTP integration tests
.github/workflows/ci.yml       cross-platform CI
```

## Testing
```bash
python -m pip install .
python -m unittest discover -s tests -v
api-mock-studio examples/api.json --check
```
CI runs these checks on Python 3.10, 3.12 and 3.13 across Ubuntu, Windows and macOS.

## Security & privacy
The server binds to `127.0.0.1` by default, performs no outbound requests, collects no telemetry, and executes no code from route files. Do not place production secrets or personal data in mock configs. Binding to all interfaces can expose responses to your LAN. See [SECURITY.md](SECURITY.md).

## Limitations
This is a deterministic JSON mock server, not an OpenAPI generator, proxy, database, authentication emulator, WebSocket server, or production API gateway. Templates currently substitute path parameters only. `$echo` is intentionally simple. Config hot reload and stateful scenarios are not implemented.

## Optional roadmap
OpenAPI import, config hot reload, richer safe templating, and stateful scenarios are reasonable future additions if they can remain predictable and secure.

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md). Keep changes tested, focused, dependency-light, and documented in both languages.

## License
MIT — see [LICENSE](LICENSE).

## Author
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**

---

# العربية

## نظرة عامة
**API Mock Studio** خادم HTTP وهمي محلي خفيف مكتوب ببايثون ويعمل من ملف JSON يعرّف المسارات والاستجابات. يفيد في تطوير الواجهات، اختبارات التكامل، العروض والعمل دون اتصال عندما لا تكون الواجهة الخلفية الحقيقية جاهزة أو مناسبة للاستخدام.

## لماذا المشروع؟
قد تكون واجهة API الحقيقية غير مكتملة أو بطيئة أو محدودة الطلبات أو غير متاحة دون إنترنت. يوفر المشروع نقاط نهاية محلية حتمية وسريعة الإعداد دون أي تبعيات تشغيل خارج مكتبة بايثون القياسية.

## الميزات
- دعم GET وPOST وPUT وPATCH وDELETE وHEAD وOPTIONS.
- معاملات مسار ديناميكية مثل `/users/:id` وقوالب `{{params.id}}`.
- قراءة query string وإرجاع جسم الطلب عبر وضع `$echo` للاختبارات.
- تخصيص رمز الحالة وترويسات الاستجابة.
- محاكاة تأخير حتى 30 ثانية.
- CORS اختياري لتطوير الواجهات محليًا.
- معالجة متوازية للطلبات وحد 1 MiB لجسم الطلب ورسائل 404 بصيغة JSON.
- تحقق صارم من الإعداد ومنع تكرار المسار والطريقة.
- الاستماع على localhost افتراضيًا، بلا تتبع أو حسابات أو مفاتيح API.

## المتطلبات والتثبيت
يتطلب Python 3.10 أو أحدث.
```bash
git clone https://github.com/rad03i2/api-mock-studio.git
cd api-mock-studio
python -m pip install .
```

## الاستخدام
```bash
api-mock-studio examples/api.json --check
api-mock-studio examples/api.json --port 8080
curl http://127.0.0.1:8080/users/42
```
يمكن إضافة `--cors` عند حاجة تطبيق متصفح محلي إلى CORS. لا تستخدم `--host 0.0.0.0` إلا على شبكة موثوقة لأنه يجعل الخادم مرئيًا خارج جهازك.

## الإعداد
ملف الإعداد يحتوي مصفوفة `routes`. لكل مسار يمكن تحديد `method` و`path` و`status` و`headers` و`body` و`delay_ms`. المثال الكامل موجود في `examples/api.json`. قيمة `{"$echo":true}` تعيد الطريقة والمسار والمعاملات والاستعلام وجسم الطلب.

## بنية المشروع
`core.py` مسؤول عن التحقق والمطابقة والقوالب، و`server.py` عن خادم HTTP، و`cli.py` عن سطر الأوامر، و`tests/` عن اختبارات المنطق والتكامل، و`.github/workflows/ci.yml` عن CI متعدد الأنظمة.

## الاختبارات
```bash
python -m pip install .
python -m unittest discover -s tests -v
api-mock-studio examples/api.json --check
```
إعداد CI يشغّل الفحوص على Python 3.10 و3.12 و3.13 في Ubuntu وWindows وmacOS.

## إرشاد المعاينة
شغّل المثال والتقط صورة للطرفية تُظهر تشغيل الخادم بجانب طلب ناجح إلى `/health` و`/users/42`. لا توجد صورة ثابتة في المستودع لأن شكل الطرفية يختلف حسب النظام.

## الخصوصية والأمان
لا يجري البرنامج اتصالات صادرة ولا يجمع بيانات استخدام ولا ينفذ كودًا من ملفات الإعداد. لا تضع أسرارًا أو بيانات إنتاج حقيقية داخل ملفات mock. الخادم يستمع إلى `127.0.0.1` افتراضيًا. راجع [SECURITY.md](SECURITY.md).

## القيود
المشروع ليس مولد OpenAPI ولا proxy ولا قاعدة بيانات ولا محاكي مصادقة ولا خادم WebSocket ولا بوابة API للإنتاج. القوالب الحالية تستبدل معاملات المسار فقط، و`$echo` متعمد أن يبقى بسيطًا. لا يوجد hot reload أو سيناريوهات ذات حالة حاليًا.

## تطوير اختياري
يمكن مستقبلًا إضافة استيراد OpenAPI وإعادة تحميل الإعداد وقوالب آمنة أغنى وسيناريوهات ذات حالة، بشرط الحفاظ على البساطة والأمان.

## المساهمة والترخيص
راجع [CONTRIBUTING.md](CONTRIBUTING.md). المشروع مرخص برخصة MIT؛ راجع [LICENSE](LICENSE).

## المؤلف
**Radwan Abdulhadi Ahmed**  
**رضوان عبدالهادي أحمد**  
GitHub: **@rad03i2**
