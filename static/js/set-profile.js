/**
 * Created by lsm on 15-4-7.
 */
Zepto(function($){
    $('.info-con').on('click',function(){$(this).siblings('.info-edit').toggle();});

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
        var action = evt.data("action");
        var data;
        switch(action)
        {
            case 'edit_nickname':
                data = $('#nicknameEdit').val().trim();
                break;
            case 'edit_realname':
                data = $('#realname').val().trim();
                break;
            case 'edit_wx_username':
                data = $('#wx_username').val().trim();
                break;
            case 'edit_birthday':
                var regYear=/^(?!0000)[0-9]{4}$/;
                var regMonth=/^(0?[1-9]|[1][012])$/;
                var year = $('#year').val().trim();
                var month = $('#month').val().trim();
                if(!regMonth.test(month)||!regYear.test(year)||!month || !year)
                {
                    $.tips({content:'请输入正确的年月!',stayTime:3000,type:"warn"});
                }
                else
                {
                    data=JSON.stringify({"year":year,"month":month});
                }
                break;
            case 'edit_height':
                data = $('#height').val().trim();
                break;
            case 'edit_weight':
                data = $('#weight').val().trim();
                break;
            case 'edit_intro':
                data = $('#intro').val().trim();
                break;
        }

        var args={'action': action, 'data': data};
        $.post('/setprofile', args, function(res){
          // process response
            if (res.success) {
                evt.parents('li').find('a.editInfo').text(data).css({'color': '#a8a8a8'});
                $.tips({content: '修改成功!', stayTime: 3000, type: "info"});
            }
            else{
                $.tips({content: res.error_text, stayTime: 3000, type: "info"});
            }
        });
    });
}