#define trigPin 13
#define echoPin 10
int min=500; //Initilize minimum value
int time=0;// timer Counter
// Setting up the input and output pins
void setup() {
  Serial.begin (9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  float duration, distance;
  digitalWrite(trigPin, LOW); 
  delayMicroseconds(2);
 
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distance = (duration / 2) * 0.0344;//Considering speed of sound= 340 m/s and waves travel twice so divided by 2
  
  if (distance <= 400 || distance >= 2){//Maximum and Minimum range of measurement by the sensor
      if(distance<min){ // Finds the minimum for a duration of 30 sec
      min=distance;
      Serial.print("Minimum = ");
      Serial.print(min);
      Serial.println("cm");
      delay(500);
      }
  }
 // Refreshes the time and minimum parameters
  delay(500);
  time=time+1;
  if(time==10){
    min=500;
    time=0;
  }
}
