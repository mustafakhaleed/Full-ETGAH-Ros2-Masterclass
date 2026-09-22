# turtlebot-controller-mostafa-eissa

A ROS 2 workspace with two nodes that control and monitor a TurtleBot using keyboard input:

- **`turtlebot_controller.py`** (Publisher) — reads keyboard input (`W`, `A`, `S`, `D`, `Q`) and publishes `Twist` movement commands to `/cmd_vel`.
- **`turtlebot_monitor.py`** (Subscriber) — subscribes to `/cmd_vel` and prints the linear/angular velocity being sent to the robot in real time.

---

## 1. Package Structure

```
turtlebot-controller-mostafa-eissa/
└── src/
    └── turtlebot_controller/
        ├── turtlebot_controller/
        │   ├── __init__.py
        │   ├── turtlebot_controller.py   # Publisher node
        │   └── turtlebot_monitor.py      # Subscriber node
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        ├── test/
        └── README.md
```

---

## 2. Requirements

- Ubuntu
- ROS 2 installed and sourced
- Python 3
- `colcon` build tool

---

## 3. Setup Instructions (Step by Step)

### Step 1 — Clone the repository
```bash
git clone https://github.com/mustafakhaleed/turtlebot-controller-mostafa-eissa.git
```
Downloads a copy of this repository (workspace) to your machine.

```bash
cd turtlebot-controller-mostafa-eissa
```
Moves you into the cloned workspace folder, which is the root of the ROS 2 workspace.

### Step 2 — Source your ROS 2 installation
```bash
source /opt/ros/<distro>/setup.bash
```
Loads the ROS 2 environment (commands like `ros2`, message types, etc.) into your terminal session. Replace `<distro>` with your ROS 2 distribution (e.g. `humble`, `foxy`).

### Step 3 — Build the workspace
```bash
colcon build
```
Compiles/prepares all ROS 2 packages inside `src/` (here, `turtlebot_controller`) and generates the `build/`, `install/`, and `log/` folders.

### Step 4 — Source the workspace
```bash
source install/setup.bash
```
Makes the packages you just built (and their nodes) available to run with `ros2 run`, in this terminal session.

> **Note:** Steps 2 and 4 must be repeated in every **new** terminal you open, since sourcing only applies to the current shell session.

---

## 4. Running the Nodes (ROS 2 Commands)

Open **two terminals**, and in each one source the workspace first (Step 2 and 4 above).

### Terminal 1 — Run the Publisher (Controller)
```bash
ros2 run turtlebot_controller cmd_vel_Pub_Handler
```
Runs the publisher node (`cmd_vel_Pub_Handler`), which prompts you for keyboard input and publishes `Twist` messages to `/cmd_vel`.

### Terminal 2 — Run the Subscriber (Monitor)
```bash
ros2 run turtlebot_controller cmd_vel_Sub_Handler
```
Runs the subscriber node (`cmd_vel_Sub_Handler`), which listens to `/cmd_vel` and prints the linear/angular velocity received.

### Useful ROS 2 inspection commands
```bash
ros2 node list
```
Lists all currently running ROS 2 nodes (should show `cmd_vel_Pub_Handler` and `cmd_vel_Sub_Handler`).

```bash
ros2 topic list
```
Lists all active topics (should include `/cmd_vel`).

```bash
ros2 topic echo /cmd_vel
```
Prints every message published on `/cmd_vel` directly from the command line, useful for testing without running the monitor node.

---

## 5. How to Test the Nodes

1. Run the **publisher** in Terminal 1 and the **subscriber** in Terminal 2 (see above).
2. In Terminal 1, type one of the following keys and press Enter:
   - `W` → move forward
   - `S` → move backward
   - `A` → turn/move left
   - `D` → turn/move right
   - `Q` → stop and exit
3. Watch Terminal 2 — it should print the `linear.x` and `angular.z` values matching what you typed, in real time.
4. Alternatively, instead of running the monitor node, you can run `ros2 topic echo /cmd_vel` in Terminal 2 to see the raw messages.

---

## 6. Expected Output

**Terminal 1 (Publisher):**
```
Enter (W/A/S/D) for Moving , or Q for Stopping W
Moving Forward
[INFO] [cmd_vel_Pub_Handler]: Publishing: linear=0.2, angular=0.0
```

**Terminal 2 (Subscriber):**
```
[INFO] [cmd_vel_Sub_Handler]: Received cmd_vel: linear=0.2, angular=0.0
```

When `Q` is entered, the publisher sends an empty `Twist` message (all zeros) to stop the robot, and the program exits.

---

 
## 7. Demo
 
https://github.com/mustafakhaleed/turtlebot-controller-mostafa-eissa/blob/main/src/turtlebot_controller/Demo_vid/Demo_Moving_Robot.mp4
 
Shows both terminals running side by side: keyboard commands entered in the publisher terminal, and the corresponding `linear`/`angular` values received live in the subscriber terminal.
 
---

## 8. Notes

- Both nodes use the `Twist` message type from `geometry_msgs`.
- Both nodes communicate over the same topic: `/cmd_vel`.
- The publisher sends commands; the subscriber only receives and logs them.
