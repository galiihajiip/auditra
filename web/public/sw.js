const CACHE = "auditra-v5";
const PRECACHE = [
  "/",
  "/index.html",
  "/favicon.ico",
  "/favicon.svg",
  "/favicon-32.png",
  "/logo.png",
  "/logo-icon.png",
  "/logo-header.png",
  "/logo-header@2x.png",
  "/manifest.webmanifest",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)).then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});
