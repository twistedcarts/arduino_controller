#include <Mouse.h>

bool active = false;

// using mpx as default selection
int recoil_Y = 6;
int recoil_X = 1;

void setup() {
    Serial.begin(9500);
    Mouse.begin();
}

void loop() {
    if (Serial.available() > 0) {
        char input = Serial.read();

        // mouse i/o detection
        if (input == '1') {
            active = true;
        } else if (input == '0') {
            active = false;

        // weapon recoil (modify these values by going into shooting range and tweaking with the values as the recoil pattern can change)
        // since arduino's can only recieve bytes (or single characters) you can either convert a string, or just use a single letter/number for different weapons. the letters/numbers must match up with what is being sent in the python script
        } else if (input == 'M') { // M4
            recoil_Y = 15;
            recoil_X = 2;
        } else if (input == 'X') { // MPX
            recoil_Y = 6; 
            recoil_X = 1;
        } else if (input == 'P') { // P90
            recoil_Y = 18; 
            recoil_X = 0;
        } else if (input == 'F') { // F2
            recoil_Y = 29; 
            recoil_X = 1;
        } else if (input == 'S') { // SMG-12
            recoil_Y = 13;
            recoil_X = 0;
        } 
    }

    if (active) {
        Mouse.move(-recoil_Y, recoil_Y, 0);
        delay(30);
    }
}
