

long debounceDelay = 20;

class Button
{
  public:
    Button(int pin, char aup, char adown)
    :buttonPin(pin), up(aup), down(adown)
    {
     prevState = -1;
     lastDebounceTime = 0;
    }  

  char up, down;
  const int buttonPin;
  int prevState;
  long lastDebounceTime;

  void InitPin()
  {
    pinMode(buttonPin, INPUT);   // digital sensor is on digital pin 2
    digitalWrite(buttonPin, HIGH);
  }

  void DoButtonStuff()
  {  
    int buttonState = digitalRead(buttonPin);
  
    if (buttonState != prevState) 
    {
      if ((millis()-lastDebounceTime) > debounceDelay)
      {
        if (buttonState == HIGH) 
        {
         Serial.write(up);
        }
        else {
         Serial.write(down);
        }
      }
      else {
        Serial.write("9"); // to let you know when a bounce would have occurred
      }
      lastDebounceTime = millis();
      prevState = buttonState;
    }
  }
};

Button Buttons[4] = { 
  Button(2, 'A', 'a'), 
  Button(4, 'B', 'b'), 
  Button(7, 'C', 'c'), 
  Button(8, 'D', 'd')
};

void setup()
{
  // start serial port at 9600 bps:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
  
  for (int i =0; i< sizeof(Buttons)/sizeof(Button); ++i)
  {
    Buttons[i].InitPin();  
  }
  
}


void loop()
{

  for (int i =0; i< sizeof(Buttons)/sizeof(Button); ++i)
  {
    Buttons[i].DoButtonStuff();  
  }
  
}

void establishContact() {
  while (Serial.available() <= 0) {
    // Serial.print('A');   // send a capital A
    delay(300);
  }
}
