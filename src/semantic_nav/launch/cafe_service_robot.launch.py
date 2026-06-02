import os
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    target_object = DeclareLaunchArgument("target_object", default_value="person",
        description="YOLO target object (person, dining table, etc)")
    
    gazebo = ExecuteProcess(
        cmd=["gazebo", "--verbose", os.path.expanduser("~/projects/ros2_semantic_nav/worlds/cafe_custom.world"),
             "-s", "libgazebo_ros_init.so", "-s", "libgazebo_ros_factory.so"],
        output="screen"
    )

    spawn_turtlebot = TimerAction(period=6.0, actions=[
        ExecuteProcess(
            cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
                 "-entity", "waffle_pi",
                 "-file", "/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf",
                 "-x", "0.0", "-y", "0.0", "-z", "0.1"],
            output="screen"
        )
    ])

    yolo_detector = TimerAction(period=10.0, actions=[
        Node(
            package="semantic_nav",
            executable="yolo_detector",
            name="yolo_detector_node",
            output="screen",
            parameters=[{
                "target_object": LaunchConfiguration("target_object"),
                "show_debug_window": True,
                "confidence_threshold": 0.4,
            }]
        )
    ])

    return LaunchDescription([target_object, gazebo, spawn_turtlebot, yolo_detector])
