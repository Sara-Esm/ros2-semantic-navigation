# 🤖 ROS 2 Semantic Navigation with YOLO + Sliding Mode Control

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue)
![Gazebo](https://img.shields.io/badge/Gazebo-11-orange)
![YOLO](https://img.shields.io/badge/YOLOv8-Deep_Learning-red)
![License](https://img.shields.io/badge/License-MIT-brightgreen)

---

> An autonomous cafe service robot built with ROS 2 Humble, YOLOv8 deep learning, and Sliding Mode Control. The robot detects people in a simulated cafe environment using real-time object detection, autonomously aligns and approaches the target while avoiding obstacles — completing perception-driven navigation with zero human intervention.

---


## 📽️ Demo

<img width="1917" height="1027" alt="Demo-" src="https://github.com/user-attachments/assets/e132c9e6-014c-417a-a8bd-434bb51468bc" />


```
[INFO] [yolo_detector_node]: TARGET 'person' | err=+0.823 area=0.0933 conf=0.91
[INFO] [obstacle_aware_controller]: → Detected person! State: ALIGNING
[INFO] [obstacle_aware_controller]: → Aligned. State: APPROACHING
[INFO] [obstacle_aware_controller]: ⚠ OBSTACLE DETECTED - Avoiding! Turn: 0.40
[INFO] [obstacle_aware_controller]: ✓ Reached target. State: SERVING
```

---

## ✨ Features

- **Real-time YOLOv8 person detection** — deep learning-based perception at 78-93% confidence on CPU
- **Sliding Mode Control** — robust nonlinear controller with boundary layer for anti-chattering
- **Reactive obstacle avoidance** — autonomous heading correction during approach phase
- **State machine mission logic** — SEARCHING → ALIGNING → APPROACHING → SERVING transitions
- **Multi-node ROS 2 architecture** — modular perception-control pipeline with pub/sub topics
- **Custom Gazebo cafe world** — extended environment with people, tables, and obstacles
- **CPU-optimized** — runs without GPU on Intel i7-8565U at 9.9 FPS detection rate

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    semantic_nav                             │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │   Gazebo    │  │  YOLOv8n     │  │  Obstacle-Aware   │   │
│  │  Cafe World │  │  Detector    │  │  SMC Controller   │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬──────────┘   │
│         │                │                    │             │
│  ┌──────▼──────┐  ┌──────▼───────┐  ┌────────▼──────────┐   │
│  │ TurtleBot3  │  │ cv_bridge +  │  │  State Machine    │   │
│  │  waffle_pi  │  │ Ultralytics  │  │  + SMC Control    │   │
│  └──────┬──────┘  └──────────────┘  └───────────────────┘   │
│         │                                                   │
│  ┌──────▼──────────────────┐                                │
│  │   semantic_nav topics   │                                │
│  │  /camera/image_raw  →   │                                │
│  │  /semantic_nav/*    →   │                                │
│  └─────────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### ROS 2 Topic Graph

| Topic | Type | Description |
|---|---|---|
| `/camera/image_raw` | `sensor_msgs/Image` | Robot camera feed |
| `/semantic_nav/detected` | `std_msgs/Bool` | YOLO detection status |
| `/semantic_nav/object_name` | `std_msgs/String` | Detected object class |
| `/semantic_nav/normalized_error` | `std_msgs/Float32` | Lateral offset [-1, 1] |
| `/semantic_nav/target_area` | `std_msgs/Float32` | Bounding box size [0, 1] |
| `/semantic_nav/debug_image` | `sensor_msgs/Image` | Annotated detection feed |
| `/cmd_vel` | `geometry_msgs/Twist` | Robot velocity commands |
| `/odom` | `nav_msgs/Odometry` | Robot odometry |

---

## 📦 Package Structure

```
ros2_semantic_nav/
├── src/semantic_nav/                # Main ROS 2 package
│   ├── launch/
│   │   └── cafe_service_robot.launch.py   # Full system launch
│   ├── semantic_nav/
│   │   ├── yolo_detector_node.py          # YOLOv8 detection node
│   │   └── obstacle_aware_controller.py   # SMC controller node
│   ├── package.xml
│   ├── setup.py
│   └── setup.cfg
│
├── worlds/                          # Simulation environment
│   └── cafe_custom.world            # Extended cafe with obstacles
│
└── README.md
```

---

## 🎯 Robot Mission

The robot executes an autonomous service task using a 4-state state machine:

```
[START] Robot spawns at cafe entrance (0, 0)
    │
    ▼
[STATE 1] SEARCHING     → Rotate until person detected by YOLO
    │
    ▼
[STATE 2] ALIGNING      → SMC-controlled rotation to center target (|err| < 0.08)
    │
    ▼
[STATE 3] APPROACHING   → Forward motion + heading correction + obstacle avoidance
    │
    ▼
[STATE 4] SERVING       → Stopped at target, ready for interaction
    │
    ▼
[COMPLETE] Service task ready
```

Each state transition is validated by YOLO detection confidence and normalized error thresholds.

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Robot OS | ROS 2 Humble Hawksbill |
| Perception | YOLOv8 nano (Ultralytics) |
| Control | Sliding Mode Control (λ=1.5, k=0.5, φ=0.1) |
| Simulation | Gazebo Classic 11 |
| Computer Vision | OpenCV 4, cv_bridge |
| Robot Model | TurtleBot3 Waffle Pi |
| Language | Python 3 |
| Platform | Ubuntu 22.04 / WSL2 |

---

## 🚀 Getting Started

### Prerequisites

```bash
# ROS 2 Humble
sudo apt install ros-humble-desktop

# TurtleBot3
sudo apt install ros-humble-turtlebot3*

# Gazebo
sudo apt install ros-humble-gazebo-ros-pkgs

# OpenCV / CV Bridge
sudo apt install python3-opencv ros-humble-cv-bridge

# YOLOv8
pip3 install ultralytics
```

### Build

```bash
mkdir -p ~/projects/ros2_semantic_nav/src
cd ~/projects/ros2_semantic_nav/src
git clone https://github.com/Sara-Esm/ros2-semantic-navigation.git .

cd ~/projects/ros2_semantic_nav
colcon build
source install/setup.bash
```

### Run

**Terminal 1 — Launch full system (Gazebo + YOLO detector):**
```bash
export TURTLEBOT3_MODEL=waffle_pi
ros2 launch semantic_nav cafe_service_robot.launch.py target_object:=person
```

Wait ~10 seconds for Gazebo and YOLO model to initialize.

**Terminal 2 — Start autonomous SMC controller:**
```bash
source install/setup.bash
ros2 run semantic_nav obstacle_aware_controller
```

The robot will autonomously detect, align, approach, and stop at the target.

---

## 📊 Results

| Metric | Value |
|---|---|
| YOLO detection confidence | 78-93% |
| Detection rate (CPU only) | 9.9 FPS |
| Control loop frequency | 20 Hz |
| Processing latency | ~120 ms |
| Max linear velocity | 0.15 m/s |
| Max angular velocity | 0.8 rad/s |
| Approach success rate | 5/5 trials (100%) |

---

## 🔑 Key Implementation Details

**YOLO Detection** (`yolo_detector_node.py`)
- Subscribes to `/camera/image_raw`, publishes to `/semantic_nav/detected` and `/semantic_nav/normalized_error`
- Ultralytics YOLOv8n quantized model for CPU efficiency
- Real-time debug visualization window with bounding boxes and confidence
- Configurable target class via launch parameter (`person`, `dining table`, etc.)

**Sliding Mode Controller** (`obstacle_aware_controller.py`)
- Sliding surface: `s = λ·e` where `e` is normalized lateral error from YOLO
- Control law: `u = -k·sat(s/φ)` with boundary layer to prevent chattering
- 4-state state machine prevents oscillation between approach/serve states
- Obstacle avoidance via reactive heading offset during approach phase

**Custom Cafe World** (`cafe_custom.world`)
- Extended Gazebo cafe environment with 2 animated actors (people)
- 5 cafe tables and additional obstacle objects for navigation challenges
- Self-contained — no external Fuel server dependencies

---

## 🔭 Future Work

- [ ] LiDAR-based 360° obstacle detection
- [ ] RRT* path planning for global navigation
- [ ] Dynamic Window Approach (DWA) for smooth local planning
- [ ] Multi-target tracking and task prioritization
- [ ] Integration with Nav2 stack
- [ ] Hardware deployment on physical TurtleBot3
- [ ] Adaptive SMC with online parameter tuning
- [ ] Behavior tree-based mission management

---

## 👩‍💻 Author

**Sara Esmaeili** — Robotics Software Engineer  
GitHub: [@Sara-Esm](https://github.com/Sara-Esm)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
