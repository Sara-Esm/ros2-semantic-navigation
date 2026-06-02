import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    target_object = DeclareLaunchArgument("target_object", default_value="chair",
        description="YOLO target: chair | dining table | bottle | person")
    show_debug = DeclareLaunchArgument("show_debug", default_value="true")

    world_path = "/usr/share/gazebo-11/worlds/cafe.world"

    # Launch Gazebo with cafe world (built-in, no missing models!)
    gazebo = ExecuteProcess(
        cmd=["gazebo", "--verbose", world_path,
             "-s", "libgazebo_ros_init.so",
             "-s", "libgazebo_ros_factory.so"],
        output="screen"
    )

    # Spawn TurtleBot3 in the cafe
    spawn_turtlebot = TimerAction(
        period=6.0,
        actions=[
            ExecuteProcess(
                cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
                     "-entity", "waffle_pi",
                     "-file", "/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf",
                     "-x", "1.0", "-y", "0.0", "-z", "0.1"],
                output="screen"
            )
        ]
    )

    # YOLO detector
    yolo_node = TimerAction(
        period=10.0,
        actions=[
            Node(
                package="semantic_nav",
                executable="yolo_detector",
                name="yolo_detector_node",
                output="screen",
                parameters=[{
                    "target_object": LaunchConfiguration("target_object"),
                    "show_debug_window": LaunchConfiguration("show_debug"),
                    "confidence_threshold": 0.4,
                }]
            )
        ]
    )

    return LaunchDescription([target_object, show_debug, gazebo, spawn_turtlebot, yolo_node])
