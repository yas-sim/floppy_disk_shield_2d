#include "spi_sram.h"

SPISRAM::SPISRAM() {}

void SPISRAM::init(void) {
  SPI.begin();
  digitalWrite(SPISRAM_HOLD, HIGH);
  pinMode(SPISRAM_HOLD, OUTPUT);
  //reset();
  setMode();
  setDefaultValue(0xff);
  curr_bit_ptn = 0x80;
  curr_byte = default_val;
  write_count = 0;
}

void SPISRAM::setDefaultValue( uint8_t val ) {
  default_val = val;
}

inline uint8_t SPISRAM::transfer(uint8_t dt) {
  return SPI.transfer(dt);
}

inline void SPISRAM::hold(uint8_t state) {
  digitalWrite(SPISRAM_HOLD, state);
}

void SPISRAM::reset(void) {
  for (int i = 0; i < 5; i++) {
    beginAccess();
    transfer(0xff); // RSTIO
    endAccess();
  }
}

inline void SPISRAM::beginAccess(void) {
  digitalWrite(SPI_SS, LOW);
  SPI.beginTransaction(SPISettings(SPI_CLK, MSBFIRST, SPI_MODE0));
}

inline void SPISRAM::endAccess(void) {
  digitalWrite(SPI_SS, HIGH);
  SPI.endTransaction();
}

void SPISRAM::setMode(void) {
  beginAccess();
  transfer(0x01); // WRMR
  transfer(0x40); // Mode=sequential
  endAccess();
}

void SPISRAM::beginWrite(void) {
  beginAccess();
  transfer(0x02); // Write command
  transfer(0x00); // Address 2 (Required by 1Mbit SRAM, 23LC1024)
  transfer(0x00); // Address 1
  transfer(0x00); // Address 0
  curr_bit_ptn = 0x80;
  curr_byte = default_val;
}

void SPISRAM::beginRead(void) {
  beginAccess();
  transfer(0x03); // Read command
  transfer(0x00); // Address 2 (Required by 1Mbit SRAM, 23LC1024)
  transfer(0x00); // Address 1
  transfer(0x00); // Address 0
}

void SPISRAM::disconnect(void) {
  digitalWrite(SPI_SCK, LOW);
  pinMode(SPI_SS,   OUTPUT);
  pinMode(SPI_SCK,  INPUT);
  pinMode(SPI_MOSI, INPUT);
  pinMode(SPI_MISO, INPUT);
  SPCR &= ~0x40;    // SPE=0, SPI I/F disable
}

void SPISRAM::connect(void) {
  digitalWrite(SPI_SCK, LOW);
  pinMode(SPI_SS,   OUTPUT);
  pinMode(SPI_SCK,  OUTPUT);
  pinMode(SPI_MOSI, OUTPUT);
  pinMode(SPI_MISO, INPUT);
  SPCR |= 0x40;    // SPE=1, SPI I/F enable
}

void SPISRAM::fill(uint8_t a) {
  beginWrite();
  for (unsigned long i = 0; i < SPISRAM_CAPACITY_BYTE; i++) {
    transfer(a + i);
  }
  endAccess();
}

void SPISRAM::clear(void) {
  beginWrite();
  for (unsigned long i = 0; i < SPISRAM_CAPACITY_BYTE; i++) {
    transfer(0);
  }
  endAccess();
}

void SPISRAM::dump(int count) {
  beginRead();
  byte dt;
  for (int i = 0; i < count; i++) {
    dt = transfer(0);
    Serial.print(dt, DEC);
    Serial.print(F(" "));
  }
  endAccess();
  Serial.println(F(""));
}

void SPISRAM::writeBit(uint8_t dt) {
  curr_byte = dt ? (curr_byte | curr_bit_ptn) : (curr_byte & ~curr_bit_ptn);
  curr_bit_ptn >>= 1;
  if(curr_bit_ptn == 0x00) {
    transfer(curr_byte);    // write out a completed byte
    curr_bit_ptn = 0x80;
    curr_byte = default_val;
  }
}

void SPISRAM::flush(void) {
  if(curr_bit_ptn != 0x80) {
    transfer(curr_byte);    // write out the residual bit data
  }
}
