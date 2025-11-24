"use strict";
// ================================================
// result.ts
// TypeScript 实现：情绪珍珠前端逻辑（异步AI调用版）
// ================================================
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
// 元素获取
const pearlImage = document.getElementById("pearl-image");
const responseText = document.getElementById("response-text");
const downloadBtn = document.getElementById("downloadBtn");
const popup = document.getElementById("popup");
const closePopup = document.getElementById("closePopup");
// API Keys（⚠️ 开发阶段使用，部署时请改为后端代理）
const GLM_API_KEY = "8b3f6c581c26415a8b14f9486dc324fa.jWpjkDN97CHNRWoX";
const SILICON_API_KEY = "sk-xrmedevcpxynmdctolizaolsbxxqzsrkeumqupaixxwxkapi";
// =============================
// 异步函数：调用AI模型生成提示词
// 支持两种模式：
// "qwen"  → Qwen3-VL-8B-Instruct
// "glm+deepseek" → GLM-4v-flash + DeepSeek
// =============================
function getPromptFromAI(imageUrl_1) {
    return __awaiter(this, arguments, void 0, function* (imageUrl, mode = "qwen") {
        var _a, _b, _c, _d, _e, _f, _g, _h, _j;
        try {
            if (mode === "qwen") {
                // ========== 方案一：Qwen3-VL 一步识别+生成 ==========
                const qwenResp = yield fetch("https://api.siliconflow.cn/v1/chat/completions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${SILICON_API_KEY}`
                    },
                    body: JSON.stringify({
                        model: "Qwen/Qwen2-VL-7B-Instruct",
                        messages: [
                            {
                                role: "user",
                                content: [
                                    {
                                        type: "text",
                                        text: "读取图片中的文字，理解文字中蕴含的情绪，用英文生成能够展现这一情绪的珍珠的设计描述性文字，细节详细。"
                                    },
                                    { type: "image_url", image_url: imageUrl }
                                ]
                            }
                        ]
                    })
                });
                const qwenData = yield qwenResp.json();
                const resultText = ((_c = (_b = (_a = qwenData === null || qwenData === void 0 ? void 0 : qwenData.choices) === null || _a === void 0 ? void 0 : _a[0]) === null || _b === void 0 ? void 0 : _b.message) === null || _c === void 0 ? void 0 : _c.content) || "";
                return resultText || "A soft glowing pearl representing calm emotion.";
            }
            else {
                // ========== 方案二：GLM4v + DeepSeek ==========
                // Step 1️⃣：GLM4v 识别文字
                const glmResp = yield fetch("https://open.bigmodel.cn/api/paas/v4/chat/completions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${GLM_API_KEY}`
                    },
                    body: JSON.stringify({
                        model: "glm-4v-flash",
                        messages: [
                            {
                                role: "user",
                                content: [
                                    { type: "text", text: "识别图片中的手写文字，只输出文字内容，不解释。" },
                                    { type: "image_url", image_url: imageUrl }
                                ]
                            }
                        ]
                    })
                });
                const glmData = yield glmResp.json();
                const recognizedText = ((_f = (_e = (_d = glmData === null || glmData === void 0 ? void 0 : glmData.choices) === null || _d === void 0 ? void 0 : _d[0]) === null || _e === void 0 ? void 0 : _e.message) === null || _f === void 0 ? void 0 : _f.content) || "";
                // Step 2️⃣：DeepSeek 根据文字生成提示词
                const deepResp = yield fetch("https://api.siliconflow.cn/v1/chat/completions", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${SILICON_API_KEY}`
                    },
                    body: JSON.stringify({
                        model: "deepseek-ai/deepseek-coder-v2-lite-instruct",
                        messages: [
                            {
                                role: "user",
                                content: `The user wrote: "${recognizedText}". Please describe a pearl image that represents the emotion in this text. Use detailed English descriptions.`
                            }
                        ]
                    })
                });
                const deepData = yield deepResp.json();
                const finalPrompt = ((_j = (_h = (_g = deepData === null || deepData === void 0 ? void 0 : deepData.choices) === null || _g === void 0 ? void 0 : _g[0]) === null || _h === void 0 ? void 0 : _h.message) === null || _j === void 0 ? void 0 : _j.content) || "";
                return finalPrompt || "A glowing pearl with gentle colors reflecting sadness.";
            }
        }
        catch (error) {
            console.error("AI调用失败:", error);
            return "A mysterious pearl radiating quiet emotion.";
        }
    });
}
// =============================
// 主函数：加载珍珠结果并更新UI
// =============================
function loadPearlResult() {
    return __awaiter(this, void 0, void 0, function* () {
        responseText.textContent = "🧠 正在识别文字并生成珍珠...";
        const imageUrl = "https://shell.kenxu.top/uploads/latest_paper.jpg"; // 从后端获得图片URL
        // 调用AI生成提示词（你可以切换模式："qwen" / "glm+deepseek"）
        const prompt = yield getPromptFromAI(imageUrl, "glm+deepseek");
        // 调用后端生成珍珠图像
        const genResp = yield fetch("https://shell.kenxu.top/api/generate_pearl", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt })
        });
        const genData = yield genResp.json();
        // 更新页面内容
        pearlImage.src = genData.pearlImageUrl;
        responseText.textContent = genData.comfortText || "✨ 你的珍珠已经准备好啦！";
    });
}
// 调用主函数
loadPearlResult();
// =============================
// 下载弹窗交互逻辑
// =============================
downloadBtn.addEventListener("click", () => {
    popup.classList.remove("hidden");
    // 2 秒后自动隐藏
    setTimeout(() => {
        popup.classList.add("hidden");
    }, 2000);
});
//# sourceMappingURL=result.js.map