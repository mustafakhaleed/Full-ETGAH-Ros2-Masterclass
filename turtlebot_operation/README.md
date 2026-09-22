# TurtleBot Operation — Obstacle Avoidance with Manual Override

ROS 2 project that makes a TurtleBot3 (Waffle) autonomously avoid obstacles using LiDAR data, while allowing an operator to manually override its movement at any time through a custom service.

## Package Structure

```
turtlebot_operation_[YOUR-NAME]/
├── obstacle_direction_controller/
│   ├── obstacle_direction_controller/
│   │   ├── __init__.py
│   │   └── direction_autopilot_node.py
│   ├── DemoVid/
│   │   └── DemoVideo.mp4
│   ├── package.xml
│   ├── setup.py
│   ├── setup.cfg
│   ├── resource/
│   └── test/
├── set_dir/
│   ├── srv/
│   │   └── SetDirection.srv
│   ├── CMakeLists.txt
│   └── package.xml
└── README.md
```

## What It Does

- **`set_dir`** — defines the `SetDirection.srv` service used to manually override the robot's movement:
  ```
  string direction
  ---
  bool success
  string message
  ```

- **`obstacle_direction_controller`** — the `direction_autopilot_node`:
  - Subscribes to `/scan` and reads LiDAR distances in the front, left, and right directions
  - Runs a state machine (`forward → left/right → reverse`) to pick the safest movement direction
  - Publishes velocity commands to `/cmd_vel`
  - Exposes the `/set_direction` service — any external call temporarily overrides the autopilot for 3 seconds, then control returns to the autopilot automatically
  - Logs every state change and override action to the ROS 2 console

## 1. Setup Instructions

### Prerequisites
- ROS 2 (tested on Humble)
- TurtleBot3 packages (`turtlebot3`, `turtlebot3_simulations`) installed and `TURTLEBOT3_MODEL=waffle` exported
- Gazebo installed and working with TurtleBot3

### Clone and Build
```bash
# Clone the repo into your workspace's src folder
cd ~/ros2_ws/src
git clone https://github.com/mustafakhaleed/turtlebot_operation_mostafa-eissa.git

# Go back to the workspace root and build only these packages
cd ~/ros2_ws
colcon build --packages-select set_dir obstacle_direction_controller

# Source the workspace (do this in every new terminal you use)
source install/setup.bash
```

## 2. ROS 2 Commands Used and What They Do

| Command | What it does |
|---|---|
| `colcon build --packages-select <pkg>` | Builds only the specified packages instead of the whole workspace, saving time |
| `source install/setup.bash` | Loads the newly built packages into the current terminal's ROS 2 environment |
| `ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py` | Starts the Gazebo simulation with a TurtleBot3 in a world with obstacles |
| `ros2 run obstacle_direction_controller direction_autopilot_node` | Runs the obstacle-avoidance node |
| `ros2 topic list` | Lists all active topics, used to confirm `/scan` and `/cmd_vel` exist |
| `ros2 topic echo /cmd_vel` | Prints the velocity commands being published live, to confirm the node is actually sending movement commands |
| `ros2 topic echo /scan --once` | Prints a single LiDAR scan message, used to check `angle_min`, `angle_max`, and `angle_increment` |
| `ros2 service list` | Lists all active services, used to confirm `/set_direction` is exposed |
| `ros2 service type /set_direction` | Shows the service's message type |
| `ros2 interface show set_dir/srv/SetDirection` | Shows the request/response fields of the custom service |
| `ros2 service call /set_direction set_dir/srv/SetDirection "{direction: 'left'}"` | Manually calls the service to override the robot's direction for 3 seconds |
| `ros2 node list` | Lists all running nodes, used to confirm the controller node and simulation nodes are alive |

## 3. How to Test the Nodes

**Terminal 1 — start the simulation:**
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
```

**Terminal 2 — run the controller node:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 run obstacle_direction_controller direction_autopilot_node
```

**Terminal 3 — watch the robot's velocity commands:**
```bash
source ~/ros2_ws/install/setup.bash
ros2 topic echo /cmd_vel
```

**Terminal 4 — test the manual override service:**
```bash
source ~/ros2_ws/install/setup.bash

# Valid directions
ros2 service call /set_direction set_dir/srv/SetDirection "{direction: 'left'}"
ros2 service call /set_direction set_dir/srv/SetDirection "{direction: 'right'}"
ros2 service call /set_direction set_dir/srv/SetDirection "{direction: 'reverse'}"
ros2 service call /set_direction set_dir/srv/SetDirection "{direction: 'forward'}"

# Invalid direction (should fail gracefully)
ros2 service call /set_direction set_dir/srv/SetDirection "{direction: 'xyz'}"
```

## 4. Expected Output

**Node startup:**
```
[INFO] [direction_auto]: Direction Auto Node initialized.
```

**Autonomous obstacle avoidance (no override active):**
```
[INFO] [direction_auto]: [AUTOPILOT] State: forward -> right (Front: 0.99m, L: 1.03m, R: 3.50m)
```

**Manual override call:**
```
requester: making request: set_dir.srv.SetDirection_Request(direction='left')
response:
set_dir.srv.SetDirection_Response(success=True, message="Movement set to 'left' for 3 seconds.")
```
Followed in the node's terminal by:
```
[INFO] [direction_auto]: [OVERRIDE] Executing manual command: left
[INFO] [direction_auto]: [AUTOPILOT] Resuming autonomous obstacle avoidance.
[INFO] [direction_auto]: [AUTOPILOT] State: left -> forward (Front: 3.50m, L: 1.15m, R: 3.50m)
```

**Invalid direction call:**
```
response:
set_dir.srv.SetDirection_Response(success=False, message="Invalid direction 'xyz'")
```

## 5. Demo

A demo video showing the robot moving autonomously in Gazebo, avoiding an obstacle, and responding to a manual `/set_direction` service call (with terminal logs visible) is included in the repo:

📹 [`obstacle_direction_controller/DemoVid/DemoVideo.mp4`](./obstacle_direction_controller/DemoVid/DemoVideo.mp4)
