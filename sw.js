/* 侍酒師學院 · 離線快取
   改版後請把下方 VERSION 加一，否則使用者會一直看到舊版。 */
const VERSION = "1.0.1";
const CACHE = "somm-academy-" + VERSION;
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./icon-192.png", "./icon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);

  // 排行榜請求一律走網路，不快取
  if (url.hostname.indexOf("script.google") >= 0) return;

  // 語音檔：快取優先（檔案不會變動），第一次下載後永久離線可用
  if (url.pathname.indexOf("/voice/") >= 0) {
    e.respondWith(caches.open(CACHE).then(c =>
      c.match(e.request).then(hit => hit || fetch(e.request).then(r => {
        if (r.ok) c.put(e.request, r.clone());
        return r;
      }))));
    return;
  }

  // 其餘：網路優先、失敗回快取，確保改版能即時生效
  e.respondWith(
    fetch(e.request).then(r => {
      if (r.ok && e.request.method === "GET") {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return r;
    }).catch(() => caches.match(e.request).then(hit => hit || caches.match("./index.html")))
  );
});
