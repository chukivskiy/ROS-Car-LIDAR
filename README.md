# Simple Teleop with LiDAR-based Collision Avoidance

A simple keyboard-based teleoperation controller for a differential drive robot with **built-in collision avoidance** using LiDAR data.

This controller was built on top of a basic teleop script (`simple_teleop.py`). It keeps all previous functionality while adding automatic checks: the robot stops moving forward if any obstacle is closer than **0.5 m** (based on `/scan` topic).

## Key Features
- Keyboard control: `w` / `x` / `a` / `d` / `s` / `q`
- **Automatic stop** when approaching obstacles closer than **0.5 m** ahead
- Backward movement (`x`) and in-place rotations (`a` / `d`) are **always allowed** — even with an obstacle directly in front
- Publishes commands to the standard ROS 2 control topic: `/diff_drive_controller/cmd_vel` (type: `geometry_msgs/msg/TwistStamped`)
- Continuously prints the current **minimum distance** to obstacles in the terminal

## Controls

| Key | Action                  | Blocked by obstacle?                  |
|-----|-------------------------|---------------------------------------|
| `w` | Forward (0.5 m/s)       | **Yes** (if min distance < 0.5 m ahead) |
| `x` | Backward (-0.5 m/s)     | No                                    |
| `a` | Turn left (1.0 rad/s)   | No                                    |
| `d` | Turn right (-1.0 rad/s) | No                                    |
| `s` | Stop                    | —                                     |
| `q` | Quit the program        | —                                     |

## How Collision Avoidance Works
- Subscribes to the `/scan` topic (`sensor_msgs/msg/LaserScan`)
- Calculates the **minimum valid range** across all laser beams
- If `min_distance ≤ 0.5 m` → forward linear velocity (`linear.x`) is forced to **0**
- Angular velocity (`angular.z`) and negative linear velocity (backward) remain fully functional

## Demo

![2026-03-0122-22-17-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/cb3ff590-4941-4e29-b4b1-22d925ee5aa0)


## How to Run
Make sure you are in a ROS 2 environment (or the provided Docker container) with access to `/scan` and the controller.

```bash
# Run directly (Python 3)
python3 src/my_diff_robot/scripts/simple_teleop.py

