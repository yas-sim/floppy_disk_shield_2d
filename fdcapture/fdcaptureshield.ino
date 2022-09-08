#include "fdcaptureshield.h"

FDCaptureShield::FDCaptureShield() { }

void FDCaptureShield::init(void) {
  disable();
  digitalWrite(CAP_RST, LOW);
  pinMode(CAP_RST,      OUTPUT);
  pinMode(CAP_EN,       OUTPUT);
  pinMode(CAP_ACTIVE,   OUTPUT);
  delay(2);
  digitalWrite(CAP_RST, HIGH);
}

inline void FDCaptureShield::enable(void) {
  digitalWrite(CAP_EN,     LOW);
  digitalWrite(CAP_ACTIVE, HIGH);
}

inline void FDCaptureShield::disable(void) {
  digitalWrite(CAP_ACTIVE, LOW);
  digitalWrite(CAP_EN,     HIGH);
}
