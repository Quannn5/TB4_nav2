import time

import cv2
import rclpy
from cv_bridge import CvBridge, CvBridgeError
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
import torch
from ultralytics import YOLO


class YoloDetector(Node):
    def __init__(self):
        super().__init__('yolo_detector')
        self.declare_parameter(
            'image_topic', '/oakd/rgb/preview/image_raw'
        )
        self.declare_parameter(
            'detections_topic', '/yolo/detections/image'
        )
        self.declare_parameter('model', 'yolov8n.pt')
        self.declare_parameter('device', 'cpu')
        self.declare_parameter('confidence_threshold', 0.35)
        self.declare_parameter('inference_rate_hz', 2.0)
        self.declare_parameter('inference_threads', 2)
        self.declare_parameter('show_window', False)

        image_topic = self.get_parameter('image_topic').value
        detections_topic = self.get_parameter('detections_topic').value
        self.device = self.get_parameter('device').value
        inference_threads = self.get_parameter('inference_threads').value
        if inference_threads < 1:
            raise ValueError('inference_threads must be at least one.')
        torch.set_num_threads(inference_threads)
        self.model = YOLO(self.get_parameter('model').value)
        self.confidence_threshold = float(
            self.get_parameter('confidence_threshold').value
        )
        inference_rate = float(
            self.get_parameter('inference_rate_hz').value
        )
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError('confidence_threshold must be between 0 and 1.')
        if inference_rate <= 0.0:
            raise ValueError('inference_rate_hz must be greater than zero.')
        self.inference_period = 1.0 / inference_rate
        self.show_window = self.get_parameter('show_window').value
        self.window_name = 'TurtleBot 4 YOLO detections'
        self.window_ready = False
        self.last_inference = 0.0
        self.bridge = CvBridge()
        self.publisher = self.create_publisher(
            Image, detections_topic, qos_profile_sensor_data
        )
        self.subscription = self.create_subscription(
            Image,
            image_topic,
            self.image_callback,
            qos_profile_sensor_data,
        )
        self.get_logger().info(
            f'YOLO model ready; subscribing to {image_topic} and publishing '
            f'annotated images to {detections_topic}.'
        )

    def image_callback(self, message):
        now = time.monotonic()
        if now - self.last_inference < self.inference_period:
            return
        self.last_inference = now

        try:
            image = self.bridge.imgmsg_to_cv2(
                message, desired_encoding='bgr8'
            )
        except CvBridgeError as error:
            self.get_logger().error(f'Could not convert camera image: {error}')
            return

        result = self.model(
            image,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False,
        )[0]
        annotated = result.plot()
        output = self.bridge.cv2_to_imgmsg(annotated, encoding='bgr8')
        output.header = message.header
        self.publisher.publish(output)

        detections = []
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                confidence = float(box.conf[0].item())
                detections.append(
                    f'{result.names[class_id]} ({confidence:.2f})'
                )
        if detections:
            self.get_logger().info(
                'Detected: ' + ', '.join(detections)
            )
        else:
            self.get_logger().info('No objects detected in this frame.')

        if self.show_window:
            try:
                if not self.window_ready:
                    cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                    self.window_ready = True
                cv2.imshow(self.window_name, annotated)
                cv2.waitKey(1)
            except cv2.error as error:
                self.get_logger().warning(
                    'Could not display the YOLO detection window; keeping the '
                    f'node running without the GUI. ({error})'
                )
                self.show_window = False


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.show_window and node.window_ready:
            cv2.destroyWindow(node.window_name)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
