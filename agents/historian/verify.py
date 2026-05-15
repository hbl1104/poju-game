#!/usr/bin/env python3
"""
史料挖掘Agent - 校验模块
校验故事内容的历史准确性
"""

import json
import re
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class VerificationResult:
    """校验结果"""
    category: str       # 类别: 时间/人物/地点/事件/引文
    claim: str          # 故事中的说法
    status: str         # 状态: confirmed/disputed/unknown/fictional
    source: str         # 依据
    note: str = ""      # 备注


class Verifier:
    """史实校验器"""
    
    # 已知的历史时间线（用于校验）
    TIMELINE = {
        "荆轲刺秦王": {"year": -227, "sources": ["史记·刺客列传"]},
        "高平陵之变": {"year": 249, "sources": ["三国志", "晋书"]},
        "齐王攸就国": {"year": 283, "sources": ["晋书·齐王攸传"]},
        "司马伦篡位": {"year": 301, "sources": ["晋书·惠帝纪"]},
    }
    
    # 人物生卒年
    FIGURE_LIFESPAN = {
        "荆轲": {"birth": None, "death": -227, "note": "刺秦失败被杀"},
        "嬴政": {"birth": -259, "death": -210, "note": "秦始皇"},
        "夏无且": {"birth": None, "death": None, "note": "侍医，后事不详"},
        "曹爽": {"birth": None, "death": 249, "note": "高平陵之变后被诛"},
        "司马懿": {"birth": 179, "death": 251, "note": "晋宣帝"},
        "桓范": {"birth": None, "death": 249, "note": "高平陵之变后被诛"},
        "司马攸": {"birth": 248, "death": 283, "note": "齐王，被迫就国途中卒"},
        "司马炎": {"birth": 236, "death": 290, "note": "晋武帝"},
        "郗隆": {"birth": None, "death": 301, "note": "扬州刺史，被杀"},
        "司马冏": {"birth": None, "death": 302, "note": "齐王，后被杀"},
    }
    
    def __init__(self):
        self.results = []
    
    def verify_story(self, story_text: str, event_id: str = None) -> List[VerificationResult]:
        """校验整个故事的历史准确性"""
        self.results = []
        
        # 1. 校验时间
        self._verify_time(story_text, event_id)
        
        # 2. 校验人物
        self._verify_figures(story_text)
        
        # 3. 校验引文
        self._verify_quotes(story_text)
        
        # 4. 校验地点
        self._verify_locations(story_text)
        
        # 5. 标记虚构内容
        self._identify_fiction(story_text)
        
        return self.results
    
    def _verify_time(self, text: str, event_id: str = None):
        """校验时间表述"""
        # 提取年份表述
        year_patterns = [
            r'(前?\d{1,4})年',
            r'公元(\d{1,4})年',
            r'公元前(\d{1,4})年',
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text)
            for year_str in matches:
                year = int(year_str.replace("前", "-"))
                # 简单校验：战国到三国时期
                if year < -500 or year > 400:
                    self.results.append(VerificationResult(
                        category="时间",
                        claim=f"{year_str}年",
                        status="disputed",
                        source="",
                        note="年份超出合理范围"
                    ))
                else:
                    self.results.append(VerificationResult(
                        category="时间",
                        claim=f"{year_str}年",
                        status="confirmed",
                        source="历法推算",
                        note="年份在合理范围内"
                    ))
    
    def _verify_figures(self, text: str):
        """校验人物"""
        for name, info in self.FIGURE_LIFESPAN.items():
            if name in text:
                status = "confirmed"
                note = f"史书有载"
                
                # 检查是否有虚构的对话
                if f"{name}说" in text or f"{name}想" in text or f"{name}感到" in text:
                    note += "；心理活动和部分对话为文学虚构"
                    status = "fictional"
                
                self.results.append(VerificationResult(
                    category="人物",
                    claim=f"{name} ({info['note']})",
                    status=status,
                    source="正史记载",
                    note=note
                ))
    
    def _verify_quotes(self, text: str):
        """校验引文"""
        # 查找书名号中的内容
        quotes = re.findall(r'《([^》]+)》', text)
        for quote in quotes:
            if any(h in quote for h in ["史记", "汉书", "三国志", "晋书", "资治通鉴"]):
                self.results.append(VerificationResult(
                    category="引文",
                    claim=f"《{quote}》",
                    status="confirmed",
                    source="正史",
                    note=""
                ))
            else:
                self.results.append(VerificationResult(
                    category="引文",
                    claim=f"《{quote}》",
                    status="unknown",
                    source="",
                    note="需人工核对"
                ))
        
        # 检查直接引用的古文
        classical_patterns = [
            r'"([^"]*(?:曰|云|谓)[^"]*)"',
            r'「([^」]*(?:曰|云|谓)[^」]*)」',
        ]
        for pattern in classical_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                self.results.append(VerificationResult(
                    category="引文",
                    claim=match[:50] + "..." if len(match) > 50 else match,
                    status="unknown",
                    source="",
                    note="需核对原文"
                ))
    
    def _verify_locations(self, text: str):
        """校验地点"""
        known_locations = [
            "咸阳", "洛阳", "许昌", "扬州", "青州", "长安",
            "高平陵", "太医署", "刺史府", "玄武门", "马嵬坡"
        ]
        
        for loc in known_locations:
            if loc in text:
                self.results.append(VerificationResult(
                    category="地点",
                    claim=loc,
                    status="confirmed",
                    source="地理志",
                    note=""
                ))
    
    def _identify_fiction(self, text: str):
        """识别虚构内容"""
        # 标记明显的文学加工
        fiction_markers = [
            ("加缪", "引用加缪哲学观点为现代阐释，非史实"),
            ("存在主义", "现代哲学概念，非历史概念"),
            ("荒诞", "现代文学阐释，非历史评价"),
            ("西西弗斯", "希腊神话比喻，非史实"),
            ("他看着", "第三人称心理描写，文学虚构"),
            ("他想起了", "内心独白，文学虚构"),
            ("感到一种", "情感描写，文学虚构"),
            ("他不知道", "内心活动，文学虚构"),
        ]
        
        for marker, note in fiction_markers:
            if marker in text:
                self.results.append(VerificationResult(
                    category="文学加工",
                    claim=f"包含'{marker}'",
                    status="fictional",
                    source="",
                    note=note
                ))
    
    def generate_report(self) -> str:
        """生成校验报告"""
        lines = ["# 史实校验报告\n"]
        
        categories = {}
        for r in self.results:
            categories.setdefault(r.category, []).append(r)
        
        for cat, items in categories.items():
            lines.append(f"\n## {cat}\n")
            for item in items:
                icon = {
                    "confirmed": "✅",
                    "disputed": "⚠️",
                    "unknown": "❓",
                    "fictional": "📝"
                }.get(item.status, "❓")
                lines.append(f"{icon} **{item.claim}** — {item.status}")
                if item.source:
                    lines.append(f"   依据: {item.source}")
                if item.note:
                    lines.append(f"   备注: {item.note}")
                lines.append("")
        
        return "\n".join(lines)


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python verify.py <故事文件路径>")
        return
    
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    event_id = filepath.split('/')[-1].replace('.md', '')
    
    verifier = Verifier()
    results = verifier.verify_story(text, event_id)
    
    print(verifier.generate_report())
    
    # 输出JSON
    output = {
        "event_id": event_id,
        "total_checks": len(results),
        "confirmed": len([r for r in results if r.status == "confirmed"]),
        "disputed": len([r for r in results if r.status == "disputed"]),
        "unknown": len([r for r in results if r.status == "unknown"]),
        "fictional": len([r for r in results if r.status == "fictional"]),
        "details": [
            {"category": r.category, "claim": r.claim, "status": r.status, "note": r.note}
            for r in results
        ]
    }
    
    # 保存报告
    report_path = filepath.replace('.md', '_verification.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(verifier.generate_report())
    
    json_path = filepath.replace('.md', '_verification.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存: {report_path}")
    print(f"数据已保存: {json_path}")


if __name__ == "__main__":
    main()
