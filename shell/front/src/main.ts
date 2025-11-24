// src/main.ts

const usernameInput = document.getElementById("username") as HTMLInputElement | null;
const startBtn = document.getElementById("startBtn") as HTMLButtonElement | null;

if (startBtn && usernameInput) {
  startBtn.addEventListener("click", async () => {
    const username = usernameInput.value.trim();
    if (!username) {
      alert("请先输入你的名字。");
      return;
    }

    try {
      // ============================
      // 1. 第一步：图像 → prompt
      // ============================

      // TODO：这里 imgurl 改成真实的纸条图像地址（例如相机上传后的 URL）
      // 暂时用占位符
      const imageUrl = "http://your-device/uploaded_note.jpg";

      const resp1 = await fetch("http://你的服务器地址/api/img2text", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username,
          imgurl: imageUrl
        })
      });

      if (!resp1.ok) {
        throw new Error("图像识别失败");
      }

      const data1 = await resp1.json();
      const prompt = data1.prompt;


      // ============================
      // 2. 第二步：prompt → 珍珠图片
      // ============================

      const resp2 = await fetch("http://你的服务器地址/api/generate_pearl", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          prompt,
          username
        })
      });

      if (!resp2.ok) {
        throw new Error("珍珠生成失败");
      }

      const data2 = await resp2.json();
      const imgUrl = data2.img_url;  // 例如 "/static/pearls/xxxx.jpg"


      // ============================
      // 3. 生成一条 comfort 文案（你可以先写死，后续再让后端生成）
      // ============================

      const comfort = encodeURIComponent("愿你在波折中依旧保持柔软与力量");


      // ============================
      // 4. 跳转到 video.html
      // ============================

      const params = new URLSearchParams();
      params.set("username", username);
      params.set("img_url", imgUrl);
      params.set("comfort", comfort);

      window.location.href = `video.html?${params.toString()}`;

    } catch(err) {
      console.error(err);
      alert("生成珍珠失败，请稍后再试。");
    }
  });
}
