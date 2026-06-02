#!/usr/bin/env python3
"""
YOLO Object Detection Node for ROS 2
Subscribes to: /camera/image_raw
Publishes: /semantic_nav/detected (Bool)
          /semantic_nav/object_name (String)
          /semantic_nav/normalized_error (Float32) - lateral error [-1, 1]
          /semantic_nav/target_area (Float32) - normalized bbox area [0, 1]
          /semantic_nav/debug_image (Image)
"""
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Bool, String, Float32
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO


class YoloDetectorNode(Node):
    def __init__(self):
        super().__init__("yolo_detector_node")

        # Parameters
        self.declare_parameter("target_object", "person")
        self.declare_parameter("confidence_threshold", 0.4)
        self.declare_parameter("model_path", "yolov8n.pt")
        self.declare_parameter("show_debug_window", True)
        self.declare_parameter("image_topic", "/camera/image_raw")

        self.target_object   = self.get_parameter("target_object").value
        self.conf_thresh     = self.get_parameter("confidence_threshold").value
        self.model_path      = self.get_parameter("model_path").value
        self.show_debug      = self.get_parameter("show_debug_window").value
        image_topic          = self.get_parameter("image_topic").value

        # Load YOLO model
        self.get_logger().info(f"Loading YOLO model: {self.model_path}")
        self.model = YOLO(self.model_path)
        self.class_names = self.model.names
        self.get_logger().info(f"Model loaded. Tracking: {self.target_object}")

        self.bridge = CvBridge()

        # Subscribers
        self.image_sub = self.create_subscription(
            Image, image_topic, self._image_cb, 10
        )

        # Publishers
        self.detected_pub  = self.create_publisher(Bool,    "/semantic_nav/detected",         10)
        self.name_pub      = self.create_publisher(String,  "/semantic_nav/object_name",      10)
        self.error_pub     = self.create_publisher(Float32, "/semantic_nav/normalized_error", 10)
        self.area_pub      = self.create_publisher(Float32, "/semantic_nav/target_area",      10)
        self.debug_pub     = self.create_publisher(Image,   "/semantic_nav/debug_image",      10)

        self.frame_count = 0

    def _image_cb(self, msg: Image):
        # Convert ROS Image to OpenCV
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"CV bridge error: {e}")
            return

        h, w = frame.shape[:2]
        img_area = h * w

        # Run YOLO inference
        results = self.model(frame, conf=self.conf_thresh, verbose=False)[0]

        # Find target object detection
        target_found = False
        best_box = None
        best_conf = 0.0

        if results.boxes is not None:
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf   = float(box.conf[0])
                name   = self.class_names[cls_id]
                if name == self.target_object and conf > best_conf:
                    target_found = True
                    best_box = box
                    best_conf = conf

        # Compute normalized error and area
        if target_found and best_box is not None:
            x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            bbox_area = (x2 - x1) * (y2 - y1)

            normalized_error = (cx - w/2) / (w/2)
            normalized_area  = bbox_area / img_area

            # Draw on debug image
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)
            cv2.putText(frame, f"{self.target_object} {best_conf:.2f}",
                        (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            cv2.putText(frame, f"err={normalized_error:+.3f} area={normalized_area:.3f}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

            self.detected_pub.publish(Bool(data=True))
            self.name_pub.publish(String(data=self.target_object))
            self.error_pub.publish(Float32(data=float(normalized_error)))
            self.area_pub.publish(Float32(data=float(normalized_area)))

            if self.frame_count % 10 == 0:
                self.get_logger().info(
                    f"TARGET '{self.target_object}' | err={normalized_error:+.3f} "
                    f"area={normalized_area:.4f} conf={best_conf:.2f}"
                )
        else:
            # Draw other detections in red (not the target)
            if results.boxes is not None:
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    conf   = float(box.conf[0])
                    name   = self.class_names[cls_id]
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,0,255), 1)
                    cv2.putText(frame, f"{name} {conf:.2f}",
                                (int(x1), int(y1)-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
            cv2.putText(frame, f"Searching for: {self.target_object}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            self.detected_pub.publish(Bool(data=False))

        # Publish debug image
        try:
            debug_msg = self.bridge.cv2_to_imgmsg(frame, "bgr8")
            self.debug_pub.publish(debug_msg)
        except Exception:
            pass

        # Show debug window
        if self.show_debug:
            cv2.imshow("YOLO Semantic Detection", frame)
            cv2.waitKey(1)

        self.frame_count += 1


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            cv2.destroyAllWindows()
        except Exception:
            pass
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
