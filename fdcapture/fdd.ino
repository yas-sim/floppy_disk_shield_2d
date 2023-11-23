#include "fdd.h"

FDD::FDD() : drive_type(0), media_type(0), write_gate_safeguard(false) {}

void FDD::init( void ) {
  digitalWrite(FD_WG, HIGH);
  pinMode(FD_WG,        OUTPUT);  // Write gate
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
    uint8_t duration = 0;
    while(readIndex() != LOW) ;
    while(duration < 100) {   // wait for 100 consecutive 'high' period
      if(readIndex() == LOW) duration = 0; else duration++;
    }
    while(readIndex() == HIGH) ;
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

inline void FDD::disableWriteGate(void) {
  digitalWrite(FD_WG, HIGH);   // WG can be disabled unconditionally
}

inline void FDD::enableWriteGate(void) {
  if(write_gate_safeguard == true) {  // safeguard must be released before enabling WG
    digitalWrite(FD_WG, LOW);
  }
}

inline void FDD::releaseWriteGateSafeguard(void) {
  write_gate_safeguard = true;
}

inline void FDD::setWriteGateSafeguard(void) {
  write_gate_safeguard = false;
}

inline bool FDD::isWriteProtected(void) {
  head(true);
  motor(true);
  delay(500);
  uint8_t wp_sts = digitalRead(FD_WP);
  return (wp_sts == LOW) ? true : false;
}


// TCNT1 = 250KHz count
// 200ms = 50,000 counts, 65,535 counts = 262.14 ms
//
// INDEX pulse = 4.33ms negative pulse
uint16_t FDD::measure_rpm_tick(void) {
  uint16_t tcnt1;
  noInterrupts();
  uint8_t TCCR1A_bkup = TCCR1A;
  uint8_t TCCR1B_bkup = TCCR1B;
  TCCR1A = 0x00;                    // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit
  TCCR1B = 0x03;                    // Timer1, WGM13,WGM12 = 0,0 / CS12,CS11,CS10 = 0,1,1 = clkIO/64

  MACRO_WAIT_INDEX();
  TCNT1 = 0;
  MACRO_WAIT_INDEX();
  tcnt1 = TCNT1;

  TCCR1A = TCCR1A_bkup;
  TCCR1B = TCCR1B_bkup;
  interrupts();
  return tcnt1;                    // Spindle spin time in TCNT1 tick count (250KHz/tick)
}


// TCNT1 = 250KHz count
// INDEX pulse = 4.33ms negative pulse

float FDD::measure_rpm(void) {
  float spin = measure_rpm_tick() / 250e3;
  return spin;            // sec/spin  default=0.2sec/spin(=300rpm)
}
