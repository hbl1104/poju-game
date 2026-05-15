#!/usr/bin/env python3
"""
多媒体转换Agent - 游戏卡片生成器
将故事数据转换为破局游戏可用的卡片数据格式
"""

import json
import os
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class CardData:
    """卡片数据"""
    level_id: str
    level_name: str
    era: str
    protagonist: str
    dilemma: str
    scenes_json: str      # JavaScript对象格式的字符串
    css_theme: dict       # CSS主题色


class CardGenerator:
    """游戏卡片生成器"""
    
    # 困局类型对应的视觉主题
    THEMES = {
        "被借刀杀人": {
            "primary": "#8B3A3A",      # 暗红
            "secondary": "#C03C28",     # 朱砂
            "accent": "#B8956A",        # 金色
            "bg_gradient": "linear-gradient(180deg, #2C2826 0%, #4A3C3C 100%)",
            "card_border": "#8B3A3A",
            "mood": "紧张、阴谋"
        },
        "骑墙困境": {
            "primary": "#4A5568",      # 灰蓝
            "secondary": "#718096",     # 中灰
            "accent": "#B8956A",        # 金色
            "bg_gradient": "linear-gradient(180deg, #2D3748 0%, #4A5568 100%)",
            "card_border": "#718096",
            "mood": "压抑、两难"
        },
        "承诺陷阱": {
            "primary": "#744210",      # 暗金
            "secondary": "#B8956A",     # 金色
            "accent": "#C03C28",        # 朱砂
            "bg_gradient": "linear-gradient(180deg, #2C2826 0%, #4A3C2C 100%)",
            "card_border": "#B8956A",
            "mood": "诱惑、危险"
        },
        "咫尺之局": {
            "primary": "#2C5282",      # 深蓝
            "secondary": "#4A7C59",     # 墨绿
            "accent": "#B8956A",        # 金色
            "bg_gradient": "linear-gradient(180deg, #1A365D 0%, #2C5282 100%)",
            "card_border": "#4A7C59",
            "mood": "紧迫、决断"
        },
    }
    
    def __init__(self):
        self.output_dir = os.path.join(os.path.dirname(__file__), "../output")
    
    def generate_card_data(self, game_data: dict, narrative_data: dict = None) -> CardData:
        """
        生成游戏卡片数据
        
        Args:
            game_data: 游戏场景数据（来自choices.py）
            narrative_data: 叙事数据（来自narrative.py）
        """
        level_id = game_data.get("id", "unknown")
        level_name = game_data.get("name", "")
        era = game_data.get("era", "")
        dilemma = game_data.get("tag", "被借刀杀人")
        
        # 获取主题
        theme = self.THEMES.get(dilemma, self.THEMES["被借刀杀人"])
        
        # 生成场景JSON
        scenes_json = self._build_scenes_js(game_data)
        
        # 生成主角名
        protagonist = narrative_data.get("protagonist", "你") if narrative_data else "你"
        
        return CardData(
            level_id=level_id,
            level_name=level_name,
            era=era,
            protagonist=protagonist,
            dilemma=dilemma,
            scenes_json=scenes_json,
            css_theme=theme
        )
    
    def _build_scenes_js(self, game_data: dict) -> str:
        """构建JavaScript场景对象字符串"""
        scenes = game_data.get("scenes", [])
        
        js_lines = ["{"]
        
        for scene in scenes:
            scene_id = scene.get("id", "")
            js_lines.append(f'  {scene_id}: {{')
            text = scene.get("text", "")
            escaped_text = text.replace(chr(10), "\\n")
            js_lines.append(f'    text: `{escaped_text}`,')
            
            # 选项
            choices = scene.get("choices", [])
            if choices:
                js_lines.append('    choices: [')
                for choice in choices:
                    js_lines.append('      {')
                    js_lines.append(f'        text: "{choice.get("text", "")}",')
                    js_lines.append(f'        next: "{choice.get("next", "")}",')
                    js_lines.append(f'        tag: "{choice.get("tag", "")}",')
                    if choice.get("parenthetical"):
                        js_lines.append(f'        parenthetical: "{choice.get("parenthetical", "")}",')
                    js_lines.append('      },')
                js_lines.append('    ],')
            
            # 结局
            if scene.get("result"):
                js_lines.append(f'    result: "{scene.get("result")}",')
            
            # 历史注脚
            if scene.get("historyNote"):
                note = scene.get("historyNote", "").replace('"', '\\"')
                js_lines.append(f'    historyNote: "{note}",')
            
            js_lines.append('  },')
        
        js_lines.append("}")
        
        return "\n".join(js_lines)
    
    def generate_level_card_html(self, card_data: CardData) -> str:
        """生成关卡卡片HTML（用于关卡选择页）"""
        theme = card_data.css_theme
        
        html = f"""
        <div class="level-card" data-level="{card_data.level_id}" style="border-color: {theme['card_border']}">
          <div class="era">{card_data.era}</div>
          <h3>{card_data.level_name}</h3>
          <div class="tag">{card_data.dilemma}</div>
          <p class="desc">{card_data.protagonist}的{card_data.dilemma}困局</p>
          <div class="mood-indicator" style="background: {theme['primary']}">{theme['mood']}</div>
        </div>
        """
        return html
    
    def generate_game_snippet(self, card_data: CardData) -> str:
        """生成可直接插入游戏的JavaScript代码片段"""
        level_id = card_data.level_id
        
        snippet = f"""
// ===== 关卡: {card_data.level_name} =====
const {level_id} = {{
  id: '{level_id}',
  era: '{card_data.era}',
  name: '{card_data.level_name}',
  desc: '{card_data.protagonist}的{card_data.dilemma}困局',
  tag: '{card_data.dilemma}',
  theme: {json.dumps(card_data.css_theme, ensure_ascii=False)},
  scenes: {card_data.scenes_json}
}};
"""
        return snippet
    
    def generate_reference_card(self, narrative_data: dict) -> str:
        """生成参考资料卡片"""
        sources = narrative_data.get("primary_sources", [])
        figures = narrative_data.get("figures", [])
        
        html = "<div class=\"reference-card\">\n"
        html += "  <h3>📜 史料参考</h3>\n"
        html += "  <ul>\n"
        for source in sources:
            html += f"    <li>《{source}》</li>\n"
        html += "  </ul>\n"
        
        if figures:
            html += "  <h4>关键人物</h4>\n"
            html += "  <ul>\n"
            for fig in figures[:5]:
                name = fig.get("name", "")
                title = fig.get("title", "")
                html += f"    <li>{name} {f'（{title}）' if title else ''}</li>\n"
            html += "  </ul>\n"
        
        html += "</div>\n"
        return html
    
    def save_outputs(self, card_data: CardData, narrative_data: dict = None):
        """保存所有输出文件"""
        os.makedirs(self.output_dir, exist_ok=True)
        
        level_id = card_data.level_id
        
        # 1. 保存游戏数据JSON
        game_json_path = os.path.join(self.output_dir, f"{level_id}_game.json")
        with open(game_json_path, 'w', encoding='utf-8') as f:
            json.dump({
                "id": card_data.level_id,
                "era": card_data.era,
                "name": card_data.level_name,
                "dilemma": card_data.dilemma,
                "protagonist": card_data.protagonist,
                "theme": card_data.css_theme,
                "scenes": card_data.scenes_json,
            }, f, ensure_ascii=False, indent=2)
        
        # 2. 保存游戏JS片段
        js_path = os.path.join(self.output_dir, f"{level_id}_level.js")
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_game_snippet(card_data))
        
        # 3. 保存关卡卡片HTML
        card_html_path = os.path.join(self.output_dir, f"{level_id}_card.html")
        with open(card_html_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_level_card_html(card_data))
        
        # 4. 保存参考卡片
        if narrative_data:
            ref_path = os.path.join(self.output_dir, f"{level_id}_reference.html")
            with open(ref_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_reference_card(narrative_data))
        
        return {
            "game_json": game_json_path,
            "game_js": js_path,
            "card_html": card_html_path,
            "reference_html": ref_path if narrative_data else None,
        }


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python cards.py <游戏数据JSON> [叙事数据JSON]")
        print("\n示例:")
        print("  python cards.py jingke_game_data.json jingke_story.json")
        return
    
    game_filepath = sys.argv[1]
    narrative_filepath = sys.argv[2] if len(sys.argv) > 2 else None
    
    with open(game_filepath, 'r', encoding='utf-8') as f:
        game_data = json.load(f)
    
    narrative_data = None
    if narrative_filepath:
        with open(narrative_filepath, 'r', encoding='utf-8') as f:
            narrative_data = json.load(f)
    
    generator = CardGenerator()
    card_data = generator.generate_card_data(game_data, narrative_data)
    
    outputs = generator.save_outputs(card_data, narrative_data)
    
    print("卡片数据已生成:")
    for key, path in outputs.items():
        if path:
            print(f"  {key}: {path}")


if __name__ == "__main__":
    main()
