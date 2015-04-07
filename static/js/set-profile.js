/**
 * Created by lsm on 15-4-7.
 */
Zepto(function($){
    $('.editInfo').on('click',function(){$(this).parents('.info-con').siblings('.info-edit').toggle();});

    $('a.editInfo').each(function(){
        if($(this).text() =='None'||$(this).text() =='')
        {$(this).text('点击设置').css({'color':'#FF3C3C'});}  //todo: the color is wrong,why?
    });

    //the cancel btn
    $('.info-edit').find('.concel-btn').each(function(){
        $(this).on('click',function(){$(this).parents('.info-edit').hide();})
    });

    //the ok btn
    $('.info-edit').find('.sure-btn').each(function(){infoEdit($(this))});
});


function infoEdit(evt){
    evt.on('click',function(){
        var nickname = $('#nicknameEdit').val();

        $.post('/setprofile', { nickname: nickname }, function(response){
          // process response
            alert(response.success);
        });
        //var email=$('#mailEdit').val().trim();
        //var year=$('#yearEdit').val().trim();
        //var month=$('#monthEdit').val().trim();
        //var sex=$('#sexEdit option:selected').data('sex');
        //var realname=$('#realnameEdit').val();
        //var regEmail=/^([a-zA-Z0-9]*[-_]?[a-zA-Z0-9]+)*@([a-zA-Z0-9]*[-_]?[a-zA-Z0-9]+)+[\.][a-z]{2,3}([\.][a-z]{2})?$/;
        //var regNumber=/^[0-9]*[1-9][0-9]*$/;
        //var regYear=/^(?!0000)[0-9]{4}$/;
        //var regMonth=/^(0?[1-9]|[1][012])$/;
        //var action=evt.data('action');
        //var data=evt.parents('.info-edit').find('.edit-box').val();
        //// action 不要放在html里面
        //if(action=='edit_email' && !regEmail.test(email))
        //{return alert("邮箱不存在!");}
        //else if(action=='edit_sex')
        //{data=sex;}
        //else if(action=='edit_birthday')
        //{
        //    if(!regMonth.test(month)||!regYear.test(year)||!month || !year)
        //        return alert("请输入正确的年月!");
        //    else
        //    {
        //        data={
        //            year:$('#yearEdit').val().trim(),
        //            month:$('#monthEdit').val().trim()
        //        }
        //    }
        //}
        //var url="/fruitzone/admin/profile";
        //var args={action: action, data: data};
        //$.postJson(url,args,
        //    function (res) {
        //        if (res.success) {
        //            evt.parents('li').find('a.editInfo').text(data).css({'color':'#a8a8a8'});
        //            evt.parents('li').find('#userBirthday').text(data.year+'-'+data.month).css({'color':'#a8a8a8'});
        //            if(data==''){evt.parents('li').find('.editInfo').text('点击设置').css({'color':'#FF3C3C'});}
        //            if(data=='0'){$('#userSex').text('其他');}
        //            else if(data=='1'){$('#userSex').text('男');}
        //            else if(data=='2'){$('#userSex').text('女');}
        //            evt.parents('li').find('.info-edit').hide();
        //            $('#serSex').attr({'data-sex':data});
        //        }
        //        else alert(res.error_text);
        //    },
        //    function(){
        //        alert('网络错误！');}
        //);
    });
}