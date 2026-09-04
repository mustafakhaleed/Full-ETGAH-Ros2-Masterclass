# task5-robot_description

A ROS 2 (Jazzy) package containing the complete URDF/Xacro description,
3D meshes, launch configurations, RViz display profile, and Gazebo Sim
integration for a custom differential-drive robot equipped with a 2D
LiDAR and an RGB camera.

---

## 1. Project Overview

This package (`my_robot_description`) defines a differential-drive
mobile robot — two driven wheels, a passive caster wheel, a 2D LiDAR,
and an RGB camera — modeled entirely in Xacro. It includes everything
needed to:

- Preview the robot's kinematic structure and TF tree in **RViz2**.
- Spawn and drive the robot in a full physics simulation in
  **Gazebo Sim**, bridged to ROS 2 topics via `ros_gz_bridge`.

---

## 2. Package Structure

```
my_robot_description/
├── config/
│   └── gz_bridge.yaml
├── launch/
│   ├── display.launch.py
│   └── gazebo.launch.py
├── meshes/
│   ├── Caster_Wheel.stl
│   ├── lidar.STL
│   └── zed.stl
├── rviz/
│   └── robot_view.rviz
├── screenshots/
│   ├── Camera_view.png
│   ├── Gz_Robot.png
│   ├── lidar_visualization.png
│   ├── Rviz_robot.png
│   └── tf_tree.png
├── tf_frames/
│   ├── frames_<timestamp>.gv
│   └── frames_<timestamp>.pdf
├── urdf/
│   ├── robot.urdf.xacro
│   └── robot.gazebo.xacro
├── CMakeLists.txt
├── package.xml
└── README.md
```

---

## 3. Prerequisites

```bash
sudo apt install ros-jazzy-xacro \
                  ros-jazzy-robot-state-publisher \
                  ros-jazzy-joint-state-publisher-gui \
                  ros-jazzy-rviz2 \
                  ros-jazzy-ros-gz-sim \
                  ros-jazzy-ros-gz-bridge \
                  ros-jazzy-teleop-twist-keyboard
```

---

## 4. Linux Commands Used

**Workspace setup & build**

```bash
# Navigate to workspace and clean prior build artifacts
cd ~/Downloads/ET_ASS6_ws
rm -rf build/ install/ log/

# Build package using symlink installation
colcon build --symlink-install --packages-select my_robot_description

# Source workspace environment
source install/setup.bash
```


## 5. ROS 2 Commands Used

**Source environment**

```bash
source /opt/ros/$ROS_DISTRO/setup.bash
source install/setup.bash
```

**Topic inspection & monitoring**

```bash
ros2 topic list
ros2 topic echo /cmd_vel
ros2 topic echo /joint_states
```

**Manual velocity command**

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}, angular: {z: 0.1}}"
```

---

## 6. How to Launch RViz

To visualize the URDF model, frames, and TF tree standalone in RViz:

```bash
ros2 launch my_robot_description display.launch.py
```

---

## 7. How to Launch Gazebo

To spawn the robot and load the Gazebo simulation environment:

```bash
ros2 launch my_robot_description gazebo.launch.py
```

---

## 8. Expected Topics

| Topic | Type | Description |
|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | Velocity commands controlling robot motion |
| `/odom` | `nav_msgs/msg/Odometry` | Raw odometry calculated by the differential drive system |
| `/joint_states` | `sensor_msgs/msg/JointState` | Active joint positions for wheels and caster assembly |
| `/tf` & `/tf_static` | `tf2_msgs/msg/TFMessage` | Dynamic and static coordinate transforms across all frames |
| `/scan` | `sensor_msgs/msg/LaserScan` | 2D LiDAR range scan measurement data |
| `/camera/image_raw` | `sensor_msgs/msg/Image` | Uncompressed RGB camera stream |
| `/camera/camera_info` | `sensor_msgs/msg/CameraInfo` | Camera intrinsic calibration properties |

---

## 9. How to Move the Robot

1. Launch the Gazebo simulation:

   ```bash
   ros2 launch my_robot_description gazebo.launch.py
   ```

2. In a new terminal, run the teleoperation node:

   ```bash
   ros2 run teleop_twist_keyboard teleop_twist_keyboard
   ```

3. Drive the robot using the keyboard:

   | Key | Action |
   |---|---|
   | `i` | Forward |
   | `,` | Backward |
   | `j` | Turn left |
   | `l` | Turn right |
   | `k` | Stop |

---

## 10. TF Tree Explanation

![TF Tree](screenshots/tf_tree.png)

The full TF tree graph (`.gv` + `.pdf`) is also exported in
`tf_frames/`, generated with:

```bash
ros2 run tf2_tools view_frames
```

The coordinate transforms form a continuous parent-child hierarchy:

- **`odom` → `base_footprint`** — dynamic transform published by
  Gazebo's DiffDrive plugin, tracking the robot's pose in the world.
- **`base_footprint` → `base_link`** — static transform placing
  `base_link` at its physical ground-clearance height.
- **`base_link` → `left_wheel` / `right_wheel`** — continuous joints
  driven by the differential-drive velocity controller.
- **`base_link` → `caster_swivel_link` → `caster_wheel`** — dynamic
  joint chain enabling free passive swivel and rolling motion.
- **`base_link` → `lidar_link`** — fixed transform specifying the
  sensor's offset on top of the chassis.
- **`base_link` → `camera_link` → `camera_optical_link`** — fixed
  transforms setting the optical-frame convention (Z forward, X right,
  Y down).

---

## 11. Screenshots

### Robot in RViz
![Robot in RViz](screenshots/Rviz_robot.png)

### TF Tree
![TF Tree](screenshots/tf_tree.png)

### Robot in Gazebo
![Robot in Gazebo](screenshots/Gz_Robot.png)

### LiDAR Visualization
![LiDAR Visualization](screenshots/lidar_visualization.png)

### Camera Visualization
![Camera Visualization](screenshots/Camera_view.png)