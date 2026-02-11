import cv2
import numpy as np
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class LaserSegment:
    start_time: float
    end_time: float
    laser_duration: float
    center_frame: int
    positions: List[Tuple[int, int]]
    trajectory_box: Tuple[int, int, int, int]

class LaserDetector:
    def __init__(self, laser_color="both"):
        self.laser_color = laser_color
        
        # 红色激光 HSV
        self.red_lower1 = (0, 100, 100)
        self.red_upper1 = (10, 255, 255)
        self.red_lower2 = (160, 100, 100)
        self.red_upper2 = (180, 255, 255)
        
        # 绿色激光 HSV
        self.green_lower = (35, 100, 100)
        self.green_upper = (85, 255, 255)
        
    def detect_frame(self, frame: np.ndarray) -> List[Tuple[int, int]]:
        """检测单帧中的激光点"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        masks = []
        
        if self.laser_color in ["red", "both"]:
            mask_red1 = cv2.inRange(hsv, self.red_lower1, self.red_upper1)
            mask_red2 = cv2.inRange(hsv, self.red_lower2, self.red_upper2)
            mask_red = cv2.bitwise_or(mask_red1, mask_red2)
            masks.append(mask_red)
        
        if self.laser_color in ["green", "both"]:
            mask_green = cv2.inRange(hsv, self.green_lower, self.green_upper)
            masks.append(mask_green)
        
        if len(masks) == 2:
            combined_mask = cv2.bitwise_or(masks[0], masks[1])
        else:
            combined_mask = masks[0]
        
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        points = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 5 < area < 1000:
                M = cv2.moments(cnt)
                if M["m00"] > 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    points.append((cx, cy))
        
        return points
    
    def extract_segments(self, video_path: str, sample_interval: int = 3,
                        min_laser_frames: int = 5, pre_context: float = 3.0,
                        post_context: float = 5.0, merge_gap: float = 1.0):
        """提取激光标记片段"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"无法打开视频: {video_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频信息: {total_frames}帧, {fps:.1f}fps, 时长{total_frames/fps:.1f}秒")
        
        laser_frames = []
        frame_idx = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % sample_interval == 0:
                points = self.detect_frame(frame)
                if points:
                    laser_frames.append({
                        'frame': frame_idx,
                        'time': frame_idx / fps,
                        'points': points
                    })
            
            frame_idx += 1
        
        cap.release()
        print(f"检测到 {len(laser_frames)} 个激光帧")
        
        if not laser_frames:
            return []
        
        # 聚类
        segments = []
        current_group = [laser_frames[0]]
        
        for i in range(1, len(laser_frames)):
            gap = laser_frames[i]['time'] - laser_frames[i-1]['time']
            if gap <= merge_gap:
                current_group.append(laser_frames[i])
            else:
                if len(current_group) >= min_laser_frames:
                    seg = self._create_segment(current_group, fps, total_frames, 
                                              pre_context, post_context)
                    segments.append(seg)
                current_group = [laser_frames[i]]
        
        if len(current_group) >= min_laser_frames:
            seg = self._create_segment(current_group, fps, total_frames,
                                      pre_context, post_context)
            segments.append(seg)
        
        print(f"提取了 {len(segments)} 个有效片段")
        return segments
    
    def _create_segment(self, group, fps, total_frames, pre_ctx, post_ctx):
        """创建片段"""
        start_time = max(0, group[0]['time'] - pre_ctx)
        end_time = min(total_frames/fps, group[-1]['time'] + post_ctx)
        
        all_positions = []
        for f in group:
            all_positions.extend(f['points'])
        
        # 计算边界框
        xs = [p[0] for p in all_positions]
        ys = [p[1] for p in all_positions]
        margin = 50
        trajectory_box = (
            max(0, min(xs) - margin),
            max(0, min(ys) - margin),
            min(1920, max(xs) + margin),
            min(1080, max(ys) + margin)
        )
        
        return LaserSegment(
            start_time=start_time,
            end_time=end_time,
            laser_duration=group[-1]['time'] - group[0]['time'],
            center_frame=group[len(group)//2]['frame'],
            positions=all_positions,
            trajectory_box=trajectory_box
        )