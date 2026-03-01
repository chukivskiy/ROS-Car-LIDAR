#!/usr/bin/env python3
import sys
import tty
import termios
import select
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan


class SimpleTeleop(Node):
    def __init__(self):
        super().__init__('simple_teleop')

        self.pub = self.create_publisher(
            TwistStamped,
            '/diff_drive_controller/cmd_vel',
            10
        )

        self.sub_scan = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        self.min_distance = 10.0
        self.SAFETY_THRESHOLD = 0.50
        self.last_print_time = self.get_clock().now()

        self.desired_linear = 0.0
        self.desired_angular = 0.0

        self.get_logger().info("w = fwd   x = back   a = left   d = right   s = stop   q = quit")
        self.get_logger().info("Safety stop: ≤ 0.5 m")

    def scan_callback(self, msg: LaserScan):
        valid_ranges = [
            r for r in msg.ranges
            if not math.isnan(r)
            and r != 0.0
            and r > 0.01
            and r < 30.0
        ]

        if valid_ranges:
            self.min_distance = min(valid_ranges)
        else:
            self.min_distance = 10.0

        now = self.get_clock().now()
        if (now - self.last_print_time).nanoseconds / 1e9 > 0.6:
            print(f"\rDistance: {self.min_distance: .3f} м ", end="", flush=True)
            self.last_print_time = now

    def get_safe_velocity(self, des_lin, des_ang):
        if des_lin <= 0:
            # Back/stop — no limits
            return des_lin, des_ang

        if self.min_distance <= self.SAFETY_THRESHOLD:
            return 0.0, des_ang   # rotation allowed

        return des_lin, des_ang

    def run(self):
        msg = TwistStamped()
        msg.header.frame_id = 'base_link'

        print("Press keys (w/x/a/d/s/q)")

        while rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.040)

            # ────────────────────────────────
            # Keyboard processing
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            key = None

            try:
                tty.setraw(fd, termios.TCSANOW)
                ready, _, _ = select.select([sys.stdin], [], [], 0.0)

                if ready:
                    key = sys.stdin.read(1)
                    if key == '\x1b':
                        select.select([sys.stdin], [], [], 0.02)
                        sys.stdin.read(10)  # skip rest of escape sequence
                        continue

            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            # ────────────────────────────────
            if key is not None:
                if key.lower() == 'w':
                    self.desired_linear = 0.5
                    self.desired_angular = 0.0
                elif key.lower() == 'x':
                    self.desired_linear = -0.5
                    self.desired_angular = 0.0
                elif key.lower() == 'a':
                    self.desired_linear = 0.0
                    self.desired_angular = 1.0
                elif key.lower() == 'd':
                    self.desired_linear = 0.0
                    self.desired_angular = -1.0
                elif key.lower() == 's':
                    self.desired_linear = 0.0
                    self.desired_angular = 0.0
                elif key in ['q', '\x03']:
                    print("\nВихід.")
                    break

            # ────────────────────────────────
            safe_lin, safe_ang = self.get_safe_velocity(
                self.desired_linear,
                self.desired_angular
            )

            msg.twist.linear.x = safe_lin
            msg.twist.angular.z = safe_ang
            msg.header.stamp = self.get_clock().now().to_msg()
            self.pub.publish(msg)

        print("\nNode interruption...")


def main():
    rclpy.init()
    node = SimpleTeleop()

    try:
        node.run()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
