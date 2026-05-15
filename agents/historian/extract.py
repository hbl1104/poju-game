#!/usr/bin/env python3
"""
史料挖掘Agent - 提取模块
从原始史料中提取关键信息：人物、时间、地点、对话、决策点
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class HistoricalFigure:
    """历史人物"""
    name: str
    title: str = ""           # 官职/身份
    faction: str = ""         # 所属阵营
    motivation: str = ""      # 动机/目标
    quoted_speech: List[str] = None  # 原文引用
    
    def __post_init__(self):
        if self.quoted_speech is None:
            self.quoted_speech = []


@dataclass
class DecisionPoint:
    """决策点 - 破局游戏的核心"""
    situation: str            # 情境描述
    options: List[str]        # 可选行动
    historical_choice: str    # 历史上实际的选择
    historical_outcome: str   # 历史结果
    alternative_outcomes: List[dict] = None  # 假设性结局
    source_quote: str = ""    # 史料原文
    
    def __post_init__(self):
        if self.alternative_outcomes is None:
            self.alternative_outcomes = []


@dataclass
class HistoricalEvent:
    """完整历史事件"""
    event_id: str
    name: str
    era: str
    location: str
    summary: str
    figures: List[HistoricalFigure]
    decision_points: List[DecisionPoint]
    primary_sources: List[str]
    historical_significance: str = ""
    
    def to_dict(self):
        return asdict(self)


class Extractor:
    """史料信息提取器"""
    
    # 官职关键词
    TITLES = [
        "皇帝", "王", "侯", "将军", "大夫", "令", "丞", "尉", "史", 
        "侍中", "尚书", "刺史", "太守", "太守", "参军", "主簿",
        "太医", "医工", "刺客", "使者", "太监", "宦官"
    ]
    
    # 对话标记
    SPEECH_MARKERS = ["曰", "云", "谓", "言", "道", "叹", "呼"]
    
    def __init__(self):
        self.figures_cache = {}
    
    def extract_figures(self, text: str, known_names: List[str] = None) -> List[HistoricalFigure]:
        """从文本中提取人物信息"""
        figures = []
        
        # 使用已知人物名
        if known_names:
            for name in known_names:
                figure = self._extract_figure_details(text, name)
                figures.append(figure)
        
        return figures
    
    def _extract_figure_details(self, text: str, name: str) -> HistoricalFigure:
        """提取单个人物的详细信息"""
        # 查找官职
        title = ""
        for t in self.TITLES:
            pattern = f"{name}.*?{t}|{t}.*?{name}"
            if re.search(pattern, text):
                title = t
                break
        
        # 查找直接引语
        speeches = []
        patterns = [
            f"{name}.*?曰[：:]?「([^」]+)」",
            f"{name}.*?曰[：:]?\"([^\"]+)\"",
            f"{name}.*?曰[：:]?(.{{3,50}}?)[。；]",
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            speeches.extend(matches)
        
        return HistoricalFigure(
            name=name,
            title=title,
            quoted_speech=speeches[:5]  # 最多5条引语
        )
    
    def extract_decision_points(self, text: str, event_context: dict = None) -> List[DecisionPoint]:
        """
        从叙事文本中提取决策点
        识别"如果...就..."、"或...或..."等结构
        """
        decisions = []
        
        # 模式1: "或...或..." 结构
        pattern_or = r'或(.{3,30})，或(.{3,30})'
        matches = re.findall(pattern_or, text)
        for m in matches:
            decisions.append(DecisionPoint(
                situation="面临抉择",
                options=list(m),
                historical_choice="",
                historical_outcome="",
                source_quote=text[max(0, text.find(m[0])-20):text.find(m[1])+len(m[1])+20]
            ))
        
        # 模式2: "若...则..." 假设结构
        pattern_if = r'若(.{3,30})，(?:则|必|将)(.{3,30})'
        matches = re.findall(pattern_if, text)
        for m in matches:
            decisions.append(DecisionPoint(
                situation=f"若{m[0]}",
                options=[m[1], f"不{m[0]}"],
                historical_choice="",
                historical_outcome="",
                source_quote=f"若{m[0]}，则{m[1]}"
            ))
        
        # 模式3: 数字标记的选择（如"上策""中策""下策"）
        pattern_strategy = r'(上策|中策|下策|上计|中计|下计)[：:]?(.{5,50})[。；]'
        matches = re.findall(pattern_strategy, text)
        if matches:
            options = [m[1] for m in matches]
            decisions.append(DecisionPoint(
                situation="谋士献计",
                options=options,
                historical_choice="",
                historical_outcome="",
                source_quote="；".join([m[1] for m in matches])
            ))
        
        return decisions
    
    def extract_key_scenes(self, text: str) -> List[dict]:
        """提取关键场景（时间+地点+事件）"""
        scenes = []
        
        # 场景标题模式（如"一、殿上"）
        pattern_scene = r'###?\s*[一二三四五六七八九十]+、(.+)\n\n(.+?)(?=###?\s*[一二三四五六七八九十]+、|$)'
        matches = re.findall(pattern_scene, text, re.DOTALL)
        
        for title, content in matches:
            scenes.append({
                "title": title.strip(),
                "content": content.strip()[:500],  # 限制长度
                "key_actions": self._extract_actions(content),
                "key_quotes": self._extract_quotes(content)
            })
        
        return scenes
    
    def _extract_actions(self, text: str) -> List[str]:
        """提取关键动作"""
        actions = []
        # 动词+宾语模式
        pattern = r'[，。]([^，。]{2,20}(?:拔|刺|掷|逃|追|杀|救|喊|写|读|看|听|说|走|跑|站|坐|跪|拜|诏|令|封|贬|赐|斩)[^，。]{2,20})[，。]'
        matches = re.findall(pattern, text)
        return list(set(matches))[:10]
    
    def _extract_quotes(self, text: str) -> List[str]:
        """提取引语"""
        quotes = []
        patterns = [
            r'「([^」]{5,100})」',
            r'"([^"]{5,100})"',
            r'曰[：:]?(.{5,100}?)[。；]'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            quotes.extend(matches)
        return quotes[:5]
    
    def process_story_file(self, filepath: str) -> HistoricalEvent:
        """处理一个完整的故事文件，提取所有信息"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # 提取基础信息
        name_match = re.search(r'#\s*(.+)\n', text)
        name = name_match.group(1) if name_match else "未知"
        
        era_match = re.search(r'\*\*时代\*\*[：:]\s*(.+?)\n', text)
        era = era_match.group(1) if era_match else ""
        
        location_match = re.search(r'\*\*地点\*\*[：:]\s*(.+?)\n', text)
        location = location_match.group(1) if location_match else ""
        
        # 提取人物
        protagonist_match = re.search(r'\*\*主角\*\*[：:]\s*(.+?)\n', text)
        protagonist = protagonist_match.group(1) if protagonist_match else ""
        
        # 从正文中提取所有可能的人名（2-4字）
        name_pattern = r'[\u4e00-\u9fa5]{2,4}(?=[，。、；："「」]|[曰云谓言道])'
        potential_names = list(set(re.findall(name_pattern, text)))
        
        figures = []
        if protagonist:
            figures.append(self._extract_figure_details(text, protagonist))
        for pn in potential_names[:10]:  # 限制数量
            if pn != protagonist and len(pn) >= 2:
                fig = self._extract_figure_details(text, pn)
                if fig.quoted_speech:  # 只保留有引语的人物
                    figures.append(fig)
        
        # 提取决策点
        decisions = self.extract_decision_points(text)
        
        # 提取场景
        scenes = self.extract_key_scenes(text)
        
        # 提取史料来源
        sources = re.findall(r'《([^》]+)》', text)
        
        # 提取困局类型
        dilemma_match = re.search(r'\*\*困局\*\*[：:]\s*(.+?)\n', text)
        dilemma = dilemma_match.group(1) if dilemma_match else ""
        
        # 构建事件ID
        event_id = filepath.split('/')[-1].replace('.md', '')
        
        return HistoricalEvent(
            event_id=event_id,
            name=name,
            era=era,
            location=location,
            summary=f"{name}：{dilemma}困局",
            figures=figures,
            decision_points=decisions,
            primary_sources=list(set(sources)),
            historical_significance=f"{era}，{dilemma}"
        )


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python extract.py <故事文件路径>")
        print("\n示例:")
        print("  python extract.py ../../stories/jingke.md")
        return
    
    filepath = sys.argv[1]
    extractor = Extractor()
    event = extractor.process_story_file(filepath)
    
    print(json.dumps(event.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
