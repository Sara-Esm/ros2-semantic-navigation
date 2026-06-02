# ROS 2 Semantic Navigation with YOLO + Sliding Mode Control

Autonomous cafe service robot with YOLOv8 person detection and Sliding Mode Control.

## Features
- Real-time YOLO detection (78-93% confidence)
- Sliding Mode Control for trajectory tracking
- Obstacle avoidance during approach
- State machine: SEARCHING → ALIGNING → APPROACHING → SERVING
- ROS 2 Humble, Gazebo 11

## Quick Start

### Build
```bash
cd ~/projects/ros2_semantic_nav
colcon build && source install/setup.bash
```

### Run

**Terminal 1:**
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch semantic_nav cafe_service_robot.launch.py target_object:=person
```

**Terminal 2:**
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 run semantic_nav obstacle_aware_controller
```

## Performance
- Detection: 78-93% confidence, 9.9 FPS
- Control: 20 Hz, SMC-based
- Approach speed: 0.15 m/s

## Files
- `yolo_detector_node.py` (164 lines)
- `obstacle_aware_controller.py` (220 lines)
- `cafe_service_robot.launch.py`

## Author
Sara Esmaeili - Robotics Software Engineer
8× Published | 104+ citations | ROS 2 · SMC · Nav2

## License
MIT

