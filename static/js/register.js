/**
 * Created by lsm on 15-4-13.
 */

Zepto(function ($) {
    $('.ui-icon-close').on('click', function () {
       $(this).prev().val('');
    });

    $('.ui-btn-primary').on('click', function () {
        var username = $('#username').val();
        if(username.length<=0){alert('请输入用户名');}
        var psw = $('#psw').val();
        if(psw.length<=0){alert('请输入密码');}
        psw = CryptoJS.SHA256(psw).toString(CryptoJS.enc.Hex); //
        var sex = $("input[name='sex']:checked").val();
        var univ_id = $('#univ').data('id');
        if(univ_id.length<=0){alert('请输入学校名');}


        $.post('/register', {email: username, password: psw, sex: sex, univ_id: univ_id}, function (res) {
            // process response
            if(res.success)window.location='/';
            else{
                alert(res.error_text);
            }
        });
    });

    $("#univ").on('input', function(){
        var name = $(this).val();
        if(name.length<=0){$('.list').empty();}
        $.post('/getuniv', {univ: name}, function (res) {
            // process response
            if(res.success){
                Change_univ_li(res.data);
            }
            else{
                alert(res.error_text);
            }
        });
    });
});

function Change_univ_li(data)
{
    $('.list').empty();
    var len = data.length;
    for(var i=0;i<len;i++){
        var item = $('<li data-id=""></li>');
        item.attr('data-id', data[i].id);
        item.text(data[i].name);
        item.on('click', function () {
            $("#univ").attr('data-id', $(this).data('id'));
            $("#univ").val($(this).text());
            $('.list').empty();
        });
        $('.list').append(item);
    }
}
