$(document).ready(function() {
  $("*").on("click",function(){
    var r = Math.floor((Math.random() * 200) + 1);
    if (r === 100) {
        console.log('TRIGGERED');
      //window.open('www.yourdomain.com','_blank');
    }
  });
});
