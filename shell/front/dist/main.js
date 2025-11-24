"use strict";
// index.html 逻辑：输入用户名后跳转到视频页
const usernameInput = document.getElementById("username");
const startBtn = document.getElementById("startBtn");
startBtn.addEventListener("click", () => {
    const name = usernameInput.value.trim();
    if (!name) {
        alert("请输入你的名字！");
        return;
    }
    window.location.href = `video.html?username=${encodeURIComponent(name)}`;
});
//# sourceMappingURL=main.js.map