// ================================================
// result.ts
// 结果页前端逻辑：只负责读取 URL 参数并更新 UI
// 不在浏览器里调用任何 AI 接口，也不放 API Key
// ================================================

// 元素获取（注意要和 result.html 里的 id 对应）
const pearlImage = document.getElementById("pearl-image") as HTMLImageElement | null;
const responseText = document.getElementById("response-text") as HTMLElement | null;
const emotionText = document.getElementById("emotion-text") as HTMLElement | null; // 如果没有这个元素，可以删掉这行和下面相关逻辑
const downloadBtn = document.getElementById("downloadBtn") as HTMLButtonElement | null;
const popup = document.getElementById("popup") as HTMLElement | null;

// 从 URL 中读取参数并更新页面内容
function loadPearlResult(): void {
  const params = new URLSearchParams(window.location.search);

  const imgUrl = params.get("img_url");
  const comfort = params.get("comfort");
  const emotion = params.get("emotion");
  const username = params.get("username");

  // 设置珍珠图片
  if (pearlImage) {
    if (imgUrl) {
      pearlImage.src = imgUrl;
    } else {
      // 没有传 img_url 就用一张默认图（可以改成你自己的）
      pearlImage.src = "/static/pearls/demo.jpg";
    }
  }

  // 设置文案
  if (responseText) {
    let text = "";

    if (username) {
      text += `${username}，\n`;
    }

    if (comfort) {
      text += comfort;
    } else {
      text += "谢谢你把心情写下来，这里是一颗为你生成的珍珠。";
    }

    responseText.textContent = text;
  }

  // 设置“检测到的情绪：xxx”
  if (emotionText && emotion) {
    emotionText.textContent = `检测到的情绪：${emotion}`;
  }
}

// 下载按钮 -> 显示“长按保存”弹窗
function setupDownloadPopup(): void {
  if (!downloadBtn || !popup) return;

  downloadBtn.addEventListener("click", () => {
    popup.classList.remove("hidden");

    // 2 秒后自动隐藏
    setTimeout(() => {
      popup.classList.add("hidden");
    }, 2000);
  });
}

// =============================
// 启动逻辑
// =============================
document.addEventListener("DOMContentLoaded", () => {
  loadPearlResult();
  setupDownloadPopup();
});
