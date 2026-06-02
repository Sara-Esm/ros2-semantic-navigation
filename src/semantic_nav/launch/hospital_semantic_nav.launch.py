import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction, SetEnvironmentVariable, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    target_object = DeclareLaunchArgument("target_object", default_value="chair",
        description="YOLO target: chair | person | bottle | tv | etc")
    show_debug = DeclareLaunchArgument("show_debug", default_value="true")

    hospital_pkg  = os.path.expanduser("~/aws-robomaker-hospital-world")
    world_path    = os.path.join(hospital_pkg, "worlds", "hospital.world")
    models_path   = os.path.join(hospital_pkg, "models")
    fuel_path     = os.path.join(hospital_pkg, "fuel_models")

    # Set Gazebo paths so it can find hospital models
    set_model_path = SetEnvironmentVariable(
        name="GAZEBO_MODEL_PATH",
        value=f"{models_path}:{fuel_path}:/opt/ros/humble/share/turtlebot3_gazebo/models"
    )

    # Launch Gazebo with hospital world
    gazebo = ExecuteProcess(
        cmd=["gazebo", "--verbose", world_path,
             "-s", "libgazebo_ros_init.so",
             "-s", "libgazebo_ros_factory.so"],
        output="screen"
    )

    # Spawn TurtleBot3 in the hospital
    spawn_turtlebot = TimerAction(
        period=8.0,
        actions=[
            ExecuteProcess(
                cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
                     "-entity", "waffle_pi",
                     "-file", "/opt/ros/humble/share/turtlebot3_gazebo/models/turtlebot3_waffle_pi/model.sdf",
                     "-x", "0.0", "-y", "0.0", "-z", "0.1"],
                output="screen"
            )
        ]
    )

    # YOLO detector
    yolo_node = TimerAction(
        period=12.0,
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

    return LaunchDescription([
        target_object, show_debug,
        set_model_path,
        gazebo, spawn_turtlebot, yolo_node
    ])
