#include "fdd.h"

FDD::FDD() : drive_type(0), media_type(0) {}

void FDD::init( void ) {
  pinMode(FD_HEAD_LOAD, OUTPUT);  // Head Load     L=contact
  pinMode(FD_MOTOR,     OUTPUT);  // Motor         L=ON
  pinMode(FD_DIR,       OUTPUT);  // DIR           L=inside(trk+), H=outside (trk-)
  pinMode(FD_STEP,      OUTPUT);  // Step  negative pulse
  pinMode(FD_SIDE1,     OUTPUT);  // Side1 select  L=side0, H=side1
  pinMode(FD_READY,     INPUT_PULLUP);
  pinMode(FD_INDEX,     INPUT_PULLUP);   // Index    L=index
  pinMode(FD_TRK00,     INPUT_PULLUP);   // TRACK00  L=TRK00
  pinMode(FD_WP,        INPUT_PULLUP);

  digitalWrite(FD_DIR,        HIGH);  // - direction
  digitalWrite(FD_STEP,       HIGH);

  set_drive_type(0); // 2D

  motor(true);      // motor on
  head(true);       // head load on
  side(0);          // side 0
}

void FDD::set_drive_type(enum FDD::ENUM_DRV_MODE mode) {
  drive_type = mode;
}

inline enum FDD::ENUM_DRV_MODE FDD::get_drive_type(void) {
  return drive_type;
}

void FDD::set_media_type(enum ENUM_DRV_MODE mode) {
  media_type = mode;
}

inline enum FDD::ENUM_DRV_MODE FDD::get_media_type(void) {
  return media_type;
}

inline void FDD::step1(void) {
    digitalWrite(FD_STEP, LOW);
    delayMicroseconds(1);
    digitalWrite(FD_STEP, HIGH);
    delay(STEP_RATE);
}

void FDD::step(void) {
  int step_n = (drive_type == ENUM_DRV_MODE::mode_2dd && media_type == ENUM_MEDIA_TYPE::media_2d) ? 2 : 1;
  for (int i = 0; i < step_n; i++) {
    step1();
  }
}

void FDD::setStepDir(uint8_t dir) {
  digitalWrite(FD_DIR, dir);
}

inline uint8_t FDD::readIndex(void) {
  return digitalRead(FD_INDEX);
}

uint8_t FDD::readTRK00(void) {
  return digitalRead(FD_TRK00);
}

void FDD::stepIn(void) {   // Step towards inner track (trk#++)
  setStepDir(LOW);
  step();
}

void FDD::stepOut(void) {  // Step towards outer track (trk#--)
  setStepDir(HIGH);
  if(readTRK00()==HIGH) {
    step();
  }
}

void FDD::track00(void) {
  while (readTRK00() == HIGH) {
    stepOut();
  }
}

inline void FDD::waitIndex(void) {      // wait for the index hole detection
    int curr = HIGH;
    int prev = readIndex();
    while(true) {
      curr = readIndex();
      if(prev==HIGH && curr==LOW) break;   // detect falling edge
      prev = curr;
    }
}

void FDD::seek(int current, int target) {
  if (current == target) return;
  if (current < target) {
    for (int i = 0; i < target - current; i++) {
      stepIn();
    }
  } else {
    for (int i = 0; i < current - target; i++) {
      stepOut();
    }
  }
}

void FDD::side(int side) {
  switch (side) {
    case 0: digitalWrite(FD_SIDE1, HIGH); break;
    case 1: digitalWrite(FD_SIDE1, LOW ); break;
    default: break;
  }
}

void FDD::motor(bool onoff) {
  if (onoff) {
    digitalWrite(FD_MOTOR, LOW);    // Motor start
  } else {
    digitalWrite(FD_MOTOR, HIGH);   // Motor stop
  }
}

void FDD::head(bool onoff) {
  if (onoff) {
    digitalWrite(FD_HEAD_LOAD,  LOW);   // Head load on
  } else {
    digitalWrite(FD_HEAD_LOAD, HIGH);   // Head load off
  }
}

void FDD::detect_drive_type(void) {
  set_drive_type(ENUM_DRV_MODE::mode_2d);
  track00();
  seek(0,44);
  seek(43,0);
  Serial.print(F("**DRIVE_TYPE "));
  if(readTRK00()==LOW) {
    set_drive_type(ENUM_DRV_MODE::mode_2d);
    Serial.println(F("2D"));
  } else {
    set_drive_type(ENUM_DRV_MODE::mode_2dd);
    Serial.println(F("2DD"));
  }
}

// TCNT1 = 250KHz count
// INDEX pulse = 4.33ms negative pulse

float FDD::measure_rpm() {
#if defined(__AVR_ATmega328P__)
  noInterrupts();
  uint8_t TCCR1A_bkup = TCCR1A;
  TCCR1A = TCCR1A & 0xfc;   // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit

  long tcnt1_, tcnt1;
  waitIndex();
  tcnt1_ = TCNT1;
  waitIndex();
  tcnt1 = TCNT1;
  interrupts();
  tcnt1 = tcnt1 > tcnt1_ ? tcnt1 - tcnt1_ : tcnt1 - tcnt1_ + 65535;
  float spin = tcnt1 / 250e3;

  TCCR1A = TCCR1A_bkup;
#else
  float spin = 0.2f;      // Arduino boards other than 'Uno' use fixed spin value
#endif
  return spin;            // sec/spin  default=0.2sec/spin(=300rpm)
}
