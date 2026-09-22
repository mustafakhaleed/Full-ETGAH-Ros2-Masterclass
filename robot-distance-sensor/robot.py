"""
Program: Robot Distance Sensor Processor
Description: Reads a list of distance sensor measurements (in meters) for a robot,
             validates user thresholds, and processes movement actions.
"""

class Robot:
    def __init__(self, name, battery, stop_threshold, warning_threshold):
        """
        Initializes the Robot with name, battery level, and distance thresholds (in meters).
        """
        self.name = name
        self.battery = battery
        self.stop_threshold = stop_threshold
        self.warning_threshold = warning_threshold    

    def Process_Distance_Sensor(self, distance):
        """
        Processes a list of distance measurements (in meters)
        and decides the robot's action for each measurement.
        """
        Actions = []
        for dist in distance:
            # Handling negative distance values (Bad readings)
            if dist < 0:
                Actions.append((dist, "INVALID: Negative distance reading!"))

            elif dist < self.stop_threshold:
                Stop_Action = "STOP: I Have to Stop Immediatly ! (Obstacle too close)"
                Actions.append((dist, Stop_Action))

            elif self.stop_threshold <= dist <= self.warning_threshold:
                Warning_Action = "SLOW: Take care I'm in Warning Area Now (Obstacle nearby)"
                Actions.append((dist, Warning_Action))

            else:
                Keep_Going_Action = "MOVE FAST: I'm Running , No obstacles Upcoming (Path clear)"
                Actions.append((dist, Keep_Going_Action))

        return Actions


if __name__ == "__main__":

    # --- 1. Get thresholds from user ---
    print("=== Welcome to Robot Control System ===")
    
    while True:
        try:
            STOP_THRESHOLD = float(input("Enter the STOP threshold distance (in meters, e.g., 0.5): "))

            if STOP_THRESHOLD < 0:
                print(" Error: Thresholds must be non-negative. Try again!\n")
                continue
            break

        except ValueError:
            print(" Error: Invalid input. Please enter valid numeric values.\n")

    # I've separated the two while loops so entering an invalid WARNING threshold won't reset the STOP threshold.
    while True:
        try:
            WARNING_THRESHOLD = float(input("Enter the WARNING threshold distance (in meters, e.g., 1.0): "))
            
            if WARNING_THRESHOLD < 0:
                print(" Error: Thresholds must be non-negative. Try again!\n")
                continue
            
            if STOP_THRESHOLD >= WARNING_THRESHOLD:
                print(" Error: WARNING threshold must be More than STOP threshold. Try again!\n")
                continue  
            break 

        except ValueError:
            print(" Error: Invalid input. Please enter valid numeric values.\n")

    # --- 2. Initialize Robot Object ---
    robot = Robot(
        name="Rover-01", 
        battery=85, 
        stop_threshold=STOP_THRESHOLD, 
        warning_threshold=WARNING_THRESHOLD
    )

    print(f"\n--- Robot Configured: {robot.name} | Battery: {robot.battery}% ---")

    # --- 3. Test Cases  ---
    test_cases = [
        [0.3, 1.5, 0.8, 2.0, 0.4],  # Test 1: Mixed inputs (Ass. Ex)
        [0.1, 0.2, 0.4],            # Test 2: All Stop zone
        [0.5, 0.7, 1.0],            # Test 3: All Slow zone
        [1.2, 2.5, 5.0],            # Test 4: All Move Fast zone
        [-1.0, 0.3, 0.8, 1.5]       # Test 5: Error Handling (Negative distance)
    ]

    print("\n--- Running Sensor Test Cases ---")
    for i, test in enumerate(test_cases, 1):
        print(f"\n>> Test Case {i}: Inputs = {test}")
        actions = robot.Process_Distance_Sensor(test)
        for dist, action in actions:
            print(f"   Distance: {dist:4.2f} m -> Action: {action}")