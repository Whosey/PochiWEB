# back/printer.py
import time
import hashlib
import httpx

from config import settings

# 佳博云打印接口地址（发送数据到打印机）
POS_API_URL = "https://api.poscom.cn/apisc/sendMsg"


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _build_security_code(req_time: str) -> str:
    """
    按照文档要求生成 securityCode:
    md5(memberCode + deviceID + reqTime + apiKey)
    """
    if not (settings.POS_MEMBER_CODE and settings.POS_DEVICE_ID and settings.POS_API_KEY):
        raise RuntimeError("佳博云打印未配置：请在 .env 中设置 POS_API_KEY / POS_MEMBER_CODE / POS_DEVICE_ID")
    raw = (
        settings.POS_MEMBER_CODE
        + settings.POS_DEVICE_ID
        + ""                     # msgNo 留空
        + req_time
        + settings.POS_API_KEY
    )
    return _md5(raw)




def _build_msg_detail(emotion: str, comfort: str, view_url: str) -> str:
    """
    生成佳博云打印要求的 msgDetail 字符串（mode=2，自由格式标签）。

    目标排版：
    一颗由你的情绪孕育的珍珠
    检测到的情绪：悲伤
    回信：
    你的价值从来不靠他人的眼光决定
    它藏在你仍然愿意变好的那份心里。
    [二维码]
    扫描二维码，查看你的珍珠
    """

    # 先处理安慰文案的多行情况
    comfort = (comfort or "").replace("\r\n", "\n").strip()
    comfort_lines = comfort.split("\n") if comfort else []

    # 每一行文本用 <gpWord> 包起来，避免乱码/排版问题
    def gp_word(text: str, align: int = 0, bold: int = 0, w: int = 0, h: int = 0) -> str:
        return (
            f"<gpWord Align={align} Bold={bold} Wsize={w} Hsize={h} "
            f"Reverse=0 Underline=0>{text}</gpWord>\n"
        )

    parts = []

    # 标题（居中、稍大号字体）
    parts.append(gp_word("一颗由你的情绪孕育的珍珠", align=1, bold=1, w=1, h=1))

    # 情绪行
    parts.append(gp_word(f"检测到的情绪：{emotion}", align=0, bold=0))

    # 空一行
    parts.append(gp_word("", align=0))

    # 回信标题
    parts.append(gp_word("回信：", align=0, bold=1))

    # 安慰文本，每行单独打印
    for line in comfort_lines:
        if line.strip():
            parts.append(gp_word(line.strip(), align=0))
        else:
            parts.append(gp_word("", align=0))

    # 再空一行
    parts.append(gp_word("", align=0))

    # 二维码说明文字（居中）
    parts.append(gp_word("扫描二维码，查看你的珍珠", align=1))

    # 二维码（正常方形二维码）
    # 参考官方文档：<gpQRCode Align=1 Size=8 Error=L>内容</gpQRCode>
    parts.append(f"<gpQRCode Align=1 Size=8 Error=L>{view_url}</gpQRCode>\n")

    # 自动切纸（如果你的型号支持）
    parts.append("<gpCut/>\n")

    return "".join(parts)



async def print_ticket(view_url: str, comfort: str, emotion: str) -> dict:
    """
    调用佳博云打印接口，打印二维码 + 安慰语小票。

    :param view_url:  前端页面 URL,例如 https://shell.kenxu.top/view?u=xxxx
    :param comfort:   安慰语（打印在二维码下方）
    :param emotion:  检测到的情绪，例如”悲伤”
    :return:          佳博接口返回的 JSON
    """
    req_time = str(int(time.time() * 1000))

    security_code = _build_security_code(req_time)

    req_time = str(int(time.time() * 1000))
    security_code = _build_security_code(req_time)

    # 处理多行安慰文案（换行单独打印）
    comfort = (comfort or "").replace("\r\n", "\n").strip()
    lines = comfort.split("\n") if comfort else []

    # 按你想要的样式拼接打印内容
    msg_lines = []

    # 标题
    msg_lines.append("<gpLabel>一颗由你的情绪孕育的珍珠</gpLabel>")
    # 情绪
    msg_lines.append(f"<gpLabel>检测到的情绪：{emotion}</gpLabel>")
    # 空一行
    msg_lines.append("<gpLabel> </gpLabel>")
    # 回信标题
    msg_lines.append("<gpLabel>回信：</gpLabel>")

    # 回信正文，一行一行加
    for line in lines:
        if line.strip():
            msg_lines.append(f"<gpLabel>{line.strip()}</gpLabel>")
        else:
            # 文本里本来就有空行，也保留一行空白
            msg_lines.append("<gpLabel> </gpLabel>")

    # 再空一行
    msg_lines.append("<gpLabel> </gpLabel>")
    # 二维码（内容是 view_url）
    msg_lines.append(f"<gpQRCode>{view_url}</gpQRCode>")
    # 二维码说明
    msg_lines.append("<gpLabel>扫描二维码，查看你的珍珠</gpLabel>")

    # 组合成最终 msgDetail
    msg_detail = "\n".join(msg_lines)


    payload = {
        "reqTime": req_time,
        "securityCode": security_code,
        "memberCode": settings.POS_MEMBER_CODE,
        "deviceID": settings.POS_DEVICE_ID,
        "mode": "2",         # 自定义标签模式
        "charset": "4",       # UTF-8
        "msgDetail": msg_detail,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(POS_API_URL, data=payload)
        resp.raise_for_status()
        # 返回云平台的 JSON（包含 code / msg 等）
        try:
            return resp.json()
        except Exception:
            return {"raw": resp.text}
