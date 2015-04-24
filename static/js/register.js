/**
 * Created by lsm on 15-4-13.
 */

Zepto(function ($) {
    $('.ui-btn-primary').on('click', function () {
        var username = $('#username').val();
        var psw = $('#psw').val();
        psw = CryptoJS.SHA256(psw).toString(CryptoJS.enc.Hex); //
        sex = $("input[name='sex']:checked").val();

        $.post('/register', {email: username, password: psw, sex:sex}, function (res) {
            // process response
            window.location='/';
        });
    });
});

