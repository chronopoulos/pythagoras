

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
         Serial.print('K');
         Serial.println(up);
        }
        else {
         Serial.print('K');
         Serial.println(down);
        }
      }
      else {
         Serial.print('K');
         Serial.println('9');
      }
      lastDebounceTime = millis();
      prevState = buttonState;
    }
  }
};

Button Buttons[24] = { 
  Button(26, 'A', 'a'), 
  Button(27, 'B', 'b'), 
  Button(2, 'C', 'c'), 
  Button(3, 'D', 'd'),
  Button(4, 'E', 'e'),
  Button(5, 'F', 'f'),
  Button(6, 'G', 'g'),
  Button(7, 'H', 'h'),
  Button(8, 'I', 'i'),
  Button(9, 'J', 'j'),
  Button(10, 'K', 'k'),
  Button(11, 'L', 'l'), 
  Button(12, 'M', 'm'), 
  Button(13, 'N', 'n'), 
  Button(14, 'O', 'o'),
  Button(15, 'P', 'p'),
  Button(16, 'Q', 'q'),
  Button(17, 'R', 'r'),
  Button(18, 'S', 's'),
  Button(19, 'T', 't'),
  Button(20, 'U', 'u'),
  Button(21, 'V', 'v'),
  Button(22, 'W', 'w'),
  Button(24, 'X', 'x')
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
