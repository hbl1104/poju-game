#!/usr/bin/env python3
"""
史料挖掘Agent - 搜索模块
从网络/本地检索与历史事件相关的原始史料
"""

import json
import os
import re
import sys
from urllib.parse import quote

# 本地史料库路径
LOCAL_DB_PATH = os.path.join(os.path.dirname(__file__), "../output/local_history_db.json")

# 核心史书列表
CORE_HISTORIES = [
    "史记", "汉书", "后汉书", "三国志", "晋书", "资治通鉴",
    "战国策", "左传", "国语", "吕氏春秋"
]

# 已知的破局游戏历史事件库
KNOWN_EVENTS = {
    "jingke": {
        "name": "荆轲刺秦王",
        "era": "战国 · 秦王政二十年（前227年）",
        "sources": ["史记·刺客列传", "战国策·燕策三"],
        "key_figures": ["荆轲", "秦王嬴政", "夏无且", "秦舞阳", "太子丹"],
        "keywords": ["图穷匕见", "药囊", "负剑", "咸阳宫"]
    },
    "caoshuang": {
        "name": "高平陵之变",
        "era": "曹魏 · 正始十年（249年）",
        "sources": ["三国志·魏书·曹爽传", "晋书·宣帝纪", "资治通鉴·魏纪九"],
        "key_figures": ["曹爽", "司马懿", "桓范", "曹芳", "郭太后"],
        "keywords": ["洛水之誓", "富家翁", "高平陵", "典农", "别营"]
    },
    "yuyi": {
        "name": "齐王攸之祸",
        "era": "西晋 · 太康年间（280年代）",
        "sources": ["晋书·齐王攸传", "晋书·武帝纪", "资治通鉴·晋纪十七"],
        "key_figures": ["司马攸", "司马炎", "程据", "冯紞", "荀勖"],
        "keywords": ["风疾", "太医", "就国", "青州", "借刀杀人"]
    },
    "xilong": {
        "name": "扬州之叛",
        "era": "西晋 · 永宁元年（301年）",
        "sources": ["晋书·郗隆传", "晋书·齐王冏传", "资治通鉴·晋纪二十五"],
        "key_figures": ["郗隆", "司马冏", "司马伦", "赵诱", "顾彦"],
        "keywords": ["骑墙", "檄文", "竞价", "扬州", "参军"]
    }
}


def search_local_db(query: str) -> list:
    """搜索本地史料数据库"""
    if not os.path.exists(LOCAL_DB_PATH):
        return []
    
    with open(LOCAL_DB_PATH, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    results = []
    query_lower = query.lower()
    
    for entry in db.get("entries", []):
        text = entry.get("text", "")
        if query_lower in text.lower():
            results.append(entry)
    
    return results


def search_by_event(event_id: str) -> dict:
    """根据事件ID获取已知的史料框架"""
    return KNOWN_EVENTS.get(event_id, {})


def extract_historical_sources(text: str) -> list:
    """从文本中提取史书引用"""
    patterns = [
        r'《([^》]+)》',
        r'"([^"]*史记[^"]*)"',
        r'"([^"]*汉书[^"]*)"',
        r'"([^"]*资治通鉴[^"]*)"',
        r'"([^"]*晋书[^"]*)"',
    ]
    
    sources = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        sources.extend(matches)
    
    return list(set(sources))


def build_search_query(event_name: str, figures: list = None, keywords: list = None) -> str:
    """构建搜索查询词"""
    parts = [event_name]
    if figures:
        parts.extend(figures[:2])  # 最多2个人物
    if keywords:
        parts.extend(keywords[:2])  # 最多2个关键词
    
    return " ".join(parts)


def find_primary_sources(event_id: str) -> dict:
    """
    为指定事件查找一手史料来源
    返回包含史书名称、卷次、关键原文的结构化数据
    """
    event = KNOWN_EVENTS.get(event_id)
    if not event:
        return {"error": f"未知事件: {event_id}"}
    
    # 构建结果
    result = {
        "event_id": event_id,
        "event_name": event["name"],
        "era": event["era"],
        "primary_sources": [],
        "key_figures": event["key_figures"],
        "keywords": event["keywords"],
        "source_urls": []
    }
    
    # 为每个史书来源生成检索链接
    for source in event["sources"]:
        result["primary_sources"].append({
            "source": source,
            "availability": "需人工核对原文",
            "reliability": "正史" if any(h in source for h in CORE_HISTORIES) else "待考"
        })
    
    return result


def discover_new_events(era: str = None, theme: str = None) -> list:
    """
    根据时代或主题发现新的潜在破局故事素材
    返回候选事件列表
    """
    candidates = []
    
    # 预定义的候选事件池（可扩展）
    candidate_pool = [
        {
            "id": "maweipo",
            "name": "马嵬坡之变",
            "era": "唐 · 天宝十五载（756年）",
            "theme": "道德两难",
            "potential": "高力士的抉择——是否处死杨贵妃",
            "sources": ["旧唐书·杨贵妃传", "资治通鉴·唐纪三十四"]
        },
        {
            "id": "chibi",
            "name": "赤壁之战前夕",
            "era": "东汉 · 建安十三年（208年）",
            "theme": "信息差陷阱",
            "potential": "黄盖的苦肉计——如何让曹操相信投降",
            "sources": ["三国志·吴书·周瑜传", "资治通鉴·汉纪五十七"]
        },
        {
            "id": "xuanwumen",
            "name": "玄武门之变",
            "era": "唐 · 武德九年（626年）",
            "theme": "时间压力",
            "potential": "尉迟恭的抉择——是否射杀李元吉",
            "sources": ["旧唐书·太宗纪", "资治通鉴·唐纪七"]
        },
        {
            "id": "yueyang",
            "name": "岳阳楼记背后",
            "era": "北宋 · 庆历六年（1046年）",
            "theme": "骑墙困境",
            "potential": "滕子京被贬后的政治生存",
            "sources": ["宋史·滕宗谅传"]
        },
        {
            "id": "shouxin",
            "name": "守新城",
            "era": "三国 · 魏太和二年（228年）",
            "theme": "被借刀杀人",
            "potential": "孟达叛魏投蜀，司马懿八日奔袭",
            "sources": ["三国志·魏书·明帝纪", "晋书·宣帝纪"]
        }
    ]
    
    for candidate in candidate_pool:
        if era and era not in candidate["era"]:
            continue
        if theme and theme not in candidate["theme"]:
            continue
        candidates.append(candidate)
    
    return candidates


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python search.py <事件ID|关键词>")
        print(f"\n已知事件: {', '.join(KNOWN_EVENTS.keys())}")
        print("\n示例:")
        print("  python search.py jingke")
        print("  python search.py discover --theme 骑墙困境")
        return
    
    arg = sys.argv[1]
    
    if arg == "discover":
        theme = None
        if "--theme" in sys.argv:
            idx = sys.argv.index("--theme")
            theme = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        candidates = discover_new_events(theme=theme)
        print(json.dumps(candidates, ensure_ascii=False, indent=2))
    else:
        result = find_primary_sources(arg)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
