/**
 * Created by lsm on 15-4-25.
 */
Zepto(function ($) {
  //var item = $('.wrapper').html();
  //  $('.wrapper').empty();
get_data(0);
});
function get_data(page){
    $.get('/photo?page='+page, function(res){
        if(res.success){append_items(res.data);}
        else{alert('error');}
    })
}


function append_items(data)
{
    var len = data.length;
    for(var i=0;i<len;i++){
        var avatar_url = 'http://7xit5j.com1.z0.glb.clouddn.com/' + data[i].avatar_url;
        var img_url = 'http://7xitqn.com1.z0.glb.clouddn.com/' + data[i].img_url;
        var sex = '&#xe71a';
        if (data.sex == 1)sex='&#xe71a';
        var lable = '';
        for(var j=0;j<data[i].info_label.length;j++){
            lable += '<span class="info_label">'+ data[i].info_label[j] +'</span>';
        }
        var item = '<div class="item"><div class="item_head"><a href="#"><img src="' +
            avatar_url +
            '" alt="hello" class="avatar"/></a><span class="nickname">' +
            data[i].nickname +
            '</span><span><i class="iconfont woman">' +
            sex +
            '</i></span><span class="creat_time">' +
            data[i].time +
            '</span></div><div class="photo"><img src="' +
            img_url +
            '"></div><div class="profile">'+
            lable+
            '</div><p class="intro">' +
            data[i].intro +
            '</p></div>';
        $('.wrapper').append(item);
    }
    if(len<10)return false;
    else return true;
}