#include <Mouse.h>

bool is_active = false;
int recoil_y = 6;
int recoil_x = 1;
String weapon_name = "MPX";

void setup() {
    Serial.begin(9500);
    Mouse.begin();
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');

        if (input == "1") {
            is_active = true;
        } else if (input == "0") {
            is_active = false;
        } else if (input.startsWith("CFG:")) {
            parse_weapon_config(input.substring(4));
        }
    }

    if (is_active) {
        smooth_move(recoil_x, recoil_y);
    }
}

void smooth_move(int x, int y) {
    const int steps = 3;
    const int step_delay = 20 / steps;

    static int step_index = 0;
    static unsigned long last_step_time = 0;

    if (millis() - last_step_time >= step_delay) {
        if (step_index < steps) {
            Mouse.move(x / steps, y / steps, 0);
            step_index++;
        } else {
            step_index = 0;
        }
        last_step_time = millis();
    }
}

void parse_weapon_config(String cfg) {
    int first_comma = cfg.indexOf(',');
    int second_comma = cfg.indexOf(',', first_comma + 1);

    if (first_comma > 0 && second_comma > first_comma) {
        weapon_name = cfg.substring(0, first_comma);
        recoil_y = cfg.substring(first_comma + 1, second_comma).toInt();
        recoil_x = cfg.substring(second_comma + 1).toInt();
    }
}
