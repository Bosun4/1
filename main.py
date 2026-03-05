import os, json, requests
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url="https://nan.meta-api.vip/v1")
SPORTS_KEY = os.environ.get("SPORTS_API_KEY")

def get_smart_data():
    headers = {"x-apisports-key": SPORTS_KEY}
    url_fixtures = "https://v3.football.api-sports.io/fixtures"
    try:
        res = requests.get(url_fixtures, headers=headers, params={"date": datetime.now().strftime("%Y-%m-%d")}).json()
        if not res.get("response"): return "暂无比赛", ""
        m = res["response"][0]
        return f"{m['teams']['home']['name']} VS {m['teams']['away']['name']}", f"这场比赛是 {m['teams']['home']['name']} 对阵 {m['teams']['away']['name']}"
    except: return "获取失败", ""

def ask_expert(role, match):
    try:
        res = client.chat.completions.create(
            model="gpt-5.2",
            messages=[
                {"role": "system", "content": f"你是一个顶级体育分析师。你的回答必须极其简练！格式：【预测比分】: X-X \n【胜负推荐】: 主胜/平/负 \n【核心理由】: 1, 2, 3。"},
                {"role": "user", "content": f"分析这场比赛并给出结果：{match}"}
            ],
            max_tokens=200
        )
        return res.choices[0].message.content.strip()
    except: return "分析异常"

if __name__ == "__main__":
    title, prompt = get_smart_data()
    data = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "match": title, "predictions": []}
    if "VS" in title:
        data["predictions"].append({"engine": "精准比分预测", "text": ask_expert("Score", title)})
        data["predictions"].append({"engine": "竞彩胜平负", "text": ask_expert("Result", title)})
    
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
