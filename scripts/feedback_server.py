#!/usr/bin/env python3
"""
破局游戏反馈收集服务
接收前端反馈并写入飞书多维表格
"""

import json
import os
import sys
from datetime import datetime
from urllib import request, parse, error

# 飞书应用凭证（从环境变量读取）
FEISHU_APP_ID = os.environ.get('FEISHU_APP_ID', '')
FEISHU_APP_SECRET = os.environ.get('FEISHU_APP_SECRET', '')

# 飞书表格配置
FEISHU_BITABLE_TOKEN = os.environ.get('FEISHU_BITABLE_TOKEN', '')  # 多维表格的 app_token
FEISHU_TABLE_ID = os.environ.get('FEISHU_TABLE_ID', '')  # 表格ID

FEEDBACK_FILE = os.path.expanduser("~/.hermes/scripts/poju_feedback.json")


def get_feishu_token():
    """获取飞书 tenant_access_token"""
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        return None
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = json.dumps({
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }).encode('utf-8')
    
    req = request.Request(url, data=data, headers={
        'Content-Type': 'application/json'
    }, method='POST')
    
    try:
        with request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            if result.get('code') == 0:
                return result.get('tenant_access_token')
    except Exception as e:
        print(f"Get token error: {e}")
    
    return None


def write_to_bitable(token, feedback):
    """写入飞书多维表格"""
    if not FEISHU_BITABLE_TOKEN or not FEISHU_TABLE_ID:
        return False
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BITABLE_TOKEN}/tables/{FEISHU_TABLE_ID}/records"
    
    # 构建记录数据
    fields = {
        "时间": feedback.get('timestamp', datetime.now().isoformat()),
        "关卡": feedback.get('level', '未知'),
        "优先级": feedback.get('priority', 'P2'),
        "反馈内容": feedback.get('content', '')[:500],  # 限制长度
        "场景": feedback.get('scene', ''),
        "用户代理": feedback.get('userAgent', '')[:200],
        "URL": feedback.get('url', '')
    }
    
    data = json.dumps({"fields": fields}).encode('utf-8')
    
    req = request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }, method='POST')
    
    try:
        with request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result.get('code') == 0
    except Exception as e:
        print(f"Write to bitable error: {e}")
        return False


def save_local(feedback):
    """保存到本地文件"""
    feedbacks = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
        except:
            pass
    
    feedbacks.append(feedback)
    
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)
    
    return True


def main():
    """主函数 - 读取本地反馈并同步到飞书"""
    if not os.path.exists(FEEDBACK_FILE):
        print("No feedback file found")
        return
    
    try:
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
    except Exception as e:
        print(f"Read feedback file error: {e}")
        return
    
    if not feedbacks:
        print("No feedback to sync")
        return
    
    # 获取飞书token
    token = get_feishu_token()
    if not token:
        print("Failed to get Feishu token, saving locally only")
        return
    
    # 同步到飞书
    success_count = 0
    for feedback in feedbacks:
        if write_to_bitable(token, feedback):
            success_count += 1
    
    print(f"Synced {success_count}/{len(feedbacks)} feedbacks to Feishu")
    
    # 清空已同步的反馈（可选）
    # with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
    #     json.dump([], f)


if __name__ == '__main__':
    main()
