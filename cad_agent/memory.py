# -*- coding: utf-8 -*-
import json
import os

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_memory.json")

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_memory(entries):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def add_example(user_input, spec):
    """
    保存一个成功的案例。
    为了防止重复和无限增长，我们可以只保留最近的 20 个，
    或者简单的去重。
    """
    entries = load_memory()
    
    # 简单去重：检查 user_input 是否已存在
    for entry in entries:
        if entry["input"] == user_input:
            return
            
    # 添加新条目
    entries.append({
        "input": user_input,
        "spec": spec
    })
    
    # 限制大小 (例如保留最近 50 条)
    if len(entries) > 50:
        entries = entries[-50:]
        
    save_memory(entries)

def get_examples(limit=3):
    """
    获取用于提示的示例。
    简单实现：返回最近的 limit 个。
    进阶实现：可以使用 embedding 搜索语义相似的案例。
    """
    entries = load_memory()
    # 返回最近的条目（反转列表）
    return entries[-limit:][::-1]
