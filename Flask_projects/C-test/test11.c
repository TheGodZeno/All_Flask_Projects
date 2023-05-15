#include <string.h>
#include <stdlib.h>

#define MAX_RX_COMMAND 11
#define ledPin1 2 // Pin number of the first LED
#define ledPin2 3 // Pin number of the second LED
#define ledPin3 4 // Pin number of the third LED
#define buttonPin1 8
#define buttonPin2 9
#define buttonPin3 10

bool ledState1 = false;
bool buttonState1 = false;
bool buttonPressed1 = false;
bool buttonReleased1 = false;

bool ledState2 = false;
bool buttonState2 = false;
bool buttonPressed2 = false;
bool buttonReleased2 = false;

bool ledState3 = false;
bool buttonState3 = false;
bool buttonPressed3 = false;
bool buttonReleased3 = false;

static unsigned long LED1_DELAY = 50, LED2_DELAY = 100, LED3_DELAY = 75;
char buff[MAX_RX_COMMAND];

void myComm() {
static int index = 0;
if (Serial.available() <= 0)
return; // No input is waiting in RX FIFO

char ch = Serial.read();

switch (ch) {
case '$':
    index = 0;
    break;
case '&':
        buff[index] = '\0';
        if (buff[0] == 'L') {
            int ledNumber = buff[1] - '0';
        if (ledNumber < 1 || ledNumber > 3) break;
        ledNumber++;
    switch (buff[2]) {
        case 'O':
            if (buff[3] == 'N') digitalWrite(ledNumber, HIGH);
            else if (buff[3] == 'F' && buff[4] == 'F') digitalWrite(ledNumber, LOW);
            break;
        default:
            if(isNumeric(buff + 2) == false){
                memset(buff, 0, sizeof(buff));
                index = 0;
                break;
            }
            int delayTime = atoi(buff + 2);
            if(delayTime < 50 || delayTime > 15000){
                memset(buff, 0, sizeof(buff));
                index = 0;
                break;
            }
            switch (ledNumber) {
                case ledPin1:
                    LED1_DELAY = delayTime;
                    break;
                case ledPin2:
                    LED2_DELAY = delayTime;
                    break;
                case ledPin3:
                    LED3_DELAY = delayTime;
                    break;
            }
            break;
    }
    }
    index = 0;
    memset(buff, 0, sizeof(buff));
    break;
default:
    buff[index] = ch;
    index++;
    if (index >= MAX_RX_COMMAND) index = 0;
    break;
}
}

bool isNumeric(const char* str) {
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] < '0' || str[i] > '9') {
            return false;
        }
    }
    return true;
}

// -------------------------------------------
void setup()
{
    Serial.begin(9600);
    pinMode(ledPin1, OUTPUT); // Set the first LED pin as output
    pinMode(ledPin2, OUTPUT); // Set the second LED pin as output
    pinMode(ledPin3, OUTPUT); // Set the third LED pin as output
    
    pinMode(buttonPin1, INPUT);
    pinMode(buttonPin2, INPUT);
    pinMode(buttonPin3, INPUT);
}
// -------------------------------------------


void loop() {
myComm();
readButton();
}


void readButton()
{
    buttonState1 = digitalRead(buttonPin1);
    buttonState2 = digitalRead(buttonPin2);
    buttonState3 = digitalRead(buttonPin3);

    if (buttonState1 == LOW && !buttonPressed1) {
        buttonPressed1 = true;
        buttonReleased1 = false;
    }

    if (buttonState2 == LOW && !buttonPressed2) {
        buttonPressed2 = true;
        buttonReleased2 = false;
    }

    if (buttonState3 == LOW && !buttonPressed3) {
        buttonPressed3 = true;
        buttonReleased3 = false;
    }


    if (buttonState1 == HIGH && !buttonReleased1) {
        buttonPressed1 = false;
        buttonReleased1 = true;
        ledState1 = !ledState1;
        digitalWrite(ledPin1, ledState1);
    }

    if (buttonState2 == HIGH && !buttonReleased2) {
        buttonPressed2 = false;
        buttonReleased2 = true;
        ledState2 = !ledState2;
        digitalWrite(ledPin2, ledState2);
    }

    if (buttonState3 == HIGH && !buttonReleased3) {
        buttonPressed3 = false;
        buttonReleased3 = true;
        ledState3 = !ledState3;
        digitalWrite(ledPin3, ledState3);
    }


    if (ledState1) blink_LED1();
    if (ledState2) blink_LED2();
    if (ledState3) blink_LED3();
}

void blink_LED1()
{
    static unsigned long previousMillis1 = 0;
    unsigned long currentMillis = millis(); // Get the current time
    if (currentMillis - previousMillis1 >= LED1_DELAY) { // Check if the interval has passed for the first LED
        previousMillis1 = currentMillis; // Update the previous time for the first LED
        digitalWrite(ledPin1, !digitalRead(ledPin1)); // Toggle the first LED
    }
}


// -------------------------------------------

void blink_LED2()
{
    static unsigned long previousMillis2 = 0;
    unsigned long currentMillis = millis(); // Get the current time
    if (currentMillis - previousMillis2 >= LED2_DELAY) { // Check if the interval has passed for the second LED
        previousMillis2 = currentMillis; // Update the previous time for the second LED
        digitalWrite(ledPin2, !digitalRead(ledPin2)); // Toggle the second LED
    }
}

// -------------------------------------------

void blink_LED3()
{
    static unsigned long previousMillis3 = 0;
    unsigned long currentMillis = millis(); // Get the current time
    if (currentMillis - previousMillis3 >= LED3_DELAY) { // Check if the interval has passed for the third LED
        previousMillis3 = currentMillis; // Update the previous time for the third LED
        digitalWrite(ledPin3, !digitalRead(ledPin3)); // Toggle the third LED
    }
}