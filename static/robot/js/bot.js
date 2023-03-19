function scrollDown() {
    $('#content').animate({
        scrollTop: $('#content').get(0).scrollHeight
    }, 100);
}

function controller(isOpen) {
    // 控制加载点是否显示
    if (isOpen === true) {
        $('#waiting').css("display", "block");
    } else {
        $('#waiting').css("display", "none");
    }
}

function init() {
    controller(true);
    setTimeout(function () {
        sendMsgText("你好，我是您的私人医疗问答助理");
    }, 1000);
    setTimeout(function () {
        $('#waiting').before('<div class="row message"><div class="col-md-1 image"><img src="/static/robot/img/profile.png"></div><div class="col-md-6 chattext"><div class="text">你可以这样询问我 <br>1. <a class="a-opt" onclick="aTag(this)">感冒怎么办</a> <br>2. <a class="a-opt" onclick="aTag(this)">什么人容易感冒</a><br>3. <a class="a-opt" onclick="aTag(this)">感冒吃什么药</a><br>4. <a class="a-opt" onclick="aTag(this)">感冒属于什么科</a><br>5. <a class="a-opt" onclick="aTag(this)">如何防止感冒</a><br>6. <a class="a-opt" onclick="aTag(this)">感冒要治多久</a><br>7. <a class="a-opt" onclick="aTag(this)">感冒有什么并发症</a><br>8. <a class="a-opt" onclick="aTag(this)">感冒有什么症状</a><br>9. <a class="a-opt" onclick="aTag(this)">感冒治疗几率大吗</a><br>10. <a class="a-opt" onclick="aTag(this)">感冒饮食要注意什么</a><br></div></div></div>');
    }, 1000);
    controller(false);

}

function button(item) {
    controller(true);
    intent = $(item).attr("intent");
    text = $(item).text();
    ReplyMsg(text);
    $.ajax({
        type: "POST",
        url: "/receiveBtn/",
        dataType: "json",
        data: {msg: text, intent: intent, username: "django"},
        success: function (data) {
            console.log(data);
            if (data['code'] === "200") {
                sendMsgText(data['response']);
                if (data['pic_url'] != "") {
                    sendPhoto(data['pic_url']);
                }
            }
        }

    });
    scrollDown();
    controller(false);
}

function aTag(item) {
    let text = $(item).text();
    console.log(text);
    if (text === "") return;

    controller(true);
    ReplyMsg(text);

    $.ajax({
        type: "POST",
        url: "/receiveMsg/",
        dataType: "json",
        data: {msg: text, username: "django"},
        success: function (data) {
            console.log(data);
            if (data['code'] === "200") {
                console.log(data["response"]);
                if (data['buttons'].length != 0) {
                    sendMsgBtn(data['response'], data['buttons'], data['intent']);
                } else {
                    sendMsgText(data['response']);
                }

            }
        }
    });
    controller(false);
}

function ReplyMsg(text) {
    // 把输入框内的文字输出到消息面板
    str = '<div class="row reply"><div class="col-md-1 col-md-push-11 image"><img src="/static/robot/img/user.jpg"></div><div class="col-md-6 col-md-push-4 chattext"><div class="text">' + text + '</div></div></div>';
    $("#waiting").before(str);
    $('#msgText').val("");
    scrollDown();
}

function sendMsgText(response) {
    // 机器人回复，只有文字
    str = '<div class="row message"><div class="col-md-1 image"><img src="/static/robot/img/profile.png"></div><div class="col-md-6 chattext"><div class="text">' + response + '</div></div></div>';
    $("#waiting").before(str);
    scrollDown();
}

function sendMsgBtn(response, buttons, intent) {
    // 机器人回复，有文字，有按钮
    str = '<div class="row message"><div class="col-md-1 image"><img src="/static/robot/img/profile.png"></div><div class="col-md-6 chattext"><div class="text"><div class="btn-notice">' + response + '</div><div class="btn-options">';
    $(buttons).each(function (index, element) {
        str += '<span class="btn btn-opt" onclick="button(this)" intent="' + intent + '">' + element + '</span>';
    });
    str += '</div></div></div></div>';

    $("#waiting").before(str);
    scrollDown();
}

function sendPhoto(pic_url) {
    str = '<div class="row message"><div class="col-md-1 image"><img src="/static/robot/img/profile.png"></div><div class="col-md-6 chattext"><div class="text"><img src="' + pic_url + '"></div></div></div>';
    $("#waiting").before(str);
    scrollDown();
}


$(document).ready(function () {
    // 对textarea绑定回车键
    $('#msgText').keydown(function (e) {
        if (e.keyCode === 13) {
            $('#sendBtn').click();
        }
    });

    init();

    // 发送消息
    $("#sendBtn").click(function () {
        let text = $('#msgText').val();
        if (text === "") return;

        controller(true);
        ReplyMsg(text);

        $.ajax({
            type: "POST",
            url: "/receiveMsg/",
            dataType: "json",
            data: {msg: text, username: "django"},
            success: function (data) {
                console.log(data);
                if (data['code'] === "200") {
                    console.log(data["response"]);
                    if (data['buttons'].length != 0) {
                        sendMsgBtn(data['response'], data['buttons'], data['intent']);
                    } else {
                        sendMsgText(data['response']);
                        if (data['pic_url'] != ""){
                            sendPhoto(data['pic_url']);
                        }

                    }

                }
            }
        });
        controller(false);
    });


});
