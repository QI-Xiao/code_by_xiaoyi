
$(document).ready(function () {
    function refresh() {
        $.getJSON("/display/", function (ret) {
             $('#result').html(ret.ph1);
             $('#result2').html(ret.ph2);
        })
    }

    setInterval(refresh, 3000)
})
