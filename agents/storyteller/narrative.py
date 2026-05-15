#!/usr/bin/env python3
"""
故事生成Agent - 加缪式叙事生成器
将史料转换为破局游戏风格的加缪式叙事
"""

import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class NarrativeScene:
    """叙事场景"""
    title: str
    content: str
    mood: str = ""          # 氛围: 紧张/荒诞/沉重/希望
    philosophical_note: str = ""  # 哲学注脚


@dataclass
class NarrativeStory:
    """完整叙事"""
    event_id: str
    title: str
    era: str
    location: str
    protagonist: str
    dilemma_type: str
    scenes: List[NarrativeScene]
    decision_points: List[dict]
    historical_note: str
    philosophical_theme: str


class CamusNarrativeGenerator:
    """加缪式叙事生成器"""
    
    # 加缪式开头模板
    OPENING_TEMPLATES = [
        "{protagonist}站在那儿，{posture}。",
        "{protagonist}不知道{object}的重量。",
        "{location}很安静。{protagonist}看着这一切，感到一种熟悉的荒谬。",
        "{protagonist}是{title}，职责是{duty}。",
    ]
    
    # 加缪式哲学引用
    CAMUS_QUOTES = [
        "真正严肃的哲学问题只有一个，那就是自杀。",
        "荒诞诞生于人类的呼唤与世界的不合理沉默之间的对峙。",
        "习惯是死亡的温床。",
        "人必须想象西西弗斯是幸福的。",
        "自由就是认识到荒诞，并在荒诞中继续生活。",
        "反抗赋予生命以价值。",
        "荒诞不在于人，也不在于世界，而在于两者共同存在。",
    ]
    
    # 困局类型映射
    DILEMMA_TYPES = {
        "被借刀杀人": {
            "theme": "工具化",
            "philosophy": "你的存在本身，就是死亡的原因。",
            "opening_mood": "被利用的荒谬",
        },
        "骑墙困境": {
            "theme": "选择的不可能性",
            "philosophy": "任何明确的选择都是错的。",
            "opening_mood": "夹缝中的窒息",
        },
        "承诺陷阱": {
            "theme": "信任的代价",
            "philosophy": "相信荒诞会对你仁慈。",
            "opening_mood": "温柔的绞索",
        },
        "咫尺之局": {
            "theme": "微小行动的意义",
            "philosophy": "即使是最微不足道的人，也能在最荒诞的时刻，做出最不荒诞的选择。",
            "opening_mood": "瞬间的永恒",
        },
        "信息差陷阱": {
            "theme": "知识的诅咒",
            "philosophy": "你知道的越多，能做的越少。",
            "opening_mood": "清醒的无力",
        },
        "时间压力": {
            "theme": "时间的暴政",
            "philosophy": "时间不是你的盟友，是对手的武器。",
            "opening_mood": "倒计时的窒息",
        },
        "道德两难": {
            "theme": "伦理的深渊",
            "philosophy": "没有正确的选择，只有不同的代价。",
            "opening_mood": "良知的撕裂",
        },
    }
    
    def __init__(self):
        self.story = None
    
    def generate(self, event_data: dict, style: str = "camus") -> NarrativeStory:
        """
        根据事件数据生成加缪式叙事
        
        Args:
            event_data: 包含事件基本信息的字典
            style: 叙事风格 (camus/absurdist/existential)
        """
        event_id = event_data.get("event_id", "unknown")
        name = event_data.get("name", "")
        era = event_data.get("era", "")
        location = event_data.get("location", "")
        protagonist = event_data.get("protagonist", "")
        dilemma_type = event_data.get("dilemma_type", "")
        
        dilemma_info = self.DILEMMA_TYPES.get(dilemma_type, self.DILEMMA_TYPES["被借刀杀人"])
        
        scenes = []
        
        # 场景一：开场（存在主义引入）
        opening = self._generate_opening(protagonist, location, event_data)
        scenes.append(NarrativeScene(
            title="一、{location}".format(location=location.split("·")[0].strip() if "·" in location else location),
            content=opening,
            mood=dilemma_info["opening_mood"],
            philosophical_note="加缪说：\"{quote}\"".format(quote=dilemma_info["philosophy"])
        ))
        
        # 场景二：困局展开
        complication = self._generate_complication(event_data)
        scenes.append(NarrativeScene(
            title="二、困局",
            content=complication,
            mood="紧张",
            philosophical_note=""
        ))
        
        # 场景三：三种荒诞（抉择分支）
        choices = self._generate_choices(event_data)
        scenes.append(NarrativeScene(
            title="三、三种荒诞",
            content=choices,
            mood="荒诞",
            philosophical_note=""
        ))
        
        # 场景四：破局者说
        resolution = self._generate_resolution(event_data)
        scenes.append(NarrativeScene(
            title="四、破局",
            content=resolution,
            mood="顿悟",
            philosophical_note=""
        ))
        
        # 场景五：历史的注脚
        epilogue = self._generate_epilogue(event_data)
        scenes.append(NarrativeScene(
            title="五、历史的注脚",
            content=epilogue,
            mood="沉重",
            philosophical_note=""
        ))
        
        return NarrativeStory(
            event_id=event_id,
            title=name,
            era=era,
            location=location,
            protagonist=protagonist,
            dilemma_type=dilemma_type,
            scenes=scenes,
            decision_points=event_data.get("decision_points", []),
            historical_note=event_data.get("historical_note", ""),
            philosophical_theme=dilemma_info["philosophy"]
        )
    
    def _generate_opening(self, protagonist: str, location: str, event_data: dict) -> str:
        """生成开场"""
        title = event_data.get("title", "")
        duty = event_data.get("duty", "在这个位置上")
        object_name = event_data.get("object", "手中的东西")
        
        template = self.OPENING_TEMPLATES[0]
        opening = template.format(
            protagonist=protagonist,
            posture="手里提着{object}".format(object=object_name),
            object=object_name,
            location=location,
            title=title,
            duty=duty
        )
        
        # 添加存在主义引入
        opening += "\n\n他不知道{object}的重量。".format(object=object_name)
        opening += "\n\n{location}很安静。".format(location=location)
        opening += "\n\n{protagonist}看着这一切，感到一种熟悉的荒谬。".format(protagonist=protagonist)
        
        return opening
    
    def _generate_complication(self, event_data: dict) -> str:
        """生成困局展开"""
        context = event_data.get("context", "")
        antagonist = event_data.get("antagonist", "")
        
        text = context if context else "局势突然变化。"
        
        if antagonist:
            text += "\n\n{antagonist}已经准备好了。".format(antagonist=antagonist)
        
        text += "\n\n{protagonist}忽然明白了：自己就是这个局的{role}。".format(
            protagonist=event_data.get("protagonist", ""),
            role=event_data.get("role_in_trap", "棋子")
        )
        
        return text
    
    def _generate_choices(self, event_data: dict) -> str:
        """生成三种荒诞选择"""
        choices = event_data.get("choices", [])
        
        if not choices:
            return self._generate_default_choices(event_data)
        
        text = ""
        labels = ["第一种荒诞", "第二种荒诞", "第三种荒诞"]
        
        for i, choice in enumerate(choices[:3]):
            label = labels[i] if i < len(labels) else f"第{i+1}种荒诞"
            text += "\n\n**{label}：{title}**\n\n".format(label=label, title=choice.get("title", ""))
            text += choice.get("description", "")
            text += "\n\n这是最{adjective}的荒诞——{conclusion}。".format(
                adjective=choice.get("adjective", "典型"),
                conclusion=choice.get("conclusion", "行动本身否定了行动的意义")
            )
        
        return text
    
    def _generate_default_choices(self, event_data: dict) -> str:
        """生成默认的三种选择"""
        protagonist = event_data.get("protagonist", "你")
        dilemma = event_data.get("dilemma_type", "困局")
        
        text = ""
        
        # 选择一：顺从
        text += "\n\n**第一种荒诞：顺从。**\n\n"
        text += "{protagonist}选择了接受。".format(protagonist=protagonist)
        text += "\n\n这是最普遍的荒诞——相信荒诞会对你仁慈。"
        
        # 选择二：逃避
        text += "\n\n**第二种荒诞：逃避。**\n\n"
        text += "{protagonist}选择了观望。".format(protagonist=protagonist)
        text += "\n\n这是最懦弱的荒诞——用拖延来逃避选择，但选择不会因此消失。"
        
        # 选择三：破局
        text += "\n\n**第三种荒诞：破局。**\n\n"
        text += "{protagonist}选择了行动。".format(protagonist=protagonist)
        text += "\n\n这不是英雄主义。这是存在主义——在毫无意义的处境中，赋予行动以意义。"
        
        return text
    
    def _generate_resolution(self, event_data: dict) -> str:
        """生成破局者说"""
        protagonist = event_data.get("protagonist", "")
        dilemma = event_data.get("dilemma_type", "")
        breakthrough = event_data.get("breakthrough", "")
        
        text = "{protagonist}的破局，不是因为他比别人更勇敢，也不是因为他比别人更聪明。".format(protagonist=protagonist)
        text += "\n\n他的破局，是因为他接受了荒诞——"
        
        if breakthrough:
            text += "{breakthrough}".format(breakthrough=breakthrough)
        else:
            text += "接受了\"我只有一个选择\"这个事实，然后问了一个别人没有问的问题。"
        
        text += "\n\n加缪说：\"人必须想象西西弗斯是幸福的。\""
        text += "\n\n{protagonist}不需要想象。他在做出选择的那一刻，已经触摸到了那种幸福。".format(protagonist=protagonist)
        
        return text
    
    def _generate_epilogue(self, event_data: dict) -> str:
        """生成历史注脚"""
        sources = event_data.get("sources", [])
        historical_outcome = event_data.get("historical_outcome", "")
        
        text = ""
        
        if sources:
            text += "《{source}》记载：\"{quote}\"\n\n".format(
                source=sources[0],
                quote=event_data.get("source_quote", "")
            )
        
        if historical_outcome:
            text += historical_outcome
        
        text += "\n\n这就是荒诞——行动的意义，往往在行动之外。"
        
        return text
    
    def to_markdown(self, story: NarrativeStory) -> str:
        """将叙事转换为Markdown格式"""
        lines = []
        
        lines.append("# {title}\n".format(title=story.title))
        lines.append("## 基础信息\n")
        lines.append("- **时代**：{era}\n".format(era=story.era))
        lines.append("- **地点**：{location}\n".format(location=story.location))
        lines.append("- **主角**：{protagonist}\n".format(protagonist=story.protagonist))
        lines.append("- **困局**：{dilemma}\n".format(dilemma=story.dilemma_type))
        lines.append("\n---\n")
        lines.append("## 加缪式故事正文\n")
        
        for scene in story.scenes:
            lines.append("\n### {title}\n".format(title=scene.title))
            lines.append("\n{content}\n".format(content=scene.content))
            if scene.philosophical_note:
                lines.append("\n*{note}*\n".format(note=scene.philosophical_note))
        
        lines.append("\n---\n")
        lines.append("## 衍生创作素材\n")
        lines.append("\n### 短视频文案（30秒）\n")
        lines.append(self._generate_short_video_script(story))
        lines.append("\n### 小红书图文标题\n")
        for title in self._generate_xiaohongshu_titles(story):
            lines.append("- {title}\n".format(title=title))
        lines.append("\n### 公众号文章标题\n")
        for title in self._generate_wechat_titles(story):
            lines.append("- {title}\n".format(title=title))
        
        return "".join(lines)
    
    def _generate_short_video_script(self, story: NarrativeStory) -> str:
        """生成短视频文案"""
        lines = [
            "\n> {protagonist}面临{dilemma}。".format(protagonist=story.protagonist, dilemma=story.dilemma_type),
            "> 顺从？死。逃避？死。",
            "> 他选择了第三种。",
            "> 不是英雄主义，是存在主义。",
            "> 在荒诞中，赋予行动以意义。",
            "> 你的{dilemma}是什么？".format(dilemma=story.dilemma_type),
        ]
        return "\n".join(lines)
    
    def _generate_xiaohongshu_titles(self, story: NarrativeStory) -> List[str]:
        """生成小红书标题"""
        return [
            "《{protagonist}的{dilemma}：历史最荒诞的抉择》".format(protagonist=story.protagonist, dilemma=story.dilemma_type),
            "《说顺从是死，说逃避也是死，他怎么活下来的》".format(),
            "《{era}，一个{dilemma}者的破局之道》".format(era=story.era.split("·")[0].strip() if "·" in story.era else story.era, dilemma=story.dilemma_type),
        ]
    
    def _generate_wechat_titles(self, story: NarrativeStory) -> List[str]:
        """生成公众号标题"""
        return [
            "《{title}：{protagonist}如何在荒诞中，找到了破局之路》".format(title=story.title, protagonist=story.protagonist),
            "《当{dilemma}成为死局：{protagonist}的存在主义选择》".format(dilemma=story.dilemma_type, protagonist=story.protagonist),
            "《{era}的荒诞与破局：从加缪的视角重读历史》".format(era=story.era.split("·")[0].strip() if "·" in story.era else story.era),
        ]


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python narrative.py <事件JSON文件>")
        print("\n示例:")
        print("  python narrative.py event_data.json")
        return
    
    filepath = sys.argv[1]
    with open(filepath, 'r', encoding='utf-8') as f:
        event_data = json.load(f)
    
    generator = CamusNarrativeGenerator()
    story = generator.generate(event_data)
    
    md_output = generator.to_markdown(story)
    
    output_path = filepath.replace('_input.json', '_story.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)
    
    print(f"故事已生成: {output_path}")
    print("\n预览:")
    print(md_output[:1000] + "...")


if __name__ == "__main__":
    main()
