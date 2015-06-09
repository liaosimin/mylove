/**
 * Created by lsm on 15-4-23.
 */
var timer_id;
var socket;
var self_msg;
if (!window.WebSocket) {
    window.WebSocket = window.MozWebSocket;
}
// Javascript Websocket Client
if (window.WebSocket) {
    socket = new WebSocket("ws://mt01.monklof.com:8887/websocket");
    socket.onmessage = function (event) {
        var receive_msg = JSON.parse(event.data);
        switch(receive_msg.type){
            case 0:
                var buddy = '<div class="chat_content_group "><p class="chat_nick">'+receive_msg.nickname+
                    '</p><p class="chat_content ">'+receive_msg.msg+'</p></div>';
                $('.chat_group').append(buddy);
                break;
            case 1:  //keep waiting
                break;
            case 2:  //stop waiting
                //self.clearInterval(timer_id);
                $('.chat_group').empty();
                append_server_msg('切换成功，新聊天对象为：'+receive_msg.nickname);
                break;
            case 3:  //close
            case 4:  //link
            case 10:  //error
                append_server_msg(receive_msg.msg);
                break;
        }
    };
    socket.onopen = function (event) {
        //var ta = document.getElementById('responseText');
        //ta.value = "Web Socket opened!";
        console.log('websocket open')
    };
    socket.onclose = function (event) {
        //var ta = document.getElementById('responseText');
        //ta.value = ta.value + "Web Socket closed";
        console.log('websocket close')
    };
} else {
    alert("Your browser does not support Web Socket.");
}
// Send Websocket data
function send() {
    if (!window.WebSocket) {
        return;
    }
    if (socket.readyState != WebSocket.OPEN) {
        alert("The socket is not open.");
        return
    }
    var message = $('textarea').val();
    if(message == "")return;
    var msg = {'type': 0, 'msg': message};
    var json = JSON.stringify(msg);
    socket.send(json);
    $('textarea').val('');
    self_msg = message;
    var self = '<div class="chat_content_group_self "><p class="chat_nick">me</p><p class="chat_content self">'+self_msg+'</p></div>';
    $('.chat_group').append(self);
}

function changePeople() {
    if (!window.WebSocket) {
        return;
    }
    if (socket.readyState == WebSocket.OPEN) {
        var msg = {'type': 1, 'msg': 'change people'};
        var json = JSON.stringify(msg);
        socket.send(json);
    } else {
        alert("The socket is not open.");
    }
}

function append_server_msg(msg)
{
    var buddy = '<div class="server">'+msg+'</div>';
    $('.chat_group').append(buddy);
}
