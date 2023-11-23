#include "spi_memory.h"

SPIMEMORY::SPIMEMORY() {}

/*
#define SPI_MEMORY_23LC1024   (0)
#define SPI_MEMORY_CY15B104Q  (1)
#define SPI_MEMORY_TYPE SPI_MEMORY_CY15B104Q
*/

void SPIMEMORY::init(void) {
  SPI.begin();
  SPCR = 0b00010000; // MSTR=1, DORD=0, CPOL=0, CPHA=0
  digitalWrite(SPIMEMORY_HOLD, HIGH);
  pinMode(SPIMEMORY_HOLD, OUTPUT);
  //reset();
#if SPI_MEMORY_TYPE==SPI_MEMORY_23LC1024
  setSramWriteMode();
#endif
  setDefaultValue(0xff);
  curr_bit_ptn = 0x80;
  curr_byte = default_val;
  write_count = 0;
}

void SPIMEMORY::setDefaultValue( uint8_t val ) {
  default_val = val;
}

inline uint8_t SPIMEMORY::transfer(uint8_t dt) {
  return SPI.transfer(dt);
}

inline void SPIMEMORY::hold(uint8_t state) {
  digitalWrite(SPIMEMORY_HOLD, state);
}

void SPIMEMORY::reset(void) {
  for (int i = 0; i < 5; i++) {
    beginAccess();
    transfer(0xff); // RSTIO
    endAccess();
  }
}

void SPIMEMORY::framWriteEnable(void) {
  beginAccess();
  transfer(0x06); // WREN: Write enable latch
  endAccess();
  for(int i=0; i<10; i++) asm("nop \n");
}

inline void SPIMEMORY::beginAccess(void) {
  digitalWrite(SPI_SS, LOW);
  SPI.beginTransaction(SPISettings(SPI_CLK, MSBFIRST, SPI_MODE0));
}

inline void SPIMEMORY::endAccess(void) {
  digitalWrite(SPI_SS, HIGH);
  SPI.endTransaction();
}

void SPIMEMORY::setSramWriteMode(void) {
  beginAccess();
  transfer(0x01); // WRMR
  transfer(0x40); // Mode=sequential
  endAccess();
}

void SPIMEMORY::beginWrite(void) {
#if SPI_MEMORY_TYPE==SPI_MEMORY_CY15B104Q
  framWriteEnable();
#endif
  beginAccess();
  transfer(0x02); // Write command
  transfer(0x00); // Address 2 (Required by 1Mbit SRAM, 23LC1024)
  transfer(0x00); // Address 1
  transfer(0x00); // Address 0
  write_count = 0;
  curr_bit_ptn = 0x80;
  curr_byte = default_val;
}

void SPIMEMORY::beginRead(void) {
  beginAccess();
  transfer(0x03); // Read command
  transfer(0x00); // Address 2 (Required by 1Mbit SRAM, 23LC1024)
  transfer(0x00); // Address 1
  transfer(0x00); // Address 0
}

void SPIMEMORY::disconnect(void) {
  digitalWrite(SPI_SCK, LOW);
  pinMode(SPI_SS,   OUTPUT);
  pinMode(SPI_SCK,  INPUT);
  pinMode(SPI_MOSI, INPUT);
  pinMode(SPI_MISO, INPUT);
  SPCR &= ~0x40;    // SPE=0, SPI I/F disable
}

void SPIMEMORY::connect(void) {
  digitalWrite(SPI_SCK, LOW);
  pinMode(SPI_SS,   OUTPUT);
  pinMode(SPI_SCK,  OUTPUT);
  pinMode(SPI_MOSI, OUTPUT);
  pinMode(SPI_MISO, INPUT);
  SPCR |= 0x40;    // SPE=1, SPI I/F enable
}

void SPIMEMORY::fill(uint8_t a) {
  beginWrite();
  for (unsigned long i = 0; i < SPIMEMORY_CAPACITY_BYTE; i++) {
    transfer(a + i);
  }
  endAccess();
}

void SPIMEMORY::clear(void) {
  beginWrite();
  for (unsigned long i = 0; i < SPIMEMORY_CAPACITY_BYTE; i++) {
    transfer(0);
  }
  endAccess();
}

void SPIMEMORY::dump(int count) {
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

void SPIMEMORY::writeBit(uint8_t dt) {
  curr_byte = dt ? (curr_byte | curr_bit_ptn) : (curr_byte & ~curr_bit_ptn);
  curr_bit_ptn >>= 1;
  if(curr_bit_ptn == 0x00) {
    transfer(curr_byte);    // write out a completed byte
    curr_bit_ptn = 0x80;
    curr_byte = default_val;
  }
  write_count++;
}

void SPIMEMORY::flush(void) {
  if(curr_bit_ptn != 0x80) {
    transfer(curr_byte);    // write out the residual bit data
  }
}
