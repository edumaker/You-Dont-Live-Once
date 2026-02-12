# type: ignore
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "src"))

from query_tool import QueryTool


def main():
    print("="*70)
    print("  知识库查询工具")
    print("="*70)
    
    tool = QueryTool()
    
    while True:
        print("\n请选择操作：")
        print("  1. 列出所有标记")
        print("  2. 关键词搜索")
        print("  3. 按标签搜索")
        print("  4. 查看指定ID详情")
        print("  5. 列出所有标签")
        print("  6. 查看未回答的标记")
        print("  7. 导出为 Markdown")
        print("  0. 退出")
        
        choice = input("\n> ").strip()
        
        if choice == "1":
            limit = input("显示数量（默认20，直接回车）：").strip()
            limit = int(limit) if limit.isdigit() else 20
            tool.list_all(limit=limit)
        
        elif choice == "2":
            keyword = input("请输入关键词：").strip()
            if keyword:
                tool.search(keyword)
        
        elif choice == "3":
            tag = input("请输入标签：").strip()
            if tag:
                tool.search_by_tag(tag)
        
        elif choice == "4":
            id_str = input("请输入ID：").strip()
            if id_str.isdigit():
                tool.get_by_id(int(id_str))
        
        elif choice == "5":
            tool.list_tags()
        
        elif choice == "6":
            tool.list_unanswered()
        
        elif choice == "7":
            tool.export_to_markdown()
        
        elif choice == "0":
            print("再见！")
            break
        
        else:
            print("无效选项，请重试")
        
        input("\n按回车继续...")


if __name__ == "__main__":
    main()