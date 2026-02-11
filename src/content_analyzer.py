import cv2
import os
from typing import Dict

class ContentAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, video_path: str, segment, output_dir: str) -> Dict:
        """提取激光标记区域的截图"""
        cap = cv2.VideoCapture(video_path)
        
        # 取激光中间帧
        cap.set(cv2.CAP_PROP_POS_FRAMES, segment.center_frame)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            raise ValueError("无法读取帧")
        
        # 保存截图
        os.makedirs(f"{output_dir}/keyframes", exist_ok=True)
        
        # 原图
        raw_path = f"{output_dir}/keyframes/frame_{segment.center_frame}_raw.jpg"
        cv2.imwrite(raw_path, frame)
        
        # 激光区域放大图
        roi = self._extract_roi(frame, segment.trajectory_box)
        roi_path = f"{output_dir}/keyframes/frame_{segment.center_frame}_roi.jpg"
        cv2.imwrite(roi_path, roi)
        
        return {
            'raw_path': raw_path,
            'roi_path': roi_path,
            'timestamp': f"{segment.start_time:.1f}s - {segment.end_time:.1f}s",
            'laser_duration': segment.laser_duration,
            'start_time': segment.start_time,
            'end_time': segment.end_time,
        }
    
    def _extract_roi(self, frame, trajectory_box):
        """提取激光区域并放大"""
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = trajectory_box
        
        # 扩大50%边距
        margin_x = int((x2 - x1) * 0.5)
        margin_y = int((y2 - y1) * 0.5)
        
        x1 = max(0, int(x1) - margin_x)
        y1 = max(0, int(y1) - margin_y)
        x2 = min(w, int(x2) + margin_x)
        y2 = min(h, int(y2) + margin_y)
        
        roi = frame[y1:y2, x1:x2]
        
        # 放大2倍
        if roi.size > 0:
            roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        return roi