# دليل البدء السريع - متجر BrainSAIT
## ابدأ في 5 دقائق

مرحباً بك في متجر BrainSAIT! سيساعدك هذا الدليل على البدء بسرعة.

## 🚀 للمستخدمين النهائيين

### تصفح المنتجات

1. **زيارة المتجر**
   - اذهب إلى [https://store.brainsait.io](https://store.brainsait.io)
   - تصفح المنتجات والحلول المتاحة

2. **إنشاء حساب**
   - انقر على "تسجيل" في الزاوية العليا
   - املأ بياناتك (البريد الإلكتروني، الاسم، كلمة المرور)
   - تحقق من بريدك الإلكتروني

3. **إجراء عملية شراء**
   - اختر منتجاً
   - انقر على "أضف إلى السلة"
   - انتقل إلى الدفع
   - اختر طريقة الدفع (Stripe، PayPal، Apple Pay، مدى)
   - أكمل عملية الشراء

4. **الوصول إلى منتجاتك**
   - اذهب إلى "حسابي" ← "منتجاتي"
   - تنزيل المنتجات المشتراة
   - الوصول إلى الوثائق والدعم

### دعم اللغات

**تبديل اللغة:**
- انقر على محدد اللغة (🌐) في الزاوية العليا
- اختر بين الإنجليزية (EN) والعربية (AR)
- ستتكيف الواجهة بالكامل مع لغتك

## 💻 للمطورين

### التثبيت السريع

```bash
# استنساخ المستودع
git clone https://github.com/Fadil369/brainsait-store.git
cd brainsait-store

# تثبيت التبعيات
cd frontend && npm install
cd ../backend && pip install -r requirements.txt

# التشغيل في وضع التطوير
cd frontend && npm run dev  # الواجهة الأمامية على http://localhost:3000
cd backend && uvicorn app.main:app --reload  # الخلفية على http://localhost:8000
```

### إعداد البيئة

**الواجهة الأمامية** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_PAYPAL_CLIENT_ID=your-paypal-client-id
```

**الخلفية** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/brainsait_store
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_test_...
```

### اختبار API

```bash
# فحص الصحة
curl http://localhost:8000/health

# الحصول على المنتجات
curl http://localhost:8000/api/products

# وثائق API
open http://localhost:8000/api/docs
```

## 🔌 لمستخدمي API

### المصادقة

1. **الحصول على مفتاح API**
   - تسجيل الدخول إلى حسابك
   - اذهب إلى "الإعدادات" ← "مفاتيح API"
   - انقر على "إنشاء مفتاح جديد"
   - انسخه واحفظه بأمان

2. **إجراء استدعاءات API**

```bash
# مثال: الحصول على المنتجات
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.store.brainsait.io/api/products

# مثال: إنشاء طلب
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"product_id": "123", "quantity": 1}' \
  https://api.store.brainsait.io/api/orders
```

### وثائق API

- **الوثائق التفاعلية**: [https://api.store.brainsait.io/api/docs](https://api.store.brainsait.io/api/docs)
- **مخطط OpenAPI**: [https://api.store.brainsait.io/api/openapi.json](https://api.store.brainsait.io/api/openapi.json)
- **دليل API الكامل**: [docs/api/README.md](./api/README.md)

## 🎯 المهام الشائعة

### تغيير تفضيل اللغة

**واجهة المستخدم:**
1. انقر على محدد اللغة (🌐) في الرأس
2. اختر اللغة المفضلة (EN/AR)

**برمجياً:**
```javascript
// تعيين اللغة في localStorage
localStorage.setItem('preferred-language', 'ar');

// أو عبر رأس Accept-Language
fetch('/api/products', {
  headers: {
    'Accept-Language': 'ar'
  }
});
```

### معالجة الدفع

**Stripe:**
```javascript
const stripe = Stripe('pk_live_...');

const {error, paymentMethod} = await stripe.createPaymentMethod({
  type: 'card',
  card: cardElement,
});

if (!error) {
  // إرسال paymentMethod.id إلى الخلفية
  await fetch('/api/payments/process', {
    method: 'POST',
    body: JSON.stringify({
      payment_method: paymentMethod.id,
      amount: 9999
    })
  });
}
```

**مدى (MADA):**
```javascript
// معالجة دفع مدى
const madaPayment = {
  card_number: '5297410000000000',
  card_type: 'mada',
  amount: 99.99,
  currency: 'SAR'
};

await fetch('/api/payments/mada', {
  method: 'POST',
  body: JSON.stringify(madaPayment)
});
```

**PayPal:**
```javascript
paypal.Buttons({
  createOrder: function(data, actions) {
    return actions.order.create({
      purchase_units: [{
        amount: {value: '99.99'}
      }]
    });
  },
  onApprove: function(data, actions) {
    return actions.order.capture();
  }
}).render('#paypal-button-container');
```

### معالجة Webhooks

**Stripe Webhooks:**
```javascript
const webhook = await stripe.webhooks.constructEvent(
  request.body,
  signature,
  webhookSecret
);

switch (webhook.type) {
  case 'payment_intent.succeeded':
    // معالجة الدفع الناجح
    break;
  case 'payment_intent.failed':
    // معالجة الدفع الفاشل
    break;
}
```

## 🏢 للمستخدمين من الشركات

### إعداد نظام متعدد المستأجرين

1. **طلب حساب مستأجر**
   - الاتصال: sales@brainsait.io
   - تقديم تفاصيل الشركة
   - استلام بيانات اعتماد المستأجر

2. **تكوين المستأجر**
   - تعيين العلامة التجارية للشركة
   - تكوين SSO (SAML/OAuth)
   - إعداد أعضاء الفريق
   - تكوين الفواتير

3. **دمج الأنظمة**
   - استخدام مفاتيح API الخاصة بالمستأجر
   - تكوين webhooks
   - إعداد مزامنة البيانات
   - اختبار التكامل

### تكامل SSO

**SAML 2.0:**
```bash
# تكوين SSO في لوحة الإدارة
POST /api/admin/sso/configure
{
  "type": "saml",
  "entity_id": "https://your-idp.com/entity",
  "sso_url": "https://your-idp.com/sso",
  "certificate": "MIIDXTCCAkWgAwIBAgIJ..."
}
```

**OAuth 2.0:**
```bash
# تكوين OAuth
POST /api/admin/sso/configure
{
  "type": "oauth2",
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "authorize_url": "https://provider.com/oauth/authorize",
  "token_url": "https://provider.com/oauth/token"
}
```

## 📚 الخطوات التالية

### معرفة المزيد

- **البنية المعمارية**: [docs/architecture/README.md](./architecture/README.md)
- **مرجع API**: [docs/api/README.md](./api/README.md)
- **النشر**: [docs/deployment/README.md](./deployment/README.md)
- **التطوير**: [docs/development/README.md](./development/README.md)

### احصل على المساعدة

- **الوثائق**: [docs/README.md](./docs/README.md)
- **البريد الإلكتروني للدعم**: support@brainsait.io
- **مشكلات GitHub**: [github.com/Fadil369/brainsait-store/issues](https://github.com/Fadil369/brainsait-store/issues)

### انضم إلى المجتمع

- **Discord**: انضم إلى مجتمع المطورين
- **LinkedIn**: تابع BrainSAIT على LinkedIn
- **YouTube**: دروس فيديو وعروض توضيحية

## 🔒 أفضل ممارسات الأمان

1. **مفاتيح API**: لا تقم أبداً بإضافة مفاتيح API إلى التحكم في الإصدار
2. **HTTPS**: استخدم دائماً HTTPS في الإنتاج
3. **الأسرار**: قم بتخزين الأسرار في متغيرات البيئة
4. **المصادقة**: استخدم كلمات مرور قوية و2FA
5. **التحديثات**: حافظ على تحديث التبعيات

## 💡 نصائح وحيل

### تحسين الأداء

```javascript
// استخدام الترقيم للقوائم الكبيرة
fetch('/api/products?page=1&per_page=20');

// ذاكرة التخزين المؤقت للاستجابات
const cache = new Map();
if (cache.has(key)) {
  return cache.get(key);
}

// استخدام الضغط
headers: {
  'Accept-Encoding': 'gzip, deflate, br'
}
```

### معالجة الأخطاء

```javascript
try {
  const response = await fetch('/api/products');
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  console.error('فشل في جلب المنتجات:', error);
  // إظهار رسالة خطأ سهلة الاستخدام
}
```

### الاختبار

```bash
# تشغيل اختبارات الواجهة الأمامية
cd frontend && npm test

# تشغيل اختبارات الخلفية
cd backend && pytest

# تشغيل اختبارات E2E
cd frontend && npm run test:e2e
```

## 🎓 دروس تعليمية

### الدرس 1: إنشاء أول تكامل لك

1. إنشاء مفتاح API
2. إجراء استدعاء API تجريبي
3. معالجة المصادقة
4. معالجة أحداث webhook
5. النشر في الإنتاج

**الوقت المقدر**: 30 دقيقة

### الدرس 2: بناء متجر مخصص

1. استنساخ المستودع
2. تخصيص العلامة التجارية
3. إضافة منتجات مخصصة
4. تكوين بوابات الدفع
5. النشر على Cloudflare

**الوقت المقدر**: ساعتان

### الدرس 3: دعم متعدد اللغات

1. إضافة ملفات الترجمة
2. تكوين i18n
3. اختبار تخطيط RTL
4. نشر موقع ثنائي اللغة

**الوقت المقدر**: ساعة واحدة

## 📞 الدعم

### هل تحتاج إلى مساعدة؟

**روابط سريعة:**
- [الأسئلة الشائعة](./docs/FAQ.md)
- [استكشاف الأخطاء وإصلاحها](./docs/deployment/TROUBLESHOOTING.md)
- [حالة API](https://status.brainsait.io)

**الاتصال:**
- **عام**: support@brainsait.io
- **المبيعات**: sales@brainsait.io
- **الأمان**: security@brainsait.io
- **الطوارئ**: متاح 24/7 للمشكلات الحرجة

## 🇸🇦 دعم السوق السعودي

### بوابات الدفع السعودية

**مدى (MADA):**
- دعم كامل لبطاقات مدى
- معالجة الدفع المحلية
- امتثال للمعايير السعودية

**STC Pay:**
- التكامل مع STC Pay
- دفع سريع وآمن
- دعم المحافظ الرقمية

**الامتثال ZATCA:**
- الفواتير الإلكترونية
- الامتثال للوائح الضريبية
- تقارير آلية

### العملة والتسعير

```javascript
// جميع الأسعار تدعم الريال السعودي
const pricing = {
  amount: 99.99,
  currency: 'SAR',
  locale: 'ar-SA'
};

// تنسيق العملة
const formatted = new Intl.NumberFormat('ar-SA', {
  style: 'currency',
  currency: 'SAR'
}).format(99.99);
// النتيجة: "٩٩٫٩٩ ر.س."
```

---

**إصدار المستند**: 1.0.0  
**آخر تحديث**: يناير 2025  
**اللغة**: العربية | [English](./QUICKSTART.md)
