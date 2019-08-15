$(document).ready(function() {
  $("*").on("click",function(){
    var r = Math.floor((Math.random() * 200) + 1);
    if (r === 100) {
      window.open('http://deloplen.com/afu.php?zoneid=2772265','_blank');
    }
  });
});
