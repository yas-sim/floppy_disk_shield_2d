void print8BIN(byte dt) {
  for (int i = 7; i >= 0; i--) {
    Serial.print((dt >> i) & 1, DEC);
  }
}


void printHex(byte dt) {
  if (dt < 0x10) {
    Serial.print(F("0"));
  }
  Serial.print(dt, HEX);
}
