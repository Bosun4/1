import os, json, requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url="https://nan.meta-api.vip/v1")

def get_jingcai_list():
    """高强度抓取 500网 竞彩足球 列表"""
    url = f"https://trade.500.com/jczq/?date={datetime.now().strftime('%Y-%m-%d')}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = 'gb2312' # 500网专用中文编码
        soup = BeautifulSoup(res.text, 'html.parser')
        matches = []
        # 寻找比赛对阵行
        rows = soup.find_all('tr', class_='bet_table_tr')[:5] # 只取前5场精华
        for r in rows:
            league = r.find('a', class_='p_tb_le').text.strip()
            teams = r.find_all('a', class_='p_tb_team')
            if len(teams) >= 2:
                matches.append(f"{league}联赛: {teams[0].text.strip()} VS {teams[1].text.strip()}")
        return matches
    except: return []

def ask_ai(match):
    try:
        res = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": "你是一个体彩专家。回答必须极简！格式：【预测比分】: X-X | 【结果】: 胜/平/负 | 【理由】: 一句话概括核心点。"},
                {"role": "user", "content": f"分析这场竞彩比赛：{match}"}
            ],
            max_tokens=200
        )
        return res.choices[0].message.content.strip()
    except: return "AI 分析中..."

if __name__ == "__main__":
    print("🕸️ 正在同步 500网/澳客 竞彩比赛列表...")
    matches = get_jingcai_list()
    data = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "predictions": []}
    
    if not matches: # 兜底防止空数据
        matches = ["英超: 阿森纳 VS 切尔西 (测试)", "欧冠: 皇马 VS 曼城 (测试)"]
        
    for m in matches:
        print(f"👉 正在分析: {m}")
        ans = ask_ai(m)
        data["predictions"].append({"match": m, "text": ans})
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("✅ 竞彩清单已生成！")
