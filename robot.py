class Robot:
    def __init__(self, stop_threshold, warning_threshold):
        """
        Initializes the Robot with stop and warning distance thresholds.
        """
        self.stop_threshold = stop_threshold
        self.warning_threshold = warning_threshold    

    def Process_Distance_Sensor(self, distance):
        """
        Processes a list of distance measurements (in centimeters)
        and decides the robot's action for each measurement.
        """
        Actions = []
        for dist in distance:
            if dist <= self.stop_threshold:
                Stop_Action = "I Have to Stop Immediatly !"
                Actions.append((dist, Stop_Action))

            elif self.stop_threshold < dist <= self.warning_threshold:
                Warning_Action = "Take care I'm in Warning Area Now"
                Actions.append((dist, Warning_Action))

            else:
                Keep_Going_Action = "I'm Running , No obstacles Upcoming"
                Actions.append((dist, Keep_Going_Action))

        return Actions


if __name__ == "__main__":

    #STOP_THRESHOLD = 10  # in cm
    #WARNING_THRESHOLD = 20  # in cm
    
    # --- 1. Get thresholds from user ---
    while True:
        try:
            STOP_THRESHOLD = float(input("Enter the STOP threshold distance (in cm): "))

            if STOP_THRESHOLD < 0:
                print(" Error: Thresholds must be non-negative. Try again!\n")
                continue
            break

        except ValueError:
            print(" Error: Invalid input. Please enter valid numeric values.\n")

    # I 've seperated the two while loops because if the user enters a negative value for the STOP_THRESHOLD, it will not affect the WARNING_THRESHOLD input. This way, the user can correct their input for each threshold independently.
    
    while True:
        try:
            WARNING_THRESHOLD = float(input("Enter the WARNING threshold distance (in cm): "))
            
            if WARNING_THRESHOLD < 0:
                print(" Error: Thresholds must be non-negative. Try again!\n")
                continue
            
            if STOP_THRESHOLD >= WARNING_THRESHOLD:
                print(" Error: WARNING threshold must be More than STOP threshold. Try again!\n")
                continue  
            break 

        except ValueError:
            print(" Error: Invalid input. Please enter valid numeric values.\n")

    # --- 2. Process distance measurements --- Test cases 
    distance_measurements = [5, 10, 15, 30, 50] 

    robot = Robot(STOP_THRESHOLD, WARNING_THRESHOLD)
    actions = robot.Process_Distance_Sensor(distance_measurements)

    # --- 3. Print Results ---
    print("\n--- Robot Distance Sensor Log ---")
    for dist, action in actions:
        print(f"Distance: {dist:2d} cm - Action: {action}")