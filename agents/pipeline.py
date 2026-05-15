#!/usr/bin/env python3
"""
内容创作Agent - 总控流水线
协调所有Agent完成从史料到多媒体的完整工作流
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Optional


class ContentCreationPipeline:
    """内容创作流水线"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.project_root, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Agent路径
        self.historian_dir = os.path.join(self.project_root, "historian")
        self.storyteller_dir = os.path.join(self.project_root, "storyteller")
        self.multimedia_dir = os.path.join(self.project_root, "multimedia")
    
    def run_full_pipeline(self, event_id: str, event_data: dict = None) -> Dict[str, str]:
        """
        运行完整流水线
        
        流程：史料搜索 -> 信息提取 -> 史实校验 -> 叙事生成 -> 抉择设计 -> 卡片生成 -> 多媒体转换
        
        Args:
            event_id: 事件ID (如 "jingke", "caoshuang" 等)
            event_data: 可选的预设事件数据
        
        Returns:
            所有输出文件路径的字典
        """
        print(f"🚀 启动内容创作流水线: {event_id}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        outputs = {}
        
        # 步骤1: 史料搜索
        print("\n📚 步骤1: 史料搜索...")
        outputs["historian"] = self._run_historian(event_id, event_data)
        print(f"   ✓ 找到 {len(outputs['historian'].get('primary_sources', []))} 个史料来源")
        
        # 步骤2: 信息提取 (如果有故事文件)
        story_file = os.path.join(self.project_root, "..", "stories", f"{event_id}.md")
        if os.path.exists(story_file):
            print("\n🔍 步骤2: 信息提取...")
            outputs["extract"] = self._run_extractor(story_file)
            print(f"   ✓ 提取了 {len(outputs['extract'].get('figures', []))} 个人物")
            print(f"   ✓ 提取了 {len(outputs['extract'].get('decision_points', []))} 个决策点")
        
        # 步骤3: 史实校验
        if os.path.exists(story_file):
            print("\n✅ 步骤3: 史实校验...")
            outputs["verify"] = self._run_verifier(story_file)
            print(f"   ✓ 校验完成")
        
        # 步骤4: 叙事生成
        print("\n✍️ 步骤4: 叙事生成...")
        narrative_input = self._prepare_narrative_input(event_id, event_data, outputs)
        outputs["narrative"] = self._run_narrative_generator(narrative_input)
        print(f"   ✓ 故事已生成")
        
        # 步骤5: 抉择设计
        print("\n🎮 步骤5: 抉择设计...")
        outputs["choices"] = self._run_choice_designer(narrative_input)
        print(f"   ✓ 游戏场景已设计")
        
        # 步骤6: 卡片生成
        print("\n🃏 步骤6: 卡片生成...")
        outputs["cards"] = self._run_card_generator(outputs["choices"], outputs.get("extract"))
        print(f"   ✓ 游戏卡片已生成")
        
        # 步骤7: 多媒体转换
        print("\n📱 步骤7: 多媒体转换...")
        outputs["multimedia"] = self._run_multimedia_conversion(narrative_input)
        print(f"   ✓ 多媒体内容已生成")
        
        # 生成汇总报告
        print("\n" + "=" * 60)
        print("📊 流水线完成!")
        self._generate_report(event_id, outputs)
        
        return outputs
    
    def _run_historian(self, event_id: str, event_data: dict = None) -> dict:
        """运行史料搜索Agent"""
        search_script = os.path.join(self.historian_dir, "search.py")
        
        if event_data:
            # 使用预设数据
            return event_data
        
        # 运行搜索脚本
        try:
            result = subprocess.run(
                [sys.executable, search_script, event_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"   ⚠️ 搜索失败: {e}")
        
        # 返回默认数据
        return {"event_id": event_id, "sources": []}
    
    def _run_extractor(self, story_file: str) -> dict:
        """运行信息提取Agent"""
        extract_script = os.path.join(self.historian_dir, "extract.py")
        
        try:
            result = subprocess.run(
                [sys.executable, extract_script, story_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"   ⚠️ 提取失败: {e}")
        
        return {}
    
    def _run_verifier(self, story_file: str) -> dict:
        """运行史实校验Agent"""
        verify_script = os.path.join(self.historian_dir, "verify.py")
        
        try:
            result = subprocess.run(
                [sys.executable, verify_script, story_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                # 读取生成的JSON报告
                report_file = story_file.replace('.md', '_verification.json')
                if os.path.exists(report_file):
                    with open(report_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
        except Exception as e:
            print(f"   ⚠️ 校验失败: {e}")
        
        return {}
    
    def _prepare_narrative_input(self, event_id: str, event_data: dict, outputs: dict) -> dict:
        """准备叙事生成器的输入数据"""
        # 合并所有已知信息
        narrative_input = {
            "event_id": event_id,
            "name": event_data.get("name", ""),
            "era": event_data.get("era", ""),
            "location": event_data.get("location", ""),
            "protagonist": event_data.get("protagonist", ""),
            "dilemma_type": event_data.get("dilemma_type", ""),
            "context": event_data.get("context", ""),
            "breakthrough": event_data.get("breakthrough", ""),
            "historical_note": event_data.get("historical_note", ""),
            "sources": event_data.get("sources", []),
            "antagonist": event_data.get("antagonist", ""),
            "role_in_trap": event_data.get("role_in_trap", "棋子"),
            "duty": event_data.get("duty", ""),
            "object": event_data.get("object", "手中的东西"),
            "choices": event_data.get("choices", []),
        }
        
        # 保存为临时JSON
        temp_file = os.path.join(self.output_dir, f"{event_id}_input.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(narrative_input, f, ensure_ascii=False, indent=2)
        
        return narrative_input
    
    def _run_narrative_generator(self, narrative_input: dict) -> dict:
        """运行叙事生成Agent"""
        narrative_script = os.path.join(self.storyteller_dir, "narrative.py")
        temp_file = os.path.join(self.output_dir, f"{narrative_input['event_id']}_input.json")
        
        try:
            result = subprocess.run(
                [sys.executable, narrative_script, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                output_file = temp_file.replace('_input.json', '_story.md')
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        return {"story_md": f.read(), "path": output_file}
        except Exception as e:
            print(f"   ⚠️ 叙事生成失败: {e}")
        
        return {}
    
    def _run_choice_designer(self, narrative_input: dict) -> dict:
        """运行抉择设计Agent"""
        choices_script = os.path.join(self.storyteller_dir, "choices.py")
        temp_file = os.path.join(self.output_dir, f"{narrative_input['event_id']}_input.json")
        
        try:
            result = subprocess.run(
                [sys.executable, choices_script, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                output_file = temp_file.replace('_input.json', '_game_data.json')
                if os.path.exists(output_file):
                    with open(output_file, 'r', encoding='utf-8') as f:
                        return {"game_data": json.load(f), "path": output_file}
        except Exception as e:
            print(f"   ⚠️ 抉择设计失败: {e}")
        
        return {}
    
    def _run_card_generator(self, game_data: dict, narrative_data: dict = None) -> dict:
        """运行卡片生成Agent"""
        cards_script = os.path.join(self.multimedia_dir, "cards.py")
        
        # game_data是choices.py的输出，包含 {"game_data": {...}, "path": ...}
        actual_game_data = game_data.get("game_data", game_data)
        event_id = actual_game_data.get("id", "unknown")
        
        # 使用正确的路径
        game_data_path = os.path.join(self.output_dir, f"{event_id}_game_data.json")
        
        # 先保存game_data到文件（如果还没有）
        if not os.path.exists(game_data_path):
            with open(game_data_path, 'w', encoding='utf-8') as f:
                json.dump(actual_game_data, f, ensure_ascii=False, indent=2)
        
        try:
            cmd = [sys.executable, cards_script, game_data_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return {"status": "success", "output": result.stdout}
        except Exception as e:
            print(f"   ⚠️ 卡片生成失败: {e}")
        
        return {}
    
    def _run_multimedia_conversion(self, narrative_input: dict) -> dict:
        """运行多媒体转换Agent"""
        temp_file = os.path.join(self.output_dir, f"{narrative_input['event_id']}_input.json")
        
        results = {}
        
        # 短视频文案
        shortvideo_script = os.path.join(self.multimedia_dir, "shortvideo.py")
        for platform in ["douyin", "xiaohongshu", "bilibili"]:
            try:
                result = subprocess.run(
                    [sys.executable, shortvideo_script, temp_file, platform],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    results[f"shortvideo_{platform}"] = "success"
            except Exception as e:
                print(f"   ⚠️ {platform}文案生成失败: {e}")
        
        # 社交媒体内容
        social_script = os.path.join(self.multimedia_dir, "social.py")
        for platform in ["wechat", "xiaohongshu", "zhihu", "weibo"]:
            try:
                result = subprocess.run(
                    [sys.executable, social_script, temp_file, platform],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    results[f"social_{platform}"] = "success"
            except Exception as e:
                print(f"   ⚠️ {platform}内容生成失败: {e}")
        
        return results
    
    def _generate_report(self, event_id: str, outputs: dict):
        """生成汇总报告"""
        report_file = os.path.join(self.output_dir, f"{event_id}_report.md")
        
        lines = []
        lines.append(f"# 内容创作报告: {event_id}")
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("\n## 输出文件\n")
        
        # 列出所有输出文件
        output_files = []
        for category, data in outputs.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, str) and os.path.exists(value):
                        output_files.append(f"- `{value}`")
        
        if output_files:
            lines.extend(output_files)
        else:
            lines.append("- 输出文件在 `agents/output/` 目录中")
        
        lines.append("\n## 内容概览\n")
        
        if "narrative" in outputs:
            lines.append("- ✅ 加缪式叙事故事")
        if "choices" in outputs:
            lines.append("- ✅ 游戏抉择分支")
        if "cards" in outputs:
            lines.append("- ✅ 游戏卡片数据")
        if "multimedia" in outputs:
            lines.append("- ✅ 多媒体内容（短视频+社交媒体）")
        
        lines.append("\n## 使用方式\n")
        lines.append("1. 游戏数据: 将 `_game_data.json` 和 `_level.js` 导入游戏引擎")
        lines.append("2. 故事文本: `_story.md` 可直接发布")
        lines.append("3. 短视频: `_*_douyin.md` 等平台文案可直接使用")
        lines.append("4. 社交媒体: `_*_wechat.md` 等平台内容可直接发布")
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        print(f"\n📄 报告已保存: {report_file}")
    
    def discover_and_create(self, era: str = None, theme: str = None) -> List[dict]:
        """
        发现新的历史事件并创建内容
        
        Args:
            era: 时代筛选
            theme: 主题筛选
        
        Returns:
            候选事件列表
        """
        print(f"🔍 发现新的破局故事素材...")
        
        search_script = os.path.join(self.historian_dir, "search.py")
        
        try:
            cmd = [sys.executable, search_script, "discover"]
            if theme:
                cmd.extend(["--theme", theme])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                candidates = json.loads(result.stdout)
                print(f"   发现 {len(candidates)} 个候选事件")
                for c in candidates:
                    print(f"   - {c['name']} ({c['era']}) - {c['theme']}")
                return candidates
        except Exception as e:
            print(f"   ⚠️ 发现失败: {e}")
        
        return []


def main():
    """CLI入口"""
    if len(sys.argv) < 2:
        print("用法: python pipeline.py <命令> [参数]")
        print("\n命令:")
        print("  create <事件ID>     - 为已知事件创建完整内容")
        print("  discover           - 发现新的候选事件")
        print("\n示例:")
        print("  python pipeline.py create jingke")
        print("  python pipeline.py discover --theme 骑墙困境")
        return
    
    command = sys.argv[1]
    pipeline = ContentCreationPipeline()
    
    if command == "create":
        if len(sys.argv) < 3:
            print("错误: 需要指定事件ID")
            return
        
        event_id = sys.argv[2]
        
        # 加载已知事件数据
        from historian.search import KNOWN_EVENTS
        event_data = KNOWN_EVENTS.get(event_id)
        
        if not event_data:
            print(f"错误: 未知事件 '{event_id}'")
            print(f"已知事件: {', '.join(KNOWN_EVENTS.keys())}")
            return
        
        # 补充完整的事件数据格式
        full_event_data = {
            "event_id": event_id,
            "name": event_data.get("name", ""),
            "era": event_data.get("era", ""),
            "location": "咸阳宫大殿",
            "protagonist": "夏无且",
            "dilemma_type": "咫尺之局",
            "context": "荆轲刺秦王，殿上群臣无兵器，殿外武士无诏不得上殿。夏无且是秦宫侍医，手无寸铁。",
            "breakthrough": "掷出药囊，创造一秒的时间差",
            "historical_note": "《史记·刺客列传》记载：'是时侍医夏无且以其所奉药囊提荆轲。'",
            "sources": event_data.get("sources", []),
            "key_figures": event_data.get("key_figures", []),
            "keywords": event_data.get("keywords", []),
            "antagonist": "荆轲",
            "role_in_trap": "旁观者",
            "duty": "在秦王不适时递上一丸药",
            "object": "一只粗布药囊",
        }
        
        outputs = pipeline.run_full_pipeline(event_id, full_event_data)
        print("\n✅ 所有内容已生成!")
    
    elif command == "discover":
        theme = None
        if "--theme" in sys.argv:
            idx = sys.argv.index("--theme")
            theme = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        
        candidates = pipeline.discover_and_create(theme=theme)
        
        if candidates:
            print("\n要为哪个事件创建内容？")
            print("运行: python pipeline.py create <事件ID>")
    
    else:
        print(f"未知命令: {command}")


if __name__ == "__main__":
    main()
