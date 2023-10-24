#include <Servo.h>

Servo base_servo;
Servo shoulder_servo;
Servo elbow_servo;
Servo gripper_servo;

void setup() {
  Serial.begin(115200);
  base_servo.attach(9);
  shoulder_servo.attach(6);
  elbow_servo.attach(5);
  gripper_servo.attach(3);

  // Initialize servo positions
  base_servo.write(10);
  shoulder_servo.write(45);
  elbow_servo.write(0);
  gripper_servo.write(90);
}

void openGripper() {
  gripper_servo.write(90); // Open the gripper
}

void closeGripper() {
  gripper_servo.write(0); // Close the gripper
}

void moveShoulder(int angle) {
  shoulder_servo.write(angle); // Set the shoulder servo angle
}

void moveElbow(int angle) {
  elbow_servo.write(angle); // Set the elbow servo angle
}

void rotateBase(int angle) {
  base_servo.write(angle); // Set the base servo angle
}

void red() {
  closeGripper();
  delay(1000);
  base_servo.write(60); // Rotate base to 45 degrees
  delay(1000); // Delay after rotating the base
  moveShoulder(90);
  delay(1000); // Delay after moving the shoulder
  openGripper();
  delay(1000); // Delay after opening the gripper
  moveShoulder(45);
  delay(1500);
  base_servo.write(10);
  delay(1000);
  openGripper(); // Rotate base to 0 degrees
  delay(1000);
}

void green() {
  closeGripper();
  delay(1000);
  base_servo.write(120); // Rotate base to 120 degrees
  delay(2000); // Delay after rotating the base
  moveShoulder(90);
  delay(1000); // Delay after moving the shoulder
  openGripper();
  delay(1000); // Delay after opening the gripper
  moveShoulder(45);
  delay(1500);
  base_servo.write(10);
  delay(1000);
  openGripper(); // Rotate base to 0 degrees
  delay(1000);
}

  void yellow() {
    closeGripper();
    delay(1000);
    base_servo.write(180); // Rotate base to 180 degrees
    delay(3000); // Delay after rotating the base
    moveShoulder(90);
    delay(1000); // Delay after moving the shoulder
    openGripper();
    delay(1000); // Delay after opening the gripper
    moveShoulder(45);
    delay(1500);
    base_servo.write(10);
    delay(1000);
    openGripper(); // Rotate base to 0 degrees
    delay(1000);
  }

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read(); // Read the incoming command

    if (command == '1') { // Command for blue
      red();
    }
    else if (command == '2') { // Command for green
      green();
    }
    else if (command == '3') { // Command for yellow
      yellow();
    }
  }
}
