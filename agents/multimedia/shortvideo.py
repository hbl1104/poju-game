#!/usr/bin/env python3
"""
多媒体转换Agent - 短视频文案生成器
将历史故事转换为适合短视频平台的文案
"""

import json
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class VideoScript:
    """视频脚本"""
    platform: str           # 平台: douyin/xiaohongshu/bilibili
    duration: int           # 时长(秒)
    hook: str               # 开头钩子(前3秒)
    body: List[str]         # 正文段落
    climax: str             # 高潮/转折
    cta: str                # 结尾互动
    bgm_suggestion: str     # BGM建议
    visual_notes: List[str] # 视觉提示


class ShortVideoGenerator:
    """短视频文案生成器"""
    
    # 平台特性
    PLATFORM_SPECS = {
        "douyin": {
            "duration": 30,
            "style": "快节奏、强情绪、口语化",
            "hook_style": "悬念/冲突/反常识",
            "max_chars": 200,
        },
        "xiaohongshu": {
            "duration": 60,
            "style": "知识感、故事性、共鸣",
            "hook_style": "问题/共鸣/好奇",
            "max_chars": 500,
        },
        "bilibili": {
            "duration": 180,
            "style": "深度、细节、历史感",
            "hook_style": "设问/悬念/历史厚重感",
            "max_chars": 1500,
        },
    }
    
    # BGM建议库
    BGM_LIBRARY = {
        "紧张": "《十面埋伏》/ 紧张鼓点",
        "悲壮": "《二泉映月》/ 低沉弦乐",
        "悬疑": "《倩女幽魂》/ 电子古风",
        "史诗": "《故宫》/ 大气管弦",
        "荒诞": "《疯狂原始人》/ 反差萌音乐",
    }
    
    def __init__(self):
        pass
    
    def generate(self, story_data: dict, platform: str = "douyin") -> VideoScript:
        """
        生成短视频文案
        
        Args:
            story_data: 故事数据
            platform: 目标平台
        """
        specs = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS["douyin"])
        
        protagonist = story_data.get("protagonist", "他")
        dilemma = story_data.get("dilemma_type", "困局")
        era = story_data.get("era", "")
        name = story_data.get("name", "")
        
        # 生成钩子
        hook = self._generate_hook(story_data, platform)
        
        # 生成正文
        body = self._generate_body(story_data, specs)
        
        # 生成高潮
        climax = self._generate_climax(story_data)
        
        # 生成CTA
        cta = self._generate_cta(story_data, platform)
        
        # BGM建议
        mood = self._detect_mood(story_data)
        bgm = self.BGM_LIBRARY.get(mood, "古风纯音乐")
        
        # 视觉提示
        visuals = self._generate_visuals(story_data, platform)
        
        return VideoScript(
            platform=platform,
            duration=specs["duration"],
            hook=hook,
            body=body,
            climax=climax,
            cta=cta,
            bgm_suggestion=bgm,
            visual_notes=visuals
        )
    
    def _generate_hook(self, story_data: dict, platform: str) -> str:
        """生成开头钩子"""
        protagonist = story_data.get("protagonist", "他")
        dilemma = story_data.get("dilemma_type", "困局")
        
        hooks = {
            "douyin": [
                f"{protagonist}面临{dilemma}，三个选择，选哪个都是死。",
                f"历史上最荒诞的救命方式，你绝对想不到。",
                f"{protagonist}：说真话是死，说假话也是死，我怎么活下来的？",
            ],
            "xiaohongshu": [
                f"{protagonist}的{dilemma}：历史最窒息的抉择时刻",
                f"如果你是{protagonist}，你会怎么选？",
                f"一个{dilemma}者的破局之道",
            ],
            "bilibili": [
                f"{story_data.get('era', '')}，{protagonist}面临一个不可能的选择。",
                f"从加缪的视角，重读{story_data.get('name', '这段历史')}。",
                f"{protagonist}：在荒诞中，如何找到破局之路？",
            ],
        }
        
        platform_hooks = hooks.get(platform, hooks["douyin"])
        return platform_hooks[0]
    
    def _generate_body(self, story_data: dict, specs: dict) -> List[str]:
        """生成正文"""
        body = []
        
        # 背景
        context = story_data.get("context", "")
        if context:
            body.append(context[:100] + "..." if len(context) > 100 else context)
        
        # 困局
        body.append(f"{story_data.get('protagonist', '主角')}面临{dilemma}困局。")
        
        # 选择
        choices = story_data.get("choices", [])
        for i, choice in enumerate(choices[:3]):
            labels = ["A.", "B.", "C."]
            body.append(f"{labels[i]} {choice.get('title', '选择')}")
        
        return body
    
    def _generate_climax(self, story_data: dict) -> str:
        """生成高潮"""
        breakthrough = story_data.get("breakthrough", "")
        if breakthrough:
            return breakthrough
        
        protagonist = story_data.get("protagonist", "他")
        return f"{protagonist}做出了一个反直觉的选择——"
    
    def _generate_cta(self, story_data: dict, platform: str) -> str:
        """生成结尾互动"""
        ctas = {
            "douyin": [
                "你会怎么选？评论区告诉我。",
                "如果是你，敢破局吗？",
                "点赞关注，下期更荒诞。",
            ],
            "xiaohongshu": [
                "你觉得{protagonist}的选择对吗？",
                "收藏这篇，下次写历史文案用得上。",
                "关注我，一起从历史中找答案。",
            ],
            "bilibili": [
                "一键三连，下期讲另一个破局故事。",
                "弹幕告诉我，如果你是{protagonist}，你会怎么选？",
                "关注这个系列，我们一起读历史。",
            ],
        }
        
        platform_ctas = ctas.get(platform, ctas["douyin"])
        return platform_ctas[0]
    
    def _detect_mood(self, story_data: dict) -> str:
        """检测故事氛围"""
        dilemma = story_data.get("dilemma_type", "")
        
        mood_map = {
            "被借刀杀人": "紧张",
            "骑墙困境": "悬疑",
            "承诺陷阱": "悲壮",
            "咫尺之局": "史诗",
        }
        
        return mood_map.get(dilemma, "紧张")
    
    def _generate_visuals(self, story_data: dict, platform: str) -> List[str]:
        """生成视觉提示"""
        era = story_data.get("era", "")
        location = story_data.get("location", "")
        
        visuals = [
            f"开场：{location}全景，暗色调",
            f"中段：人物特写，紧张表情",
            f"高潮：关键动作慢镜头",
        ]
        
        if "战国" in era:
            visuals.append("服饰：战国袍服，宽袖大带")
        elif "汉" in era or "曹魏" in era:
            visuals.append("服饰：汉服/魏晋风骨")
        elif "晋" in era:
            visuals.append("服饰：晋代宽袍大袖")
        
        return visuals
    
    def to_markdown(self, script: VideoScript) -> str:
        """转换为Markdown格式"""
        lines = []
        
        lines.append(f"# {script.platform} 短视频文案 ({script.duration}秒)\n")
        lines.append(f"**BGM建议**: {script.bgm_suggestion}\n")
        lines.append("\n## 开头钩子 (前3秒)\n")
        lines.append(f"> {script.hook}\n")
        lines.append("\n## 正文\n")
        for i, para in enumerate(script.body, 1):
            lines.append(f"{i}. {para}\n")
        lines.append("\n## 高潮/转折\n")
        lines.append(f"> {script.climax}\n")
        lines.append("\n## 结尾互动\n")
        lines.append(f"> {script.cta}\n")
        lines.append("\n## 视觉提示\n")
        for visual in script.visual_notes:
            lines.append(f"- {visual}\n")
        
        return "\n".join(lines)


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python shortvideo.py <故事JSON> [平台]")
        print("\n支持平台: douyin, xiaohongshu, bilibili")
        print("\n示例:")
        print("  python shortvideo.py jingke_story.json douyin")
        return
    
    filepath = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else "douyin"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        story_data = json.load(f)
    
    generator = ShortVideoGenerator()
    script = generator.generate(story_data, platform)
    
    md_output = generator.to_markdown(script)
    
    output_path = filepath.replace('.json', f'_{platform}.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)
    
    print(f"短视频文案已生成: {output_path}")
    print("\n预览:")
    print(md_output)


if __name__ == "__main__":
    main()
