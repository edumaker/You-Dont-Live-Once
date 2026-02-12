import json
import os
from typing import List, Dict
from datetime import datetime


class QueryTool:
    def __init__(self, db_path: str = "output/qa_database.json"):
        self.db_path = db_path
        self.data = self._load()
    
    def _load(self) -> List[Dict]:
        """加载知识库"""
        if not os.path.exists(self.db_path):
            print(f"知识库不存在: {self.db_path}")
            return []
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_all(self, limit: int = 20):
        """列出所有标记"""
        if not self.data:
            print("知识库为空")
            return
        
        print(f"\n{'='*70}")
        print(f"共有 {len(self.data)} 条记录（显示前 {min(limit, len(self.data))} 条）")
        print(f"{'='*70}")
        
        for entry in self.data[:limit]:
            self._print_entry(entry)
    
    def search(self, keyword: str):
        """关键词搜索"""
        if not self.data:
            print("知识库为空")
            return
        
        results = []
        keyword_lower = keyword.lower()
        
        for entry in self.data:
            # 搜索多个字段
            searchable_text = (
                entry.get('ai_description', '') +
                entry.get('your_answer', '') +
                entry.get('key_point', '') +
                ' '.join(entry.get('tags', [])) +
                entry.get('video_file', '')
            ).lower()
            
            if keyword_lower in searchable_text:
                results.append(entry)
        
        if not results:
            print(f"\n未找到包含 '{keyword}' 的记录")
            return
        
        print(f"\n{'='*70}")
        print(f"找到 {len(results)} 条包含 '{keyword}' 的记录")
        print(f"{'='*70}")
        
        for entry in results:
            self._print_entry(entry)
    
    def search_by_tag(self, tag: str):
        """按标签搜索"""
        if not self.data:
            print("知识库为空")
            return
        
        results = [e for e in self.data if tag in e.get('tags', [])]
        
        if not results:
            print(f"\n未找到标签为 '{tag}' 的记录")
            return
        
        print(f"\n{'='*70}")
        print(f"找到 {len(results)} 条标签为 '{tag}' 的记录")
        print(f"{'='*70}")
        
        for entry in results:
            self._print_entry(entry)
    
    def get_by_id(self, entry_id: int):
        """按 ID 查看详情"""
        entry = next((e for e in self.data if e['id'] == entry_id), None)
        
        if not entry:
            print(f"未找到 ID 为 {entry_id} 的记录")
            return
        
        self._print_entry(entry, detailed=True)
    
    def list_tags(self):
        """列出所有标签"""
        all_tags = set()
        for entry in self.data:
            all_tags.update(entry.get('tags', []))
        
        if not all_tags:
            print("暂无标签")
            return
        
        print(f"\n{'='*70}")
        print(f"共有 {len(all_tags)} 个标签：")
        print(f"{'='*70}")
        
        # 统计每个标签的数量
        tag_counts = {}
        for tag in all_tags:
            count = sum(1 for e in self.data if tag in e.get('tags', []))
            tag_counts[tag] = count
        
        # 按数量排序
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {tag}: {count} 条记录")
    
    def list_unanswered(self):
        """列出未回答的标记"""
        unanswered = [e for e in self.data if e.get('confidence') != '已确认']
        
        if not unanswered:
            print("所有标记都已回答")
            return
        
        print(f"\n{'='*70}")
        print(f"有 {len(unanswered)} 条未回答的标记")
        print(f"{'='*70}")
        
        for entry in unanswered:
            self._print_entry(entry)
    
    def _print_entry(self, entry: Dict, detailed: bool = False):
        """打印单条记录"""
        status = "✅" if entry.get('confidence') == '已确认' else "⏳"
        
        print(f"\n{status} [{entry['id']}] {entry['timestamp']}")
        print(f"   视频: {entry.get('video_file', '未知')}")
        
        # 截断描述
        desc = entry.get('ai_description', '无描述')[:100]
        if len(entry.get('ai_description', '')) > 100:
            desc += "..."
        print(f"   AI描述: {desc}")
        
        # 你的回答
        answer = entry.get('your_answer', '未回答')
        if answer and answer != '【待你回答】':
            answer_preview = answer[:80]
            if len(answer) > 80:
                answer_preview += "..."
            print(f"   你的回答: {answer_preview}")
        
        # 标签和关键点
        tags = entry.get('tags', [])
        if tags and tags != ['待分类']:
            print(f"   标签: {', '.join(tags)}")
        
        key_point = entry.get('key_point', '')
        if key_point and key_point != '【待你总结】':
            print(f"   关键点: {key_point}")
        
        # 详细模式显示完整信息
        if detailed:
            print(f"\n   完整AI描述:\n   {entry.get('ai_description', '无')}")
            print(f"\n   完整回答:\n   {entry.get('your_answer', '无')}")
            print(f"   截图: {entry.get('screenshot', '无')}")
        
        print(f"   {'─'*60}")
    
    def export_to_markdown(self, output_path: str = "output/knowledge_base.md"):
        """导出为 Markdown 文件"""
        if not self.data:
            print("知识库为空，无法导出")
            return
        
        lines = [
            "# 激光标记知识库\n",
            f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"总记录数: {len(self.data)}\n\n",
            "---\n\n"
        ]
        
        for entry in self.data:
            lines.append(f"## [{entry['id']}] {entry['timestamp']}\n\n")
            lines.append(f"**视频**: {entry.get('video_file', '未知')}\n\n")
            lines.append(f"**AI描述**:\n{entry.get('ai_description', '无')}\n\n")
            
            answer = entry.get('your_answer', '未回答')
            if answer and answer != '【待你回答】':
                lines.append(f"**我的回答**:\n{answer}\n\n")
            
            tags = entry.get('tags', [])
            if tags and tags != ['待分类']:
                lines.append(f"**标签**: {', '.join(tags)}\n\n")
            
            key_point = entry.get('key_point', '')
            if key_point and key_point != '【待你总结】':
                lines.append(f"**关键点**: {key_point}\n\n")
            
            lines.append("---\n\n")
        
        # 保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"\n已导出到: {output_path}")