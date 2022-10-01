#include "fdcaptureshield.h"

FDCaptureShield::FDCaptureShield() { }

void FDCaptureShield::init(void) {
  disconnect();
  digitalWrite(CAP_RST, LOW);
  pinMode(CAP_RST,      OUTPUT);
  pinMode(CAP_EN,       OUTPUT);
  pinMode(CAP_ACTIVE,   OUTPUT);
  delay(2);
  digitalWrite(CAP_RST, HIGH);
}

inline void FDCaptureShield::enable_sampling_clock(void) {
  digitalWrite(CAP_ACTIVE, HIGH);
}

inline void FDCaptureShield::disable_sampling_clock(void) {
  digitalWrite(CAP_ACTIVE, LOW);
}

inline void FDCaptureShield::connect(void) {
  digitalWrite(CAP_EN, LOW);
  enable_sampling_clock();
}

inline void FDCaptureShield::connect_and_standby(void) {
  digitalWrite(CAP_EN, LOW);
  disable_sampling_clock();
}

inline void FDCaptureShield::disconnect(void) {
  digitalWrite(CAP_EN, HIGH);
  disable_sampling_clock();
}
