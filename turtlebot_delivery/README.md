# Turtlebot Delivery — Mostafa Eissa

ROS 2 workspace with two packages implementing an autonomous package
delivery mission using ROS 2 Actions on a TurtleBot3 in Gazebo.

## Packages

- **delivery_mission_interfaces** — defines the custom `DeliveryMission.action`
  (Goal: speed, pickup_duration, delivery_duration, timeout /
   Result: success, message /
   Feedback: current_phase, phase_progress, elapsed_time, remaining_time)
- **delivery_mission_controller** — the action server node
  (`delivery_mission_node.py`) that drives the robot through 3 phases:
  driving to pickup → simulated pickup pause → driving to delivery.

## 1. Step-by-step setup instructions

1. Clone this repo into your ROS 2 workspace `src/` folder:
```bash
   cd ~/delivery_mission_ws/src
   git clone https://github.com/mustafakhaleed/turtlebot_delivery_mostafa-eissa.git .
```
2. Install TurtleBot3 simulation packages:
```bash
   sudo apt install ros-<distro>-turtlebot3* ros-<distro>-turtlebot3-simulations
   export TURTLEBOT3_MODEL=burger
```
3. Build the workspace:
```bash
   cd ~/delivery_mission_ws
   colcon build --symlink-install
   source install/setup.bash
```

## 2. Every ROS 2 command used (and what it does)

| Command | What it does |
|---|---|
| `ros2 pkg create` | scaffolds a new ROS 2 package |
| `colcon build --symlink-install` | builds all packages in the workspace |
| `ros2 launch turtlebot3_gazebo empty_world.launch.py` | starts Gazebo with the TurtleBot3 in an empty world |
| `ros2 run delivery_mission_controller delivery_mission_node` | starts the action server |
| `ros2 action send_goal ... --feedback` | sends a goal to the action server and streams feedback/result |
| `ros2 topic echo /cmd_vel` | inspects the velocity commands being published |
| `ros2 action list` / `ros2 action info` | lists / inspects available actions |

## 3. How to test your nodes

Open 3 terminals (run `source install/setup.bash` in each first).

**Terminal 1 — Gazebo:**
```bash
export TURTLEBOT3_MODEL=burger
ros2 launch turtlebot3_gazebo empty_world.launch.py
```

**Terminal 2 — action server:**
```bash
ros2 run delivery_mission_controller delivery_mission_node
```

**Terminal 3 — send a goal:**
```bash
ros2 action send_goal /delivery_mission delivery_mission_interfaces/action/DeliveryMission \
"{speed: 0.15, pickup_duration: 5.0, delivery_duration: 5.0, timeout: 20.0}" --feedback
```

**Test cancel:** send a longer goal, then press `Ctrl+C` mid-execution —
the robot stops immediately and the result reports `success: false`.

**Test timeout:** send a goal where `timeout` is shorter than the total
mission length (e.g. `pickup_duration: 10.0, delivery_duration: 10.0, timeout: 5.0`) —
the mission aborts and reports `success: false`.

## 4. Expected output
phase started: DRIVING_TO_PICKUP
phase finished: DRIVING_TO_PICKUP
phase started: PICKING_UP
phase finished: PICKING_UP
phase started: DRIVING_TO_DELIVERY
phase finished: DRIVING_TO_DELIVERY
mission completed successfully



The robot drives forward in Gazebo, stops for the pickup pause, then
drives forward again for the delivery phase, matching the feedback
streamed to the terminal.

## 5. Demo

Video showing the robot moving in Gazebo alongside the terminal output:

`demo/Delivey_Demo_Vid.mp4`

(Click the file in
the repo, then use the "Download" or "View raw" button to play Video.)
