import os, json, requests
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url="https://nan.meta-api.vip/v1")
SPORTS_KEY = os.environ.get("SPORTS_API_KEY")

def get_smart_data():
    """高科技融合：自动抓取今日赛事 + 挖掘历史交锋大数据"""
    headers = {"x-apisports-key": SPORTS_KEY}
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 1. 抓取今日焦点比赛
    url_fixtures = "https://v3.football.api-sports.io/fixtures"
    try:
        res = requests.get(url_fixtures, headers=headers, params={"date": today}).json()
        if not res.get("response"): return "暂无赛事", "无数据"
            
        m = res["response"][0] 
        home, away = m['teams']['home'], m['teams']['away']
        match_title = f"[{m['league']['name']}] {home['name']} VS {away['name']}"
        
        # 2. 核心科技：调取开源界最看重的 H2H (历史交锋) 真实数据
        h2h_url = "https://v3.football.api-sports.io/fixtures/headtohead"
        h2h_res = requests.get(h2h_url, headers=headers, params={"h2h": f"{home['id']}-{away['id']}", "last": "5"}).json()
        
        history_text = "【近5场真实交锋大数据】:\n"
        if h2h_res.get("response"):
            for past in h2h_res["response"]:
                score = f"{past['goals']['home']}-{past['goals']['away']}"
                history_text += f"- {past['teams']['home']['name']} {score} {past['teams']['away']['name']}\n"
        else:
            history_text += "暂无近期交锋数据"

        # 把真实数据和球队名字融合成超级提示词
        rich_prompt = f"今日赛事: {match_title}\n{history_text}\n请严格基于上述真实历史比分数据，运行你的专业算法进行推演。"
        return match_title, rich_prompt
    except Exception as e:
        return "数据抓取失败", str(e)

def ask_expert(sys_role, prompt, model="gpt-5.2"):
    """召唤AI专家并注入真实数据"""
    try:
        res = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": sys_role}, {"role": "user", "content": prompt}],
            max_tokens=300
        )
        return res.choices[0].message.content.strip()
    except Exception as e: return f"算力超载: {e}"

if __name__ == "__main__":
    print("🔍 正在启动高阶数据特征挖掘...")
    title, rich_prompt = get_smart_data()
    print(f"🎯 锁定目标: {title}")
    print("📈 成功提取真实历史交锋大数据！正在注入 AI 矩阵...")
    
    data = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "match": title, "predictions": []}
    
    if "VS" in title:
        sys1 = "你是泊松分布与xG专家。请分析我提供的【真实交锋大数据】，计算出进球期望，输出最科学的【精准比分】和【大小球】。"
        data["predictions"].append({"engine": "🧮 泊松分布比分模型 (真实数据驱动)", "text": ask_expert(sys1, rich_prompt)})

        sys2 = "你是基于Elo等级分系统的专家。请根据我提供的【真实交锋大数据】评估血脉压制情况，给出【胜平负概率(%)】和【竞彩推荐】。"
        data["predictions"].append({"engine": "⚔️ Elo 实力评级模型 (真实数据驱动)", "text": ask_expert(sys2, rich_prompt)})

        sys3 = "你是博彩操盘手。结合历史比分寻找庄家可能利用的【数据诱导点】(例如某队历史占优必定大热)，给出【防坑警告】和【投资建议】。"
        data["predictions"].append({"engine": "🏦 凯利机构操盘模型 (反诱盘逻辑)", "text": ask_expert(sys3, rich_prompt)})

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("✅ 真实数据融合分析完毕！网页前端已同步更新。")
