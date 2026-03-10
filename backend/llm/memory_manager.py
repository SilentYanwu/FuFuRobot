# backend/llm/memory_manager.py
import json
import os
import threading
from pathlib import Path
from typing import Dict, List, Any
from backend.config import BASE_DIR

## 设置各类记忆的最大保存数量
# AI记住的用户长期事实
fact_num=40
# AI记住的用户最近动态
lastly_num=40
# AI记住的自己的AI状态信息
aistate_num=80
# AI记住的聊天上下文（30个对话，60条）
savedcontext_num=60

# 定义记忆文件路径
MEMORY_FILE = BASE_DIR / "user_memory.json"

class MemoryManager:
    _instance = None
    _lock = threading.Lock() # 线程锁，防止读写冲突

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """初始化加载记忆"""
        self.memory = {
            "user_profile": {},     # 用户画像：姓名、年龄、专业等
            "facts": [],            # 事实列表：用户发生过的事、喜好等
            "lately_things": [],    # 关于用户最近的动态
            "ai_state": [],         # AI 状态信息
            "saved_context": [],    # 保存的上次聊天上下文
            "summary": ""           # 总体摘要
        }
        self.load_memory()

    def load_memory(self):
        """从文件加载记忆"""
        with self._lock:
            if MEMORY_FILE.exists():
                try:
                    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.memory.update(data)
                except Exception as e:
                    print(f"Error loading memory: {e}")

    def save_memory(self):
        """保存记忆到文件"""
        with self._lock:
            try:
                with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                    json.dump(self.memory, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Error saving memory: {e}")

    def update_profile(self, key: str, value: str):
        """更新用户画像 (key 存在则覆盖)"""
        if not key or not value:
            return
        
        # 简单的去重逻辑：如果值一样就不更新
        if self.memory["user_profile"].get(key) == value:
            return
            
        print(f"🧠 [记忆更新] 画像: {key} = {value}")
        self.memory["user_profile"][key] = value
        self.save_memory()

    def add_fact(self, fact: str):
        """添加一条事实 (追加模式)"""
        if not fact:
            return
            
        # 简单的去重
        if fact in self.memory["facts"]:
            return
            
        print(f"🧠 [记忆更新] 事实: {fact}")
        self.memory["facts"].append(fact)
        # 限制事实数量
        if len(self.memory["facts"]) > fact_num:
            self.memory["facts"] = self.memory["facts"][(0-fact_num):]
            
        self.save_memory()

    def add_lately_thing(self, thing: str):
        """添加一条近期动态 (追加模式)"""
        if not thing:
            return
            
        # 简单的去重
        if thing in self.memory["lately_things"]:
            return
            
        print(f"🧠 [记忆更新] 近期动态: {thing}")
        self.memory["lately_things"].append(thing)
        # 限制近期动态数量
        if len(self.memory["lately_things"]) > lastly_num:
            self.memory["lately_things"] = self.memory["lately_things"][(0-lastly_num):]
            
        self.save_memory()
        
    def add_ai_state(self, state: str):
        """添加一条 AI 状态信息 (追加模式)"""
        if not state:
            return
            
        # 简单的去重
        if state in self.memory["ai_state"]:
            return
            
        print(f"🧠 [记忆更新] AI状态: {state}")
        self.memory["ai_state"].append(state)
        # 限制ai状态记忆数量，只保留最近40条
        if len(self.memory["ai_state"]) > aistate_num:
            self.memory["ai_state"] = self.memory["ai_state"][(0-aistate_num):]
        self.save_memory()
        
    def get_memory_context(self) -> str:
        """
        生成注入到 System Prompt 的上下文文本
        """
        context = []
        
        # 1. 构建用户画像部分
        if self.memory["user_profile"]:
            profile_str = ", ".join([f"{k}: {v}" for k, v in self.memory["user_profile"].items()])
            context.append(f"【用户基本资料】{profile_str}")
        
        # 2. 构建用户的事实记忆部分
        recent_facts = self.memory["facts"][(0-fact_num):]
        if recent_facts:
            facts_str = "; ".join(recent_facts)
            context.append(f"【你们的共同回忆/已知事实】{facts_str}")

        # 3. 构建近期动态部分
        recent_lately = self.memory["lately_things"][(0-lastly_num):]
        if recent_lately:
            lately_str = "; ".join(recent_lately)
            context.append(f"【用户近期动态】{lately_str}")
        
        # 4. 构建AI状态部分
        recent_states = self.memory["ai_state"][(0-aistate_num):]
        if recent_states:
            states_str = "; ".join(recent_states)
            context.append(f"【AI最近信息】{states_str}")


        return "\n" + "\n".join(context) + "\n"
    # 保存最近的聊天上下文
    def save_chat_context(self, history: List[Dict[str, str]]):
        """
        保存最近的聊天记录到 JSON
        只保留最后 savedcontext_num 条消息 (即 savedcontext_num/2 轮对话)
        这是用于填充下次的上下文内容，使对话完善。
        """
        if not history:
            return
        # 保留最后 savedcontextnum 条消息
        recent_context = history[(0-savedcontext_num):]
        
        # 只有当内容发生变化时才写入文件，减少IO
        if self.memory.get("saved_context") != recent_context:
            self.memory["saved_context"] = recent_context
            self.save_memory()
            # print(f"💾 [系统] 已保存最后 {len(recent_context)} 条对话上下文")

    # 获取保存的上下文
    def get_saved_context(self) -> List[Dict[str, str]]:
        """
        启动时获取上次保存的对话
        """
        return self.memory.get("saved_context", [])

# 创建全局实例
memory_manager = MemoryManager()