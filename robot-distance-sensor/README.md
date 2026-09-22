# robot-distance-sensor-Mostafa-Eissa

This project implements an Object-Oriented Python program to process distance sensor measurements (in meters) for a mobile robot and determine navigation actions based on configurable safety thresholds.

---

## 1. What does this program do?
The program evaluates real-time ultrasonic sensor distance readings (in meters) for a mobile robot. It validates the user inputs and distance values, then categorizes each distance into movement actions (`STOP`, `SLOW`, or `MOVE FAST`) to ensure the robot avoids collisions safely.

---

## 2. How does the Robot class work?
The `Robot` class encapsulates all necessary properties and behaviors of the system:
* **Attributes:** Stores the robot's metadata (`name` and `battery` percentage) along with dynamic distance thresholds (`stop_threshold` and `warning_threshold`).
* **Logic Execution:** Takes distance measurements and evaluates them against the instance's thresholds to generate actionable responses.

---

## 3. What does each method do?
* `__init__(self, name, battery, stop_threshold, warning_threshold)`: Constructor method that initializes the robot's attributes and safety distance boundaries upon instantiation.
* `Process_Distance_Sensor(self, distance)`: Accepts a list of distance values (in meters), handles invalid negative readings, and returns a list of tuples containing distance values alongside their corresponding actions (`STOP`, `SLOW`, `MOVE FAST`).

---

## 4. How do I run the code?
1. Clone or download this repository.
2. Open your terminal in the project directory.
3. Run the Python script:
   ```bash
   python3 robot.py
   ```
4. Enter your desired **STOP** threshold (e.g., `0.5`) and **WARNING** threshold (e.g., `1.0`) when prompted.

---

## 5. What did you learn from using AI?
* **Object-Oriented Design:** How to properly structure classes, pass initialization parameters, and maintain clean instance methods.
* **Defensive Coding & Validation:** Implementing structured input loops and exception checks to handle negative values and invalid user inputs seamlessly.
* **Code Optimization:** Refining variable naming and code readability to meet assignment guidelines without losing individual implementation style.