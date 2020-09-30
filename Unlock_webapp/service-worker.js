var cacheName = 'UNLOCK 4/90';
var filesToCache = [
'/',
'/login',
'/tutorial',
'/signup',
'/pickup',
'/readyforpickup',
'/hospitalinfo',
'/profile',
'/settings',
'/calendar',
'/static/css/clean-blog.css',
'/static/css/nav.css',
'/static/css/waves.css',
'/static/img/locked.svg',
'/static/img/logo.png',
'/static/img/radial-gradient.png'
]; 
self.addEventListener('install', function(e) {
e.waitUntil(
caches.open(cacheName).then(function(cache) {
return cache.addAll(filesToCache);
}).catch(reason => console.error(reason))
);
}); 
self.addEventListener('fetch', function(e) {
e.respondWith(
caches.match(e.request).then(function(response) {
return response || fetch(e.request);
}).catch(reason => console.error(reason))
);
});