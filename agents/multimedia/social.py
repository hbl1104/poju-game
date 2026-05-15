#!/usr/bin/env python3
"""
多媒体转换Agent - 社交媒体内容生成器
生成适合不同平台的社交媒体内容
"""

import json
import sys
from dataclasses import dataclass
from typing import List


@dataclass
class SocialContent:
    """社交媒体内容"""
    platform: str
    title: str
    body: str
    hashtags: List[str]
    image_prompt: str
    engagement_tips: List[str]


class SocialMediaGenerator:
    """社交媒体内容生成器"""
    
    # 平台特性
    PLATFORM_CONFIG = {
        "wechat": {
            "max_length": 2000,
            "style": "深度、故事性、知识感",
            "format": "长文",
            "hashtag_style": "无",
        },
        "xiaohongshu": {
            "max_length": 1000,
            "style": "轻松、共鸣、种草感",
            "format": "图文",
            "hashtag_style": "#标签",
        },
        "zhihu": {
            "max_length": 3000,
            "style": "专业、分析、论证",
            "format": "回答/文章",
            "hashtag_style": "话题",
        },
        "weibo": {
            "max_length": 500,
            "style": "简洁、热点、情绪",
            "format": "短博文",
            "hashtag_style": "#话题#",
        },
    }
    
    def __init__(self):
        pass
    
    def generate(self, story_data: dict, platform: str = "wechat") -> SocialContent:
        """生成社交媒体内容"""
        config = self.PLATFORM_CONFIG.get(platform, self.PLATFORM_CONFIG["wechat"])
        
        # 生成标题
        title = self._generate_title(story_data, platform)
        
        # 生成正文
        body = self._generate_body(story_data, platform, config)
        
        # 生成标签
        hashtags = self._generate_hashtags(story_data, platform)
        
        # 生成配图提示
        image_prompt = self._generate_image_prompt(story_data)
        
        # 生成互动建议
        engagement = self._generate_engagement_tips(platform)
        
        return SocialContent(
            platform=platform,
            title=title,
            body=body,
            hashtags=hashtags,
            image_prompt=image_prompt,
            engagement_tips=engagement
        )
    
    def _generate_title(self, story_data: dict, platform: str) -> str:
        """生成标题"""
        name = story_data.get("name", "")
        protagonist = story_data.get("protagonist", "")
        dilemma = story_data.get("dilemma_type", "")
        era = story_data.get("era", "").split("·")[0].strip() if "·" in story_data.get("era", "") else story_data.get("era", "")
        
        titles = {
            "wechat": [
                f"{protagonist}的{dilemma}：{name}背后的存在主义选择",
                f"从加缪的视角，重读{name}",
                f"{era}的荒诞与破局：{protagonist}如何在绝境中找到生路",
            ],
            "xiaohongshu": [
                f"{protagonist}的{dilemma}，我哭了😭",
                f"历史上最窒息的抉择，{protagonist}怎么选？",
                f"{era}｜一个{dilemma}者的破局之道",
            ],
            "zhihu": [
                f"如何评价{name}中{protagonist}的选择？",
                f"{name}：一场关于{dilemma}的存在主义实验",
                f"从{name}看{dilemma}的破局逻辑",
            ],
            "weibo": [
                f"#{protagonist}#{dilemma}# 如果是你，怎么选？",
                f"{name}：{protagonist}的{dilemma}，结局让人唏嘘",
                f"#{era}# {protagonist}面临{dilemma}，他的选择绝了",
            ],
        }
        
        platform_titles = titles.get(platform, titles["wechat"])
        return platform_titles[0]
    
    def _generate_body(self, story_data: dict, platform: str, config: dict) -> str:
        """生成正文"""
        protagonist = story_data.get("protagonist", "")
        dilemma = story_data.get("dilemma_type", "")
        context = story_data.get("context", "")
        
        if platform == "wechat":
            return self._generate_wechat_body(story_data)
        elif platform == "xiaohongshu":
            return self._generate_xiaohongshu_body(story_data)
        elif platform == "zhihu":
            return self._generate_zhihu_body(story_data)
        elif platform == "weibo":
            return self._generate_weibo_body(story_data)
        
        return context
    
    def _generate_wechat_body(self, story_data: dict) -> str:
        """生成公众号文章正文"""
        lines = []
        
        lines.append(f"## 一、{story_data.get('era', '')}的{dilemma}困局")
        lines.append("")
        lines.append(story_data.get("context", ""))
        lines.append("")
        lines.append(f"## 二、{story_data.get('protagonist', '主角')}的三种选择")
        lines.append("")
        
        choices = story_data.get("choices", [])
        for i, choice in enumerate(choices[:3]):
            labels = ["第一种荒诞", "第二种荒诞", "第三种荒诞"]
            lines.append(f"**{labels[i]}：{choice.get('title', '')}**")
            lines.append("")
            lines.append(choice.get("description", ""))
            lines.append("")
        
        lines.append("## 三、破局者说")
        lines.append("")
        lines.append(story_data.get("breakthrough", "破局的核心，是让对手的借口失效。"))
        lines.append("")
        lines.append("## 四、历史的注脚")
        lines.append("")
        lines.append(story_data.get("historical_note", ""))
        
        return "\n".join(lines)
    
    def _generate_xiaohongshu_body(self, story_data: dict) -> str:
        """生成小红书正文"""
        lines = []
        
        lines.append(f"姐妹们，今天讲一个超窒息的历史故事😭")
        lines.append("")
        lines.append(f"{story_data.get('protagonist', '主角')}面临{dilemma}困局")
        lines.append("")
        lines.append("三个选择：")
        choices = story_data.get("choices", [])
        for i, choice in enumerate(choices[:3]):
            emojis = ["😨", "😰", "😎"]
            lines.append(f"{emojis[i]} {choice.get('title', '')}")
        lines.append("")
        lines.append(f"最后他选择了：{story_data.get('breakthrough', '破局')}")
        lines.append("")
        lines.append("如果是你，会怎么选？")
        lines.append("")
        lines.append("#历史 #破局 #选择困难症 #加缪 #存在主义")
        
        return "\n".join(lines)
    
    def _generate_zhihu_body(self, story_data: dict) -> str:
        """生成知乎回答正文"""
        lines = []
        
        lines.append(f"**先说结论**：{story_data.get('protagonist', '主角')}的破局之道，不是更聪明的谋略，而是接受荒诞。")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 背景分析")
        lines.append("")
        lines.append(story_data.get("context", ""))
        lines.append("")
        lines.append("## 抉择分析")
        lines.append("")
        
        choices = story_data.get("choices", [])
        for choice in choices[:3]:
            lines.append(f"### {choice.get('title', '')}")
            lines.append("")
            lines.append(choice.get("description", ""))
            lines.append("")
            lines.append(f"**结果**：{choice.get('conclusion', '')}")
            lines.append("")
        
        lines.append("## 历史评价")
        lines.append("")
        lines.append(story_data.get("historical_note", ""))
        
        return "\n".join(lines)
    
    def _generate_weibo_body(self, story_data: dict) -> str:
        """生成微博正文"""
        lines = []
        
        lines.append(f"{story_data.get('protagonist', '主角')}的{dilemma}困局：")
        lines.append("")
        lines.append(story_data.get("context", "")[:100] + "...")
        lines.append("")
        lines.append(f"最后他选择了：{story_data.get('breakthrough', '破局')}")
        lines.append("")
        lines.append("如果是你，会怎么选？")
        
        return "\n".join(lines)
    
    def _generate_hashtags(self, story_data: dict, platform: str) -> List[str]:
        """生成标签"""
        era = story_data.get("era", "").split("·")[0].strip() if "·" in story_data.get("era", "") else story_data.get("era", "")
        dilemma = story_data.get("dilemma_type", "")
        
        base_tags = [
            era,
            dilemma,
            "破局",
            "历史",
            "存在主义",
            "加缪",
        ]
        
        if platform == "weibo":
            return [f"#{tag}#" for tag in base_tags]
        elif platform == "xiaohongshu":
            return [f"#{tag}" for tag in base_tags]
        elif platform == "zhihu":
            return [f"{tag}" for tag in base_tags]
        
        return base_tags
    
    def _generate_image_prompt(self, story_data: dict) -> str:
        """生成AI配图提示词"""
        protagonist = story_data.get("protagonist", "")
        era = story_data.get("era", "")
        location = story_data.get("location", "")
        dilemma = story_data.get("dilemma_type", "")
        
        style = "中国古风插画，水墨风格，暗色调"
        
        if "战国" in era:
            costume = "战国袍服，宽袖大带"
        elif "汉" in era or "曹魏" in era:
            costume = "汉服，魏晋风骨"
        elif "晋" in era:
            costume = "晋代宽袍大袖"
        else:
            costume = "古代服饰"
        
        prompt = f"{style}，{location}，{protagonist}身穿{costume}，面临{dilemma}困局的紧张时刻，戏剧性光影，电影感构图"
        
        return prompt
    
    def _generate_engagement_tips(self, platform: str) -> List[str]:
        """生成互动建议"""
        tips = {
            "wechat": [
                "在文末设置投票：你会怎么选？",
                "引导读者在评论区分享自己的\"破局\"经历",
                "设置悬念：下期讲另一个更荒诞的故事",
            ],
            "xiaohongshu": [
                "在评论区回复前10条评论",
                "用\"如果是你\"引发共鸣",
                "配合情绪化的封面图",
            ],
            "zhihu": [
                "在回答中引用史料，增强可信度",
                "邀请读者补充其他历史视角",
                "关联相关历史问题",
            ],
            "weibo": [
                "设置投票功能",
                "@相关历史博主互动",
                "配合热搜话题发布",
            ],
        }
        
        return tips.get(platform, [])
    
    def to_markdown(self, content: SocialContent) -> str:
        """转换为Markdown"""
        lines = []
        
        lines.append(f"# {content.platform} 内容方案\n")
        lines.append(f"**标题**：{content.title}\n")
        lines.append(f"**配图提示**：{content.image_prompt}\n")
        lines.append("\n## 正文\n")
        lines.append(content.body)
        lines.append("\n## 标签\n")
        lines.append(" ".join(content.hashtags))
        lines.append("\n## 互动建议\n")
        for tip in content.engagement_tips:
            lines.append(f"- {tip}")
        
        return "\n".join(lines)


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python social.py <故事JSON> [平台]")
        print("\n支持平台: wechat, xiaohongshu, zhihu, weibo")
        print("\n示例:")
        print("  python social.py jingke_story.json wechat")
        return
    
    filepath = sys.argv[1]
    platform = sys.argv[2] if len(sys.argv) > 2 else "wechat"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        story_data = json.load(f)
    
    generator = SocialMediaGenerator()
    content = generator.generate(story_data, platform)
    
    md_output = generator.to_markdown(content)
    
    output_path = filepath.replace('.json', f'_{platform}.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)
    
    print(f"社交媒体内容已生成: {output_path}")
    print("\n预览:")
    print(md_output[:500] + "...")


if __name__ == "__main__":
    main()
