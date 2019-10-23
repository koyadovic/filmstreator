window.isMobilePhone = function() {
  var check = false;
  return (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))) check = true;})(navigator.userAgent||navigator.vendor||window.opera);
  console.log('Is mobile phone: ' + check);
  return check;
};
window.isRobot = function() {
  var check = false;
  if (/bot|google|baidu|bing|msn|duckduckbot|teoma|slurp|yandex/i.test(navigator.userAgent)) {
    check = true;
  }
  return check;
};
var yall=function(){"use strict";return function(e){var n=(e=e||{}).lazyClass||"lazy",t=e.lazyBackgroundClass||"lazy-bg",o="idleLoadTimeout"in e?e.idleLoadTimeout:200,r=e.observeChanges||!1,i=e.events||{},a=window,s="requestIdleCallback",c="IntersectionObserver",u=["srcset","src","poster"],d=[],l=function(e,o){return d.slice.call((o||document).querySelectorAll(e||"img."+n+",video."+n+",iframe."+n+",."+t))},f=function(n){var o,r,i=n.parentNode;for(var a in"PICTURE"==i.nodeName&&(r=i),"VIDEO"==n.nodeName&&(r=n),o=l("source",r))b(o[a]);b(n),n.autoplay&&n.load();var s=n.classList;s.contains(t)&&(s.remove(t),s.add(e.lazyBackgroundLoaded||"lazy-bg-loaded"))},v=function(e){for(var n in i)e.addEventListener(n,i[n].listener||i[n],i[n].options||void 0);y.observe(e)},b=function(e){u.forEach(function(n){n in e.dataset&&a.requestAnimationFrame(function(){e[n]=e.dataset[n]})})},g=l();if(/baidu|(?:google|bing|yandex|duckduck)bot/i.test(navigator.userAgent))for(var m in g)f(g[m]);else if(c in a&&c+"Entry"in a&&"isIntersecting"in a[c+"Entry"].prototype){var y=new a[c](function(e,t){e.forEach(function(e){if(e.isIntersecting){var i=e.target;s in a&&o?a[s](function(){f(i)},{timeout:o}):f(i),i.classList.remove(n),t.unobserve(i),(g=g.filter(function(e){return e!=i})).length||r||y.disconnect()}})},{rootMargin:("threshold"in e?e.threshold:200)+"px 0%"});for(var h in g)v(g[h]);r&&new MutationObserver(function(){l().forEach(function(e){g.indexOf(e)<0&&(g.push(e),v(e))})}).observe(l(e.observeRootSelector||"body")[0],e.mutationObserverOptions||{childList:!0,subtree:!0})}}}();
document.addEventListener("DOMContentLoaded", yall);
var lastHeight = null;
function adjustBodyPadding() {
  var height = $('nav.notbody').height();
  if(!lastHeight || lastHeight != height) {
    lastHeight = height;
    $('body').css({'padding-top': height});
  }
  setTimeout(adjustBodyPadding, 100);
}
adjustBodyPadding();

$(document).ready(function() {
    var hamburguer = document.getElementById("hidden-sidebar-hamburger");
    var isPhone = getComputedStyle(hamburguer, null).display != "none";
    if(isPhone) {
        new Hammer(document.getElementById('sidebar')).on("swipeleft", function(ev) {
            if (ev.type == 'swipeleft') $('nav.sidebar').css('left', '-20em');
        });
        new Hammer(document.getElementById('content')).on("swipeleft swiperight", function(ev) {
            if (ev.type == 'swiperight') $('nav.sidebar').css('left', '0px');
            else if (ev.type == 'swipeleft') $('nav.sidebar').css('left', '-20em');
        });
        document.getElementById('content').addEventListener('click', function (event) {
            var current = $('nav.sidebar').css('left');
            if (current == "0px") $('nav.sidebar').css('left', '-20em');
        });
    }
});
function toggleNav() {
    var current = $('nav.sidebar').css('left');
    if (current == "0px") $('nav.sidebar').css('left', '-20em'); else $('nav.sidebar').css('left', '0px');
}
