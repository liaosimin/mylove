/**
 * Created by lsm on 15-4-12.
 */
Zepto(function ($) {
    $('.ui-btn-primary').on('click', function () {
        var username = $('#username').val();
        var psw = $('#psw').val();
        psw = CryptoJS.SHA256(psw).toString(CryptoJS.enc.Hex);
        $.post('/login', {email: username, password: psw}, function(res){
            if (res.success) {
                window.location='/';
            }
        });
    });
});