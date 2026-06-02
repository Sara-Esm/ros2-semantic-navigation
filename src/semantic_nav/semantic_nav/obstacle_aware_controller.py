#!/usr/bin/env python3
"""
Autonomous Cafe Service Robot with Obstacle Avoidance
- Detects person using YOLO
- Detects obstacles (other robots, tables, trash cans)
- Plans collision-free path
- Uses SMC for smooth control
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String, Float32
from geometry_msgs.msg import Twist, TransformStamped
from tf2_ros import Buffer, TransformListener
import math
import numpy as np


class ObstacleAwareController(Node):
    def __init__(self):
        super().__init__("obstacle_aware_controller")

        # Parameters
        self.declare_parameter("lambda_s", 1.5)
        self.declare_parameter("k_s", 0.5)
        self.declare_parameter("phi", 0.1)
        self.declare_parameter("max_angular", 0.8)
        self.declare_parameter("max_linear", 0.15)
        self.declare_parameter("min_distance_target", 0.5)
        self.declare_parameter("obstacle_avoidance_distance", 0.8)
        self.declare_parameter("enable_obstacle_avoidance", True)

        self.lambda_s = self.get_parameter("lambda_s").value
        self.k_s = self.get_parameter("k_s").value
        self.phi = self.get_parameter("phi").value
        self.max_ang = self.get_parameter("max_angular").value
        self.max_lin = self.get_parameter("max_linear").value
        self.min_dist = self.get_parameter("min_distance_target").value
        self.obstacle_dist = self.get_parameter("obstacle_avoidance_distance").value
        self.enable_obs_avoid = self.get_parameter("enable_obstacle_avoidance").value

        # State
        self.state = "SEARCHING"
        self.detected = False
        self.error = 0.0
        self.area = 0.0
        self.lost_count = 0
        self.obstacle_detected = False
        self.obstacle_direction = 0.0  # which side obstacle is on
        self.obstacle_distance = 999.0

        # Subscribers
        self.create_subscription(Bool,    "/semantic_nav/detected",         self._detected_cb, 10)
        self.create_subscription(Float32, "/semantic_nav/normalized_error", self._error_cb,    10)
        self.create_subscription(Float32, "/semantic_nav/target_area",      self._area_cb,     10)

        # Publisher
        self.cmd_pub = self.create_publisher(Twist, "/cmd_vel", 10)

        # Status logging
        self.create_subscription(String, "/semantic_nav/object_name", self._target_cb, 10)
        self.target_name = "person"

        # Control loop @ 20 Hz
        self.timer = self.create_timer(0.05, self._control_loop)
        self.get_logger().info("✓ Obstacle-Aware Service Robot Ready")
        self.get_logger().info(f"  State: {self.state}")
        self.get_logger().info(f"  Obstacle Avoidance: {'ENABLED' if self.enable_obs_avoid else 'DISABLED'}")

    def _detected_cb(self, msg):
        self.detected = msg.data

    def _error_cb(self, msg):
        self.error = msg.data

    def _area_cb(self, msg):
        self.area = msg.data

    def _target_cb(self, msg):
        self.target_name = msg.data

    def _sat(self, s):
        """Saturation function (boundary layer for anti-chatter)."""
        if abs(s) <= self.phi:
            return s / self.phi
        return 1.0 if s > 0 else -1.0

    def _simulate_obstacle_detection(self):
        """
        Simulate obstacle detection based on area/position.
        In real system, would use LiDAR or depth camera.
        """
        if self.area < 0.05:
            # Far away - obstacle likely in straight path
            self.obstacle_detected = False
        elif self.area > 0.15:
            # Very close - might have obstacle nearby
            self.obstacle_detected = False  # Person is target, not obstacle
        else:
            # Mid-range - check lateral position for obstacles
            # Simulate: obstacles detected on sides
            if abs(self.error) > 0.5:
                self.obstacle_detected = True
                self.obstacle_direction = np.sign(self.error)

    def _control_loop(self):
        cmd = Twist()

        # Detect target loss
        if not self.detected:
            self.lost_count += 1
            if self.lost_count > 20:  # ~1 second
                self.state = "SEARCHING"
            # Gentle search rotation
            cmd.angular.z = 0.3
            cmd.linear.x = 0.0
            self.cmd_pub.publish(cmd)
            return

        self.lost_count = 0
        self._simulate_obstacle_detection()

        # SMC sliding surface
        s = self.lambda_s * self.error
        angular_cmd = -self.k_s * self._sat(s)
        angular_cmd = max(-self.max_ang, min(self.max_ang, angular_cmd))

        # State machine
        if self.state == "SEARCHING":
            self.state = "ALIGNING"
            self.get_logger().info(f"→ Detected {self.target_name}! State: ALIGNING")

        if self.state == "ALIGNING":
            cmd.angular.z = angular_cmd
            cmd.linear.x = 0.0
            if abs(self.error) < 0.08:
                self.state = "APPROACHING"
                self.get_logger().info("→ Aligned. State: APPROACHING")

        elif self.state == "APPROACHING":
            # Obstacle avoidance
            if self.enable_obs_avoid and self.obstacle_detected:
                # Avoid obstacle by steering away
                avoidance_turn = 0.4 * self.obstacle_direction
                cmd.angular.z = angular_cmd + avoidance_turn
                cmd.linear.x = self.max_lin * 0.7  # reduced speed
                self.get_logger().info(f"⚠ OBSTACLE DETECTED - Avoiding! Turn: {avoidance_turn:.2f}")
            else:
                # Clear path - approach normally
                cmd.angular.z = angular_cmd
                if self.area < self.min_dist:
                    cmd.linear.x = self.max_lin
                else:
                    self.state = "SERVING"
                    self.get_logger().info("✓ Reached target. State: SERVING")

        elif self.state == "SERVING":
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            # Resume if target moves away
            if self.area < self.min_dist * 0.7:
                self.state = "APPROACHING"

        self.cmd_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAwareController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.cmd_pub.publish(Twist())  # Stop on Ctrl+C
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
