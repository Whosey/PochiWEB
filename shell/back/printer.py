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

    目标排版（和你截图接近）：
    ————————————————
    一颗由你的情绪孕育的珍珠         （居中）
    检测到的情绪：悲伤                （左对齐）
    回信：                            （左对齐，下面是多行安慰语）

      这里是安慰语第一行
      这里是安慰语第二行

                  [二维码居中]
          扫描二维码，查看你的珍珠
    """

    # 处理安慰文案的多行情况
    comfort = (comfort or "").replace("\r\n", "\n").strip()
    comfort_lines = comfort.split("\n") if comfort else []

    # 每一行文本用 <gpWord> 包起来，方便控制对齐/加粗/大小
    def gp_word(text: str, align: int = 0, bold: int = 0, w: int = 0, h: int = 0) -> str:
        return (
            f"<gpWord Align={align} Bold={bold} Wsize={w} Hsize={h} "
            f"Reverse=0 Underline=0>{text}</gpWord>\n"
        )

    parts: list[str] = []

    # 顶部横线（用一行长破折号模拟）
    parts.append(gp_word("——————————————", align=1))

    # 标题（居中、稍大一号、加粗）
    parts.append(gp_word("一颗由你的情绪孕育的珍珠", align=1, bold=1, w=1, h=1))

    # 空一行
    parts.append(gp_word("", align=0))

    # 情绪行
    parts.append(gp_word(f"检测到的情绪：{emotion}", align=0))

    # 空一行
    parts.append(gp_word("", align=0))

    # 回信标题
    parts.append(gp_word("回信：", align=0, bold=1))

    # 安慰文本，每行前面加两个空格做缩进
    for line in comfort_lines:
        if line.strip():
            parts.append(gp_word("  " + line.strip(), align=0))
        else:
            parts.append(gp_word("", align=0))

    # 空两行，然后打印二维码
    parts.append(gp_word("", align=0))
    parts.append(gp_word("", align=0))

    # 二维码（居中）
    parts.append(f"<gpQRCode Align=1 Size=6 Error=L>{view_url}</gpQRCode>\n")

    # 二维码下方说明文字（居中）
    parts.append(gp_word("扫描二维码，查看你的珍珠", align=1))

    # 自动切纸（如果你的型号支持）
    parts.append("<gpCut/>\n")

    return "".join(parts)




async def print_ticket(view_url: str, emotion: str, comfort: str) -> dict:
    """
    调用佳博云打印接口，打印「情绪 + 回信 + 二维码」小票。

    :param view_url:  前端页面 URL, 例如 https://shell.kenxu.top/view?u=xxxx
    :param emotion:   检测到的情绪，例如 "悲伤"
    :param comfort:   回信文案（可以多行）
    :return:          佳博接口返回的 JSON
    """
    req_time = str(int(time.time() * 1000))
    security_code = _build_security_code(req_time)

    # 用上面那个函数生成整张小票的内容
    msg_detail = _build_msg_detail(emotion=emotion, comfort=comfort, view_url=view_url)

    payload = {
        "reqTime": req_time,
        "securityCode": security_code,
        "memberCode": settings.POS_MEMBER_CODE,
        "deviceID": settings.POS_DEVICE_ID,
        "mode": "2",          # 自定义标签模式
        "charset": "4",       # UTF-8
        "msgDetail": msg_detail,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(POS_API_URL, data=payload)
        resp.raise_for_status()
        try:
            return resp.json()
        except Exception:
            return {"raw": resp.text}

