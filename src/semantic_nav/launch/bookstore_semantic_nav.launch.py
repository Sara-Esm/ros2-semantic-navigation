import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    target_object = DeclareLaunchArgument("target_object", default_value="chair",
        description="YOLO target: chair | person | bottle | book | potted plant")
    show_debug = DeclareLaunchArgument("show_debug", default_value="true")

    world_path = os.path.expanduser("~/aws_ws/src/aws-robomaker-bookstore-world/worlds/bookstore.world")

    # Launch Gazebo with bookstore world
    gazebo = ExecuteProcess(
        cmd=["gazebo", "--verbose", world_path, "-s", "libgazebo_ros_init.so", "-s", "libgazebo_ros_factory.so"],
        output="screen"
    )

    # Spawn TurtleBot3 after Gazebo starts
    turtlebot3_pkg = get_package_share_directory("turtlebot3_gazebo")
    spawn_turtlebot = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(turtlebot3_pkg, "launch", "spawn_turtlebot3.launch.py")
                ),
                launch_arguments={
                    "x_pose": "0.0",
                    "y_pose": "0.0",
                }.items()
            )
        ]
    )

    # YOLO detector
    yolo_node = TimerAction(
        period=8.0,
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
