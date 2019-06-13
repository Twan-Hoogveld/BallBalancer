int pwmPin   = 9;   // fan PWM -> connected to digital pin 9
int pwmVal   = 100;
int incoming_data = 0; //Default PWM speed.

void setup()
{
pinMode(pwmPin, OUTPUT);   // sets the pin as output
Serial.begin(9600);
}

// Main program
void loop()
{
    if(Serial.available() > 0){
        incoming_data = Serial.read();
  }
    analogWrite(pwmPin,incoming_data);
}