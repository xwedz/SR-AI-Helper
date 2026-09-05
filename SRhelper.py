from openai import OpenAI
import requests
import gradio as gr
from bs4 import BeautifulSoup
from groq import Groq
import os
from google.colab import userdata
from opencc import OpenCC
"""#2.讀取API資料"""

GROQ_API_KEY = userdata.get('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"



"""#3.儲存各項變數和名稱資料"""

# 可選欄位
available_fields = [
    ("遺器、飾品搭配", "套装推荐理由"),
    ("主詞條推薦", "主词条推荐"),
    ("副詞條推薦", "副词条推荐"),
    ("詞條推薦理由", "词条推荐理由"),
    ("畢業光錐", "毕业光锥"),
    ("可選光錐", "可选光锥"),
]


character_map = {
    "克拉拉": "克拉拉",
    "丹恆": "丹恒",
    "景元": "景元",
    "符玄": "符玄",
    "銀狼": "银狼",
    "風堇": "风堇",
    "停雲": "停云",
    "三月七": "三月七",
    "姬子": "姬子",
    "瓦爾特": "瓦尔特",
    "帕姆": "帕姆",
    "卡芙卡": "卡芙卡",
    "刃": "刃",
    "流螢": "流萤",
    "艾利歐": "艾利欧",
    "彥卿": "彦卿",
    "鏡流": "镜流",
    "雲璃": "云璃",
    "飛霄": "飞霄",
    "靈砂": "灵砂",
    "希兒": "希儿",
    "布洛妮婭": "布洛妮娅",
    "傑帕德": "杰帕德",
    "白露": "白露",
    "羅剎": "罗刹",
    "丹恆·飲月": "丹恒·饮月",
    "托帕&帳帳": "托帕&账账",
    "霍霍": "藿藿",
    "銀枝": "银枝",
    "阮·梅": "阮·梅",
    "真理醫生": "真理医生",
    "黑天鵝": "黑天鹅",
    "花火": "花火",
    "黃泉": "黄泉",
    "砂金": "砂金",
    "波提歐": "波提欧",
    "知更鳥": "知更鸟",
    "翡翠": "翡翠",
    "椒丘": "椒丘",
    "亂破": "乱破",
    "星期日": "星期日",
    "忘歸人": "忘归人",
    "素裳": "素裳",
    "青雀": "青雀",
    "黑塔": "黑塔",
    "艾絲妲": "艾丝妲",
    "佩拉": "佩拉",
    "虎克": "虎克",
    "桑博": "桑博",
    "阿蘭": "阿兰",
    "希露瓦": "希露瓦",
    "雪衣": "雪衣",
    "娜塔莎": "娜塔莎",
    "盧卡": "卢卡",
    "加拉赫": "加拉赫",
    "開拓者·存護": "开拓者·存护",
    "開拓者•同諧": "开拓者•同谐",
    "開拓者•記憶": "开拓者•记忆",
    "開拓者·毀滅": "开拓者·毁灭",
    "玲可": "玲可",
    "寒鴉": "寒鸦",
    "桂乃芬": "桂乃芬",
    "米莎": "米莎",
    "馭空": "驭空",
    "缇寶": "缇宝",
    "阿格萊雅": "阿格莱雅",
    "萬敵": "万敌",
    "貊澤": "貊泽",
    "大黑塔": "大黑塔",
    "那刻夏": "那刻夏",
    "米莎": "米沙",
    "遐蝶": "遐蝶"
}

# 問題類別同義詞映射
question_type_map = {
    "主詞條推薦": ["主詞條", "主屬性", "主屬", "主要詞條", "主屬項"],
    "副詞條推薦": ["副詞條", "副屬性", "副屬", "副屬項"],
    "遺器、飾品搭配": ["套裝", "套裝推薦", "遺器", "聖遺物", "儀器"],
    "畢業光錐": ["畢業光錐", "最佳光錐", "最強光錐", "首選光錐"],
    "可選光錐": ["可選光錐", "其他光錐", "替代光錐", "平替光錐"]
}

#角色模糊搜尋
character_name_map = {
    "開拓者·存護": ["開拓者存護", "存護主", "存護開拓者"],
    "開拓者·記憶": ["開拓者記憶", "記憶主", "記憶開拓者"],
    "開拓者·毀滅": ["開拓者毀滅", "毀滅主", "毀滅開拓者"],
    "丹恆·飲月": ["丹恆飲月","飲月丹恆"],
    "阮·梅": ["阮梅"]
}

cc = OpenCC('s2t')

import re

"""#4.重點爬蟲及搜尋功能"""

def fetch_specific_section(character_name, section_title):
    base_url = "https://wiki.biligame.com/sr/"
    url = base_url + character_name
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        if res.status_code != 200:
            return f"<p style='color: red;'>❌ 找不到角色頁面：{url}</p>"

        soup = BeautifulSoup(res.text, "html.parser")

        # 將所有連結變黃色
        for a in soup.find_all("a"):
            a.attrs.pop("href", None)  # 移除超連結功能
            a['style'] = "color: yellow; text-decoration: none; font-weight: bold; cursor: default;"  # 改顏色、拿掉底線、讓滑鼠指標變正常


        # 畢業光錐
        if section_title == "毕业光锥":
            lightcone_html = ""
            reason_result = "⚠️ 找不到「推荐理由」相關內容。"

            for table in soup.find_all("table"):
                for tr in table.find_all("tr"):
                    th = tr.find("th")
                    if th and "毕业光锥" in th.get_text(strip=True):
                        td = tr.find("td")
                        if td:
                            # 抓圖片和名稱
                            img_tag = td.find("img")
                            name = ""
                            if td.find("font"):
                                name = td.find("font").get_text(strip=True)
                            elif td.find("a", title=True):
                                name = td.find("a", title=True)['title']

                            if img_tag and 'src' in img_tag.attrs:
                                img_url = img_tag['src']
                                lightcone_html = f"""
                                    <div style='display: inline-flex; flex-direction: column; align-items: center; gap: 10px;'>
                                        <img src="{img_url}" style="height:60px;">
                                        <span style="font-weight: bold; font-size: 18px;">{name}</span>
                                    </div>
                                """
                        break
                if lightcone_html:
                    break

            # 抓推薦理由
            for table in soup.find_all("table"):
                for tr in table.find_all("tr"):
                    tds = tr.find_all("td")
                    if len(tds) == 2 and tds[0].get_text(strip=True) == "推荐理由":
                        # ✅ 處理 <a> 標籤樣式
                        for a in tds[1].find_all("a"):
                            a.attrs = {}
                            a['style'] = "color: yellow; text-decoration: none; font-weight: bold;"

                        reason_html = str(tds[1])
                        reason_result = f"<p><b style='color: #f44336;'>【推薦理由】</b></p><div>{reason_html}</div>"
                        break

            return cc.convert(f"<p><b style='color: orange;'>【畢業光錐】</b></p>{lightcone_html}<br>{reason_result}")

        # 可選光錐
        elif section_title == "可选光锥":
            optional_lightcone_groups = []

            for table in soup.find_all("table"):
                trs = table.find_all("tr")
                i = 0
                while i < len(trs):
                    tr = trs[i]
                    th = tr.find("th")
                    if th and "可选光锥" in th.get_text(strip=True):
                        group_html = []
                        td = tr.find("td")
                        if td:
                            for a_tag in td.find_all("a"):
                                img_tag = a_tag.find("img")
                                if img_tag and img_tag.get("src"):
                                    name = img_tag.get("alt", "")
                                    src = img_tag.get("src", "")
                                    img_html = f"""
                                        <div style='display: inline-flex; flex-direction: column; align-items: center; margin: 5px;'>
                                            <img src="{src}" style="height:60px;">
                                            <span style="font-weight: bold; font-size: 18px;">{name}</span>
                                        </div>
                                    """
                                    group_html.append(img_html)

                        # 抓推薦理由
                        reason_text = "⚠️ 找不到推薦理由。"
                        if i + 1 < len(trs):
                            next_tr = trs[i + 1]
                            tds = next_tr.find_all("td")
                            if len(tds) == 2 and tds[0].get_text(strip=True) == "推荐理由":
                                # ✅ 處理 <a> 標籤樣式
                                for a in tds[1].find_all("a"):
                                    a.attrs = {}
                                    a['style'] = "color: yellow; text-decoration: none; font-weight: bold;"

                                reason_html = str(tds[1])
                                reason_text = f"<p><b style='color: #f44336;'>【推薦理由】</b></p><div>{reason_html}</div>"
                                i += 1

                        group_result = f"<div style='margin-bottom: 15px;'><p><b style='color: orange;'>【可選光錐組】</b></p>{''.join(group_html)}{reason_text}</div>"
                        optional_lightcone_groups.append(group_result)

                    i += 1

            if optional_lightcone_groups:
                return cc.convert("".join(optional_lightcone_groups))
            else:
                return cc.convert("⚠️ 找不到「可選光錐」相關內容。")

        # 一般欄位
        for table in soup.find_all("table"):
            for tr in table.find_all("tr"):
                tds = tr.find_all("td")
                if len(tds) == 2:
                    title = tds[0].get_text(strip=True)
                    if section_title in title:
                        content_td = tds[1]

                        #處理連結樣式（黃色、無底線、粗體，並移除 href 功能）
                        for a in content_td.find_all("a"):
                            a.attrs = {}  # 移除所有 href 等屬性
                            a['style'] = "color: yellow; text-decoration: none; font-weight: bold;"

                        #將標題改為橘色加粗
                        title_html = f"<p><span style='color: orange; font-weight: bold;'>【{title}】</span></p>"

                        #把內容包回 HTML
                        html_block = str(content_td)
                        # 替換特定<b>包住的項目為紅色
                        keywords = [
                            "【遗器套装】", "【位面饰品】", "【主词条推荐】",
                            "【副词条推荐】", "【词条推荐理由】",
                            "【躯干】", "【脚部】", "【位面球】", "【连结绳】"
                        ]

                        for keyword in keywords:
                            html_block = html_block.replace(
                                f"<b>{keyword}</b>",
                                f"<b style='color: #f44336;'>{keyword}</b>"  # 🔴 紅色
                            )
                        return cc.convert(f"{title_html}<div>{html_block}</div>")

        # 沒找到欄位
        return cc.convert(f"<p>⚠️ 找不到「{section_title}」相關內容。</p>")

    except Exception as e:
        return cc.convert(f"<p style='color:red;'>⚠️ 發生錯誤：{e}</p>")

"""#5.重點AI助手功能"""

import difflib

# 模糊比對取得問題類別
def detect_question_type_fuzzy(user_input: str) -> str | None:
    for q_type, keywords in question_type_map.items():
        for keyword in keywords:
            if keyword in user_input:
                return q_type
        # 加入模糊匹配（拼錯容錯）
        close_matches = difflib.get_close_matches(user_input, keywords, n=1, cutoff=0.7)
        if close_matches:
            return q_type
    return None

# 整合後的 AI 回答函式
def ai_answer(question):
    # 將使用者問題簡轉繁
    question_trad = cc.convert(question)

    # 嘗試從 question 中判斷 matched_field（欄位）
    matched_field_label = detect_question_type_fuzzy(question_trad)
    matched_field = None
    if matched_field_label:
        for label, value in available_fields:
            if matched_field_label == label:
                matched_field = value
                break

    # 嘗試從角色列表中找出提到的角色
    matched_character = None
    # 依照角色名稱長度排序（長的先比）
    sorted_characters = sorted(character_map.keys(), key=lambda x: -len(x))

    for trad_name in sorted_characters:
        if trad_name in question_trad:
            matched_character = character_map[trad_name]
            break

    if not matched_character or not matched_field:
        return cc.convert("⚠️ 抱歉，我找不到你要問的角色或欄位，請再確認一下問題內容喔～")

    # 呼叫爬蟲取得原始資料
    raw_html = fetch_specific_section(matched_character, matched_field)

    # 把 HTML 轉成純文字作為上下文給 AI 看
    raw_text = BeautifulSoup(raw_html, "html.parser").get_text()

    client = Groq(api_key=GROQ_API_KEY)

    #system prompt
    system_prompt = (
        "你是一個專業且熱情的《崩壞：星穹鐵道》遊戲顧問，擅長用簡短、重點的方式讓使用者快速理解他所詢問的關於角色的問題。"
        "請用輕鬆親切的語氣說明以下資料，幫助使用者快速理解角色該怎麼配裝。如果有推薦理由，也請用點列方式條列，簡潔明瞭。"
        "請務必使用繁體中文來回答。"
        "回答中禁止出現英文。"
        "回答光錐相關問題時，請詳細列出各組光錐內的名稱以及推薦理由"
        "請根據資料內容回覆，若資料不足請告訴使用者使用直接查詢功能。"
        "請勿給出不存在於資料中的推斷性回答。"
    )

    # 發送給 Groq 模型（LLaMA 3）
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"以下是來自星穹鐵道 Wiki 的資料：\n{raw_text}\n請幫我用親切有趣的語氣整理這份資料，並針對「{matched_field_label}」做說明。請避免使用英文並務必使用繁體中文(台灣)來回答"}
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content.strip()
    return cc.convert(f"<div style='white-space: pre-wrap; color: white;'>{answer}</div>")

"""#6.建立Gradio使用介面"""

# 建立 Gradio 介面
def query(character_name_trad, section_title):
    character_name_simp = character_map.get(character_name_trad, character_name_trad)
    return fetch_specific_section(character_name_simp, section_title)



with gr.Blocks(title="星穹鐵道角色欄位查詢") as demo:
    gr.Markdown("## 🌟 星穹鐵道角色攻略提取器（資料來源：星穹铁道 WIKI_BWIKI）")
    gr.Markdown("### ⚠️陣容搭配相關搜尋功能未完善")
    gr.Markdown("#### ⚠️目前尚有少數角色缺失及分組錯誤")

    with gr.Tabs():

        with gr.TabItem("毀滅"):
            with gr.Group():
                with gr.Row():
                    character_dropdown1 = gr.Dropdown(choices=["克拉拉", "阿蘭", "刃", "虎克", "丹恆·飲月", "鏡流", "托帕&帳帳", "雪衣", "開拓者·毀滅", "雲璃", "萬敵", "流螢", "亂破", "米莎"], label="選擇角色")
                    section_dropdown1 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn1 = gr.Button("查詢", variant="primary")

        with gr.TabItem("智識"):
            with gr.Group():
                with gr.Row():
                    character_dropdown2 = gr.Dropdown(choices=["姬子", "黑塔", "希露瓦", "景元", "青雀", "翡翠", "大黑塔", "那刻夏", "風堇"], label="選擇角色")
                    section_dropdown2 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn2 = gr.Button("查詢", variant="primary")

        with gr.TabItem("存護"):
            with gr.Group():
                with gr.Row():
                    character_dropdown3 = gr.Dropdown(choices=["傑帕德", "三月七", "符玄", "砂金", "開拓者·存護"], label="選擇角色")
                    section_dropdown3 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn3 = gr.Button("查詢", variant="primary")

        with gr.TabItem("虛無"):
            with gr.Group():
                with gr.Row():
                    character_dropdown4 = gr.Dropdown(choices=["銀狼", "瓦爾特", "佩拉", "卡芙卡", "黑天鵝", "黃泉", "桂乃芬", "桑博", "盧卡", "椒丘", "忘歸人"], label="選擇角色")
                    section_dropdown4 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn4 = gr.Button("查詢", variant="primary")

        with gr.TabItem("同諧"):
            with gr.Group():
                with gr.Row():
                    character_dropdown5 = gr.Dropdown(choices=["停雲", "布洛妮婭", "艾絲妲", "馭空", "寒鴉", "知更鳥", "星期日", "開拓者•同諧", "缇寶", "花火", "阮·梅"], label="選擇角色")
                    section_dropdown5 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn5 = gr.Button("查詢", variant="primary")

        with gr.TabItem("巡獵"):
            with gr.Group():
                with gr.Row():
                    character_dropdown6 = gr.Dropdown(choices=["丹恆", "彥卿", "希兒", "素裳", "銀枝", "波提歐", "飛霄", "貊澤", "真理醫生"], label="選擇角色")
                    section_dropdown6 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn6 = gr.Button("查詢", variant="primary")

        with gr.TabItem("豐饒"):
            with gr.Group():
                with gr.Row():
                    character_dropdown7 = gr.Dropdown(choices=["娜塔莎", "白露", "玲可", "羅剎", "霍霍", "靈砂", "加拉赫", "阿格萊雅"], label="選擇角色")
                    section_dropdown7 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn7 = gr.Button("查詢", variant="primary")

        with gr.TabItem("記憶"):
            with gr.Group():
                with gr.Row():
                    character_dropdown8 = gr.Dropdown(choices=["開拓者•記憶", "遐蝶", "藿藿", "阿格萊雅"], label="選擇角色")
                    section_dropdown8 = gr.Dropdown(choices=available_fields, label="選擇欄位標題")
                search_btn8 = gr.Button("查詢", variant="primary")

        with gr.TabItem("🤖AI 助手"):
            with gr.Group():
                gr.Markdown("🔍 範例: 三月七的聖遺物哪個好、克拉拉的主詞條那些好...等等。")
                gr.Markdown("1️⃣ 注意!「畢業光錐」和「平替光錐」需要分開搜尋!")
                gr.Markdown("2️⃣ 若回答出現英文，請嘗試再次送出問題。")
                gr.Markdown("3️⃣ 目前「畢業光錐」可能有名稱顯示的bug。")
                user_question = gr.Textbox(label="請輸入你的問題")
                ask_button = gr.Button("送出問題", variant="primary")
                ai_output = gr.HTML(label="AI 回答")

    output_box = gr.HTML(label="查詢結果")

    # 🔗 查詢綁定按鈕
    search_btn1.click(fn=query, inputs=[character_dropdown1, section_dropdown1], outputs=output_box)
    search_btn2.click(fn=query, inputs=[character_dropdown2, section_dropdown2], outputs=output_box)
    search_btn3.click(fn=query, inputs=[character_dropdown3, section_dropdown3], outputs=output_box)
    search_btn4.click(fn=query, inputs=[character_dropdown4, section_dropdown4], outputs=output_box)
    search_btn5.click(fn=query, inputs=[character_dropdown5, section_dropdown5], outputs=output_box)
    search_btn6.click(fn=query, inputs=[character_dropdown6, section_dropdown6], outputs=output_box)
    search_btn7.click(fn=query, inputs=[character_dropdown7, section_dropdown7], outputs=output_box)
    search_btn8.click(fn=query, inputs=[character_dropdown8, section_dropdown8], outputs=output_box)

    ask_button.click(fn=ai_answer, inputs=user_question, outputs=ai_output)

demo.launch(share=True, debug=True, server_port=7858)