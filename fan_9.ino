
int pwmPin   = 9;   // fan PWM -> connected to digital pin 9
int pwmVal   = 255;
int DEBUG    = 1; // DEBUG counter; if set to 1, will write values back via serial

void setup()
{
 pinMode(pwmPin, OUTPUT);   // sets the pin as output
 if (DEBUG) {
   Serial.begin(9600);
 }
}

// Main program
void loop()
{
     analogWrite(pwmPin, pwmVal);

     delay(2000);
    
     if (DEBUG) { // If we want to read the output
      if (pwmVal < 245) {
         pwmVal += 2;
         Serial.print("pwnVAL : ");
         Serial.print( pwmVal);
         Serial.print ("\n");
        
      } else {
         Serial.print('at max high');  // Print red value
         Serial.print("\t");    // Print a tab
         pwmVal = 230;
      }
    }
    
    delay(2000); // Pause for 'wait' milliseconds before resuming the loop
}
