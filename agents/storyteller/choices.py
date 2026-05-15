#!/usr/bin/env python3
"""
故事生成Agent - 抉择分支设计器
为历史事件设计游戏化的抉择分支
"""

import json
import sys
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class GameChoice:
    """游戏选项"""
    text: str               # 选项文字
    tag: str                # 标签
    next_scene: str         # 下一个场景ID
    result_type: str        # 结果类型: win/win_alt/neutral/lose
    historical_accuracy: str  # 历史准确性: accurate/plausible/fictional
    parenthetical: str = ""  # 括号注释（历史背景）
    philosophical_note: str = ""  # 哲学注脚


@dataclass
class GameScene:
    """游戏场景"""
    scene_id: str
    text: str               # HTML格式的故事文本
    choices: List[GameChoice]
    result: str = ""        # 结局类型
    history_note: str = ""  # 历史注脚
    is_end: bool = False    # 是否结局场景


@dataclass
class LevelData:
    """关卡数据"""
    id: str
    era: str
    name: str
    desc: str
    tag: str
    scenes: List[GameScene]


class ChoiceDesigner:
    """抉择分支设计师"""
    
    # 困局类型对应的选择模板
    CHOICE_TEMPLATES = {
        "被借刀杀人": {
            "options": [
                {"text": "如实禀报", "tag": "诚实", "result": "lose", "accuracy": "accurate"},
                {"text": "推辞不往", "tag": "逃避", "result": "neutral", "accuracy": "plausible"},
                {"text": "让诊断复杂化", "tag": "破局", "result": "win", "accuracy": "plausible"},
            ],
            "parentheticals": [
                "（历史上，如实禀报的御医往往成为替罪羊）",
                "（推辞虽能自保，但无法阻止悲剧发生）",
                "（用医学的复杂性，让政治的简单性失效）",
            ]
        },
        "骑墙困境": {
            "options": [
                {"text": "全力响应", "tag": "激进", "result": "lose", "accuracy": "accurate"},
                {"text": "守州自保", "tag": "观望", "result": "lose", "accuracy": "accurate"},
                {"text": "制造竞价局面", "tag": "破局", "result": "win", "accuracy": "plausible"},
            ],
            "parentheticals": [
                "（全力响应会导致家人被杀）",
                "（观望会被愤怒的部下所杀）",
                "（让两边都需要你，比选一边站更安全）",
            ]
        },
        "承诺陷阱": {
            "options": [
                {"text": "相信承诺", "tag": "天真", "result": "lose", "accuracy": "accurate"},
                {"text": "犹豫不决", "tag": "拖延", "result": "lose", "accuracy": "accurate"},
                {"text": "挟天子以令诸侯", "tag": "破局", "result": "win", "accuracy": "plausible"},
            ],
            "parentheticals": [
                "（历史上，曹爽相信洛水之誓后被夷三族）",
                "（犹豫不是谨慎，是送给对手的礼物）",
                "（手握天子、军队、粮草，不需要谈判）",
            ]
        },
        "咫尺之局": {
            "options": [
                {"text": "扑上去", "tag": "勇敢", "result": "lose", "accuracy": "plausible"},
                {"text": "大喊提醒", "tag": "机智", "result": "win_alt", "accuracy": "accurate"},
                {"text": "掷出药囊", "tag": "破局", "result": "win", "accuracy": "accurate"},
            ],
            "parentheticals": [
                "（手无寸铁扑向刺客，等于送死）",
                "（历史上，有人大喊\"王负剑\"，秦王拔剑反击）",
                "（夏无且以药囊掷荆轲，创造了一秒的时间差）",
            ]
        },
    }
    
    def design_choices(self, event_data: dict) -> List[GameScene]:
        """
        为事件设计完整的游戏场景和抉择分支
        """
        dilemma_type = event_data.get("dilemma_type", "被借刀杀人")
        template = self.CHOICE_TEMPLATES.get(dilemma_type, self.CHOICE_TEMPLATES["被借刀杀人"])
        
        scenes = []
        
        # 场景1：起始场景
        scenes.append(GameScene(
            scene_id="start",
            text=self._format_scene_text(event_data, "start"),
            choices=[
                GameChoice(
                    text=opt["text"],
                    tag=opt["tag"],
                    next_scene=f"choice_{i}",
                    result_type=opt["result"],
                    historical_accuracy=opt["accuracy"],
                    parenthetical=template["parentheticals"][i] if i < len(template["parentheticals"]) else ""
                )
                for i, opt in enumerate(template["options"])
            ]
        ))
        
        # 为每个选择创建后续场景
        for i, opt in enumerate(template["options"]):
            scene_id = f"choice_{i}"
            
            if opt["result"] == "win":
                scenes.append(self._create_win_scene(event_data, scene_id, opt))
            elif opt["result"] == "win_alt":
                scenes.append(self._create_win_alt_scene(event_data, scene_id, opt))
            elif opt["result"] == "neutral":
                scenes.append(self._create_neutral_scene(event_data, scene_id, opt))
            else:
                scenes.append(self._create_lose_scene(event_data, scene_id, opt))
        
        # 添加重试场景
        scenes.append(GameScene(
            scene_id="retry",
            text="你失败了。但历史允许假设。\n\n再试一次？",
            choices=[
                GameChoice(
                    text="回到起点",
                    tag="重试",
                    next_scene="start",
                    result_type="",
                    historical_accuracy=""
                )
            ],
            is_end=False
        ))
        
        return scenes
    
    def _create_win_scene(self, event_data: dict, scene_id: str, option: dict) -> GameScene:
        """创建胜利场景"""
        protagonist = event_data.get("protagonist", "你")
        
        text = "{protagonist}做出了正确的选择。\n\n".format(protagonist=protagonist)
        text += "这不是最体面的胜利，但你活下来了。\n\n"
        text += "**破局者说**：\n"
        text += "破局的核心，不是提供\"更好\"的方案，而是让对手的借口\"失效\"。\n\n"
        text += "在荒诞的世界里，不被利用，本身就是一种胜利。"
        
        return GameScene(
            scene_id=scene_id,
            text=text,
            choices=[],
            result="win",
            history_note=event_data.get("historical_note", ""),
            is_end=True
        )
    
    def _create_win_alt_scene(self, event_data: dict, scene_id: str, option: dict) -> GameScene:
        """创建替代胜利场景"""
        text = "你活下来了，但代价不菲。\n\n"
        text += "历史记住了你——但记住的方式，不是你想要的。\n\n"
        text += "**历史注脚**：\n"
        text += "这是另一种荒诞——你参与了历史，但历史没有记住你。"
        
        return GameScene(
            scene_id=scene_id,
            text=text,
            choices=[],
            result="win_alt",
            history_note="",
            is_end=True
        )
    
    def _create_neutral_scene(self, event_data: dict, scene_id: str, option: dict) -> GameScene:
        """创建中性场景"""
        text = "你选择了逃避。\n\n"
        text += "你活下来了，但未能阻止悲剧。\n\n"
        text += "这是另一种荒诞——不参与，不等于不存在。\n"
        text += "你的逃避只是让别人成为了刀。"
        
        return GameScene(
            scene_id=scene_id,
            text=text,
            choices=[
                GameChoice(
                    text="再试一次",
                    tag="重试",
                    next_scene="start",
                    result_type="",
                    historical_accuracy=""
                )
            ],
            result="neutral",
            is_end=False
        )
    
    def _create_lose_scene(self, event_data: dict, scene_id: str, option: dict) -> GameScene:
        """创建失败场景"""
        text = "你做出了错误的选择。\n\n"
        text += "这是最纯粹的荒诞——行动本身否定了行动的意义。\n\n"
        text += "**历史注脚**：\n"
        text += "在权力的游戏中，天真和犹豫是最致命的弱点。"
        
        return GameScene(
            scene_id=scene_id,
            text=text,
            choices=[
                GameChoice(
                    text="回到起点",
                    tag="重试",
                    next_scene="start",
                    result_type="",
                    historical_accuracy=""
                )
            ],
            result="lose",
            is_end=False
        )
    
    def _format_scene_text(self, event_data: dict, scene_type: str) -> str:
        """格式化场景文本"""
        if scene_type == "start":
            return event_data.get("opening_text", "故事开始了...")
        return ""
    
    def to_game_data(self, event_data: dict) -> dict:
        """转换为游戏关卡数据格式"""
        scenes = self.design_choices(event_data)
        
        level_data = {
            "id": event_data.get("event_id", "unknown"),
            "era": event_data.get("era", ""),
            "name": event_data.get("name", ""),
            "desc": event_data.get("summary", ""),
            "tag": event_data.get("dilemma_type", ""),
            "scenes": []
        }
        
        for scene in scenes:
            scene_data = {
                "id": scene.scene_id,
                "text": scene.text,
                "choices": [
                    {
                        "text": c.text,
                        "next": c.next_scene,
                        "tag": c.tag,
                        "parenthetical": c.parenthetical
                    }
                    for c in scene.choices
                ],
                "result": scene.result,
                "historyNote": scene.history_note,
                "isEnd": scene.is_end
            }
            level_data["scenes"].append(scene_data)
        
        return level_data


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python choices.py <事件JSON文件>")
        return
    
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        event_data = json.load(f)
    
    designer = ChoiceDesigner()
    game_data = designer.to_game_data(event_data)
    
    output_path = filepath.replace('_input.json', '_game_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, ensure_ascii=False, indent=2)
    
    print(f"游戏数据已生成: {output_path}")
    print(f"\n共 {len(game_data['scenes'])} 个场景")
    for scene in game_data['scenes']:
        print(f"  - {scene['id']}: {len(scene['choices'])} 个选项, 结局: {scene['result']}")


if __name__ == "__main__":
    main()
