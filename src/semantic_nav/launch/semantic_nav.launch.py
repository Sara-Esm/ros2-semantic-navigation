from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


PERSON_SDF = """<?xml version="1.0"?>
<sdf version="1.6">
  <model name="standing_person">
    <static>true</static>
    <include>
      <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Standing person</uri>
    </include>
  </model>
</sdf>"""

CHAIR_SDF = """<?xml version="1.0"?>
<sdf version="1.6">
  <model name="real_office_chair">
    <static>true</static>
    <include>
      <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/OfficeChairBlack</uri>
    </include>
  </model>
</sdf>"""

with open('/tmp/person.sdf', 'w') as f: f.write(PERSON_SDF)
with open('/tmp/chair.sdf', 'w') as f: f.write(CHAIR_SDF)


def generate_launch_description():

    target_object = DeclareLaunchArgument("target_object", default_value="person",
        description="YOLO target: person | chair | bottle | etc")
    show_debug = DeclareLaunchArgument("show_debug", default_value="true")

    spawn_person = TimerAction(period=8.0, actions=[
        ExecuteProcess(cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
            "-entity", "standing_person", "-file", "/tmp/person.sdf",
            "-x", "-4.5", "-y", "5.0", "-z", "0.0"], output="screen")
    ])

    spawn_chair = TimerAction(period=12.0, actions=[
        ExecuteProcess(cmd=["ros2", "run", "gazebo_ros", "spawn_entity.py",
            "-entity", "real_office_chair", "-file", "/tmp/chair.sdf",
            "-x", "2.0", "-y", "-0.5", "-z", "0.0"], output="screen")
    ])

    yolo_node = Node(
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

    return LaunchDescription([target_object, show_debug, spawn_person, spawn_chair, yolo_node])
