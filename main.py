# type: ignore
import sys
import os
from pathlib import Path

# 添加 src 到路径
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    print("="*60)
    print("  数字人激光标记系统")
    print("  智谱GLM-4V视觉识别版")
    print("="*60)
    
    # 延迟导入，避免初始化错误
    try:
        from laser_detector import LaserDetector
        from content_analyzer import ContentAnalyzer
        from qa_generator import QAGenerator
        from knowledge_base import SimpleKnowledgeBase
        print("所有模块导入成功")
    except Exception as e:
        print(f"导入错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车退出...")
        return
    
    # 获取视频路径
    try:
        video_path = input("\n视频路径（拖入或输入）: ").strip().strip('"')
        
        if not video_path:
            print("错误：未输入路径")
            input("按回车退出...")
            return
            
        if not os.path.exists(video_path):
            print(f"错误：文件不存在 - {video_path}")
            input("按回车退出...")
            return
        
        # 选择激光颜色
        print("\n选择激光笔颜色：")
        print("  1. 自动检测（红绿都检测）")
        print("  2. 红色激光")
        print("  3. 绿色激光")
        color_choice = input("请输入选项（1/2/3，默认1）: ").strip()
        
        laser_color = "both"
        if color_choice == "2":
            laser_color = "red"
        elif color_choice == "3":
            laser_color = "green"
        
        # 获取视频背景
        print("\n视频主题/背景（帮助AI理解，可直接回车跳过）:")
        video_context = input("> ").strip()
        
        # 开始处理
        print(f"\n{'='*60}")
        print(f"开始处理: {os.path.basename(video_path)}")
        print(f"激光检测模式: {laser_color}")
        print(f"{'='*60}")
        
        # 初始化组件
        print("\n初始化组件...")
        try:
            detector = LaserDetector(laser_color=laser_color)
            analyzer = ContentAnalyzer()
            qa_gen = QAGenerator()
            kb = SimpleKnowledgeBase()
            print("组件初始化完成")
        except Exception as e:
            print(f"初始化错误: {e}")
            import traceback
            traceback.print_exc()
            input("按回车退出...")
            return
        
        # 检测激光
        print("\n【步骤1/3】检测激光标记...")
        try:
            segments = detector.extract_segments(video_path)
        except Exception as e:
            print(f"检测错误: {e}")
            import traceback
            traceback.print_exc()
            input("按回车退出...")
            return
        
        if not segments:
            print("未检测到激光标记，处理结束。")
            print("提示：请检查视频是否包含红色或绿色激光笔标记")
            input("按回车退出...")
            return
        
        print(f"检测到 {len(segments)} 个激光标记片段\n")
        
        # 逐个处理
        for i, seg in enumerate(segments, 1):
            print(f"\n{'─'*60}")
            print(f"【标记 {i}/{len(segments)}】{seg.start_time:.1f}s - {seg.end_time:.1f}s")
            print(f"{'─'*60}")
            
            # 截图
            print("步骤1：提取截图...")
            try:
                content = analyzer.analyze(video_path, seg, "output")
                print(f"  截图保存: {content['roi_path']}")
            except Exception as e:
                print(f"  截图错误: {e}")
                continue
            
            # 智谱分析
            print("\n步骤2：智谱GLM-4V分析图片中...")
            try:
                qa = qa_gen.analyze_image(
                    content['roi_path'],
                    content['timestamp'],
                    content['laser_duration']
                )
            except Exception as e:
                print(f"  AI分析错误: {e}")
                qa = {
                    "ai_description": f"【分析失败】{e}",
                    "question": f"【{content['timestamp']}】请查看截图，手动描述内容",
                    "ai_answer": "【待你回答】",
                    "confidence": "低",
                    "tags": ["分析失败"],
                    "key_point": "【待补充】"
                }
            
            # 显示结果
            print(f"\n{'='*60}")
            print("🤖 智谱看到的画面：")
            print(f"{qa['ai_description']}")
            print(f"{'='*60}")
            
            # 用户回答
            print(f"\n❓ {qa['question']}")
            try:
                your_answer = input("\n💡 你的回答（为什么标记这里，直接回车跳过）：\n> ").strip()
            except:
                your_answer = ""
            
            if your_answer:
                qa['ai_answer'] = your_answer
                qa['confidence'] = "已确认"
                
                # 标签
                try:
                    tags = input("\n🏷️ 标签（空格分隔，如：算法 重点，直接回车跳过）：\n> ").strip()
                    if tags:
                        qa['tags'] = tags.split()
                except:
                    pass
                
                # 关键点
                try:
                    key_point = input("\n🎯 一句话总结（直接回车跳过）：\n> ").strip()
                    if key_point:
                        qa['key_point'] = key_point
                except:
                    pass
            else:
                print("  （已跳过，可稍后补充）")
            
            # 保存
            try:
                entry_id = kb.add(os.path.basename(video_path), content, qa)
                print(f"\n✅ 已保存到知识库，ID: {entry_id}")
            except Exception as e:
                print(f"\n保存错误: {e}")
        
        print(f"\n{'='*60}")
        print(f"处理完成！共处理 {len(segments)} 个片段")
        print(f"数据保存在: output/qa_database.json")
        print(f"{'='*60}")
        
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n程序错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        input("\n按回车退出...")

if __name__ == "__main__":
    main()