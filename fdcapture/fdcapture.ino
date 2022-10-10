// 2D/2DD Floppy disk capture shield control software

#include <stdio.h>
#include <limits.h>

#include <SPI.h>
#include <avr/pgmspace.h>

#include "fdd.h"
#include "spi_sram.h"
#include "fdcaptureshield.h"

#if !defined(__AVR_ATmega328P__)
#error This program can only run on Arduino Uno.
#endif

uint8_t cmdBuf[cmdBufSize+1];

uint16_t g_spin_tick;          // FDD spin time (Timer 1 tick count @ 250KHz)
uint32_t g_calibrated_clock;   // Calibrated timer1 clock

// GPIO mapping
#define FD_WG         (A5)   // Write gate signal !!DANGER!!
#define SPISRAM_HOLD  (A4)
#define FD_TRK00      (A3)
#define FD_READY      (A2)
#define CAP_ACTIVE    (A1)
#define FD_INDEX      (A0)
#define SPI_SCK       (13)
#define SPI_MISO      (12)
#define SPI_MOSI      (11)
#define SPI_SS        (10)
#define FD_STEP       (9)
#define FD_DIR        (8)
#define FD_MOTOR      (7)
#define FD_HEAD_LOAD  (6)
#define FD_SIDE1      (5)
#define CAP_RST       (4)
#define CAP_EN        (3)
#define FD_WP         (2)  // WP == LOW

void debug_blink(void)
{
  while(true) {
    digitalWrite(CAP_ACTIVE, HIGH);
    delay(300);
    digitalWrite(CAP_ACTIVE, LOW);
    delay(300);
  }
}

// Objects
FDD fdd;
SPISRAM spisram;
FDCaptureShield FDCap;

const unsigned long TRACK_CAPACITY_BYTE   = ((1024L*1024L)/8L); // 1Mbit SRAM full capacity


void dumpTrack_encode(unsigned long bytes = 0UL) {

  spisram.beginRead();

  if (bytes == 0) bytes = TRACK_CAPACITY_BYTE;

  int prev = 0;
  int count = 1;
  int b;
  int chr_count = 0;
  byte out;
  for (unsigned long i = 0; i < bytes; i++) {
    int dt = spisram.transfer(0);
    const uint8_t encode_base = ' ';
    const uint8_t max_length = 'z'-encode_base;
    const uint8_t extend_char = '{';
    for (int p = 0; p < 8; p++) {
      b = (dt & 0x80u) ? 1 : 0;
      dt <<= 1;
      if (b == prev) {    // no pulse
        if(++count >= max_length) {
          if (chr_count == 0) {
            Serial.write('~');    // Start line code
          }
          Serial.write(extend_char);        // state extend character (extend pulse-to-pulse period without pulse)
          count -= max_length;
          chr_count++;
          if (chr_count == 99) {
            chr_count = 0;
            Serial.println("");
          }
        }
      } else {            // pulse
        out = count + encode_base;
        if (chr_count == 0) {
          Serial.write('~');    // Start line code
        }
        Serial.write(out);
        count = 1;
        chr_count++;
        if (chr_count == 99) {
          chr_count = 0;
          Serial.println("");
        }
      }
      prev = b;
    }
  }
  spisram.endAccess();
  Serial.println(F(""));
}


// =================================================================


// Read single track
void trackRead(uint16_t capture_tick_count) {
  spisram.beginWrite();
  spisram.hold(LOW);
  spisram.disconnect();                              // Disconnect SPI SRAM from Arduino

  noInterrupts();
  uint8_t TCCR1A_bkup = TCCR1A;
  uint8_t TCCR1B_bkup = TCCR1B;
  TCCR1A &= 0xfc;            // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit
  TCCR1B  = 0x03;            // Timer1, WGM13,WGM12 = 0,0 / CS12,CS11,CS10 = 0,1,1 = clkIO/64

  MACRO_WAIT_INDEX();                                // wait for next index pulse
  TCNT1 = 0;                                         // Reset timer counter

  // Start captuering
  MACRO_DISABLE_SPI_HOLD();
  MACRO_FDCAP_CONNECT();

  while(TCNT1 < capture_tick_count) /* NOP */ ;

  // Stop capturing
  MACRO_DISABLE_SAMPLING_CLOCK();

  TCCR1A = TCCR1A_bkup;
  TCCR1B = TCCR1B_bkup;
  interrupts();

  FDCap.disconnect();
  spisram.connect();
  spisram.endAccess();
}

// Read tracks  (track # = 0-79 (,83))
void read_tracks(int start_track, int end_track, int read_overlap) {
  fdd.track00();

  Serial.print("**SAMPLING_RATE 4000000\n");    // 4MHz is the default sampling rate of the Arduino FD shidld.

  uint32_t capture_tick_count = ((100 + (uint32_t)read_overlap) * (uint32_t)g_spin_tick) / 100;
  if(capture_tick_count > 0xffffu) capture_tick_count = 0xffffu;
  uint32_t capture_capacity_byte = ((4e6 / g_calibrated_clock) * capture_tick_count) / 8;

  Serial.print(";CAPACITY[bytes]:");
  Serial.println(capture_capacity_byte);

  size_t curr_trk = 0;
  for (size_t trk = start_track; trk <= end_track; trk++) {
    size_t fdd_track = trk / 2;
    size_t fdd_side  = trk % 2;
    fdd.seek(curr_trk, fdd_track);
    curr_trk = fdd_track;

    fdd.side(fdd_side);
    spisram.clear();

    Serial.print(F("**TRACK_READ "));
    Serial.print(fdd_track);
    Serial.print(F(" "));
    Serial.println(fdd_side);

    trackRead(capture_tick_count);

    dumpTrack_encode(capture_capacity_byte);    // Dump captured data
    //dumpTrack_encode(TRACK_CAPACITY_BYTE);    // SPI SRAM full dump
    Serial.println(F("**TRACK_END"));
  }
}


// =================================================================


uint8_t count_space_chars(uint8_t *str) {
  uint8_t count = 0;
  uint8_t prev = '\0';
  while(*str != '\0') {
    if(*str == ' ' && prev != ' ') {
      count++;
    }
    prev = *str++;
    if(count > 10) break;   // safeguard
  }
  return count;
}

// Write single track
void trackWrite(uint32_t bits_to_write, uint16_t time_out_tick=0 /* 1tick=250KHz */) {

#if 0
  spisram.beginRead();
  // SPI SRAM contents dump - debug purpose
  for(int i=0; i<0x2000; i++) {
    uint8_t dt = spisram.transfer(0);
    if(dt < 0x10) Serial.print("0");
    Serial.print(dt, HEX);
    //if(i % 32==31) Serial.print("\n");
  }
  Serial.println();
  spisram.endAccess();
#endif

  spisram.beginRead();
  spisram.hold(LOW);
  spisram.disconnect();              // Disconnect SPI SRAM from Arduino

  noInterrupts();
  uint8_t TCCR1A_bkup = TCCR1A;
  uint8_t TCCR1B_bkup = TCCR1B;
  TCCR1A &= 0xfc;            // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit
  TCCR1B  = 0x03;            // Timer1, WGM13,WGM12 = 0,0 / CS12,CS11,CS10 = 0,1,1 = clkIO/64

  MACRO_FDCAP_CONNECT_AND_STANDBY();          // Enable fd-shield, keep SCK line low.

  MACRO_WAIT_INDEX();
  TCNT1 = 0;                                  // Reset timer counter

  // Start writing
  MACRO_ENABLE_WG();                          // Enable WG
  MACRO_DISABLE_SPI_HOLD();
  MACRO_ENABLE_SAMPLING_CLOCK();              // Start supplying 4MHz clock to SCK

  if(time_out_tick == 0) {
    MACRO_WAIT_INDEX();                       // wait for next index pulse
  } else {
    while(TCNT1 < time_out_tick) /* NOP */ ;  // Wait until specified time passed
  }
  MACRO_DISABLE_WG();                         // Disable WG right after the next index hole detection

  TCCR1A = TCCR1A_bkup;                       // Restore timer1 setting
  TCCR1B = TCCR1B_bkup;
  interrupts();

  digitalWrite(SPI_SS, HIGH);
  FDCap.disconnect();
  spisram.connect();
  spisram.endAccess();
}

// Write tracks
// normalize_mode : 0=no normalize, 1=perform normalize
void write_tracks(int normalize_mode) {
  const uint8_t encode_base = ' ';
  const uint8_t max_length = 'z'-encode_base;
  const uint8_t extend_char = '{';
  const uint8_t bit_cell      = 8;
  const uint8_t bit_cell_half = bit_cell / 2;

  fdd.track00();
  int curr_trk = 0;
  int trk, sid;
  unsigned int write_bits = 0;   // number of bits to write
  uint8_t test = 0;

  uint8_t mode = 0;     // Command mode
  uint8_t dist = 0;    // data pulse distance
  uint8_t bit_dt = 0;
  uint64_t total_bits = 0L;
  bool overflow_warning = false;

  // Measure spindle spin time (1 tick = 250KHz)
  uint32_t spin_time_tick = 0;
  for(int i = 0; i < 4; i++) {
    spin_time_tick += fdd.measure_rpm_tick();
  }
  spin_time_tick /= 4;
  Serial.print("#SPIN_TIME_TICK $");
  Serial.println(spin_time_tick, HEX);

  Serial.println(F("++READY"));
  while(true) {
    readLine(cmdBuf, cmdBufSize);
    uint8_t cmdLen = strlen(cmdBuf);
    if(cmdLen > cmdBufSize) cmdLen = cmdBufSize;
    if(cmdBuf[0] == '*' && cmdBuf[1] == '*') {          // CMD
      if(cmdBuf[2] == 'T' && cmdBuf[8] == 'R') {        // **TRACK_READ 0 0
        mode = 1;   // Read track data mode
        if(count_space_chars(cmdBuf) == 3) {
          sscanf(cmdBuf+12, "%d %d %d", &trk, &sid, &write_bits); // write will finish after (write_bits) written
        } else {
          sscanf(cmdBuf+12, "%d %d", &trk, &sid);
          write_bits = 0;                               // Write will finish on 2nd index hole detection
        }
        FDCap.disconnect();                             // CAP_ACTIVATE=LOW, CAP_EN=HIGH
        spisram.connect();                              // Activate SPI_SS, SPI_SCK, SPI_MOSI, SPI_MISO
        fdd.seek(curr_trk, trk);
        fdd.side(sid);
        curr_trk = trk;
        total_bits = 0;
        overflow_warning = false;
        spisram.fill(0xff);
        spisram.beginWrite();
      } else if(cmdBuf[2] == 'T' && cmdBuf[8] == 'E') { // **TRACK_END
        mode = 0;   // Command mode
        spisram.flush();
        spisram.endAccess();
        uint32_t bits = spisram.getLength();
        trackWrite(bits, write_bits);
        if(write_bits > 0) {
          Serial.print(F("\n#$"));
          Serial.print(write_bits, HEX);
          Serial.println(F(" written."));
        }
      } else if(cmdBuf[2] == 'M' && cmdBuf[8] == 'T') { // **MEDIA_TYPE
      } else if(cmdBuf[2] == 'S' && cmdBuf[7] == 'S') { // **SPIN_SPD 0.199
      } else if(cmdBuf[2] == 'O' && cmdBuf[6] == 'L') { // **OVERLAP 0
      } else if(cmdBuf[2] == 'C' && cmdBuf[7] == 'E') { // **COMPLETED
        break;
      }
    }
    if(mode == 1) {
      if(cmdBuf[0] == '~') {                // Pulse data line
        for(uint8_t i = 1; i < cmdLen; i++) {   // skip '~' on the top of the line
          if(cmdBuf[i] < ' ') continue;
          dist = cmdBuf[i] - encode_base;
          if(dist >= 1) {
            if(normalize_mode == 1) {
              //dist = (dist + bit_cell_half) & (~(bit_cell-1));
              dist = (dist+4) & 0b11111000u;      // assuming the bit cell width is 8 (2D/2DD).
              //dist = (dist+2) & 0b11111100u;      // assuming the bit cell width is 4 (2HD).
            }
            if(total_bits + dist > spisram.SPISRAM_CAPACITY_BYTE * 8) {   // SPI SRAM overflow
              if(overflow_warning == false) {
                Serial.println("\n!!SPI-SRAM OVERFLOWED");
                overflow_warning = true;
              }
              dist = 0;
              continue;
            }
            total_bits += dist;
            if(cmdBuf[i] != extend_char && dist <= max_length) {
              for(uint8_t b = 0; b < dist - 1; b++) {
                spisram.writeBit(1);
              }
              spisram.writeBit(bit_dt);         // make a pulse
            } else {
              for(uint8_t b = 0; b < max_length; b++) {
                spisram.writeBit(1);            // don't make pulse
              }
            }
          }
        }
      }
    }
    Serial.println("++ACK");
  };
}

// =================================================================

// Testing SPI SRAM
void test_spi_sram(void) {
  const uint32_t SPISRAM_CAPACITY_BYTE = 2 * 65536UL; // 1Mbit SRAM (bytes)

  spisram.connect();

  Serial.println(F("Testing SPI SRAM..."));
  spisram.beginWrite();
  for(uint64_t adr = 0; adr < SPISRAM_CAPACITY_BYTE; adr++) {
    for(uint8_t bit = 0x80u; bit > 0; bit >>= 1) {
      spisram.writeBit((adr & bit) ? 1 : 0);
    }
  }
  spisram.flush();
  spisram.endAccess();

  uint32_t bits = spisram.getLength();
  Serial.println(F("Write completed."));
  Serial.print(bits);
  Serial.println(F(" bits written."));

#if 0
  // error injection
  spisram.beginWrite();
  spisram.transfer(0x08);
  spisram.endAccess();
#endif

  spisram.beginRead();
  for(uint64_t adr = 0; adr < SPISRAM_CAPACITY_BYTE; adr++) {
    uint8_t dt = spisram.transfer(0);
    if(dt != (adr & 0xffu)) {
      Serial.println(F("Compare error ("));
      Serial.print((uint8_t)adr, HEX);
      Serial.print(F(") : C="));
      Serial.print((uint8_t)(adr & 0xffu), HEX);
      Serial.print(F(" - "));
      Serial.println(dt, HEX);
    }
  }
  spisram.endAccess();
  Serial.println(F("Test completed."));
}


// =================================================================

// Calibrate motor speed
void revolution_calibration(void) {
  float spin;
  while(true) {
    spin = fdd.measure_rpm();
    Serial.println(spin * 1000, DEC); // ms
  }
}

// Measure FDD spindle speed (measure time for 5 spins)
void report_spindle_speed(void) {
    float spin = 0.f;
    uint32_t spin_tick = 0;
    for(int i=0; i<5; i++) {
      spin_tick += fdd.measure_rpm_tick();
    }
    spin_tick /= 5;
    spin = (double)spin_tick / (double)g_calibrated_clock;
    Serial.print(F("**SPIN_SPD "));
    Serial.println(spin, 8);
    g_spin_tick = spin_tick;
}

// =================================================================


uint8_t readLine(uint8_t buf[], const uint8_t buf_size) {
  uint8_t ch;
  uint8_t pos = 0;
  buf[0] = '\0';
  while(pos < buf_size) {
    buf[pos] = '\0';
    while(Serial.available()==0);
    ch = Serial.read();
    if(ch == '\n') break;
    if(ch >= ' ' && ch <= 0x7e) {   // stores only readable characters
      buf[pos++] = ch;
    }
  }
  return pos;
}


void setup() {
  // Make sure that the FD_capture board doesn't drive MOSI and SCK lines
  FDCap.init();
  spisram.init();

  Serial.begin(115200);

  fdd.init();                                     // Motor on, Head load on
  delay(200);

  spisram.clear();

  Serial.println("");
  Serial.println(F("**FLOPPY DISK SHIELD FOR ARDUINO"));
  g_calibrated_clock = 250e3;                     // Default clock for timer1
}

// Command format
// "+R strack etrack mode overlap"
// "+V"
void loop() {
  char cmd;

  Serial.println(F("++CMD"));
  readLine(cmdBuf, cmdBufSize);
  if(cmdBuf[0] != '+') {      // Command line must start with '+'.
    Serial.println(F("++ERR"));
    return;
  }
  cmd = toupper(cmdBuf[1]);

  if(cmd == 'R') {
    fdd.head(true);
    fdd.motor(true);
    enum FDD::ENUM_DRV_MODE media_mode = FDD::ENUM_DRV_MODE::mode_2d;
    int start_track, end_track;
    int read_overlap;   // track read overlap (%)
    sscanf(cmdBuf, "+R %d %d %d %d", &start_track, &end_track, &media_mode, &read_overlap);
    fdd.set_media_type(media_mode);
    Serial.println(F("**START"));

    // Detect FDD type (2D/2DD)
    fdd.detect_drive_type();
    fdd.track00();

    report_spindle_speed();

    uint32_t sampling_tick_count = ((100 + (uint32_t)read_overlap) * (uint32_t)g_spin_tick) / 100;
    if(sampling_tick_count > 0xffffu) {
      read_overlap = (int)(((double)0x10000 / (double)g_spin_tick) * 100.f - 100.f);
      Serial.print(F("##READ_OVERLAP IS LIMITED TO "));
      Serial.print(read_overlap);
      Serial.println(F("% BECAUSE THE AMOUNT OF CAPTURE DATA EXCEEDS THE MAX SPI-SRAM CAPACITY."));
    }
    Serial.print(F("**OVERLAP "));
    Serial.println(read_overlap);

    // Read all tracks
    read_tracks(start_track, end_track, read_overlap);

    Serial.println(F("**COMPLETED"));
  }
  // WRITE command needs to be 'WR' not 'W'.
  if(cmd == 'W') {
    fdd.head(true);
    fdd.motor(true);
    if(cmdBuf[2] != 'R') return;
    if(fdd.isWriteProtected() == true) {
      Serial.println(F("++WRITE_PROTECTED"));
    } else {
      uint8_t cmd;
      int normalize_flag;
      sscanf(cmdBuf, "+WR %d", &normalize_flag);
      // Detect FDD type (2D/2DD)
      fdd.detect_drive_type();
      enum FDD::ENUM_DRV_MODE media_mode = FDD::ENUM_DRV_MODE::mode_2d;
      fdd.set_media_type(media_mode);
      if(normalize_flag) {
        Serial.println(F("**Bit pulse timing normalizer activated."));
      }
      write_tracks(normalize_flag);
    }
  }
  if(cmd == 'V') {
    fdd.head(true);
    fdd.motor(true);
    Serial.println(F("**Revolution calibration mode"));
    revolution_calibration();
  }
  if(cmd == 'C') {
    fdd.head(true);
    fdd.motor(true);
    uint16_t tick;
    uint32_t ttl_tick = 0;
    const uint8_t niter = 5;
    for(int i=0; i < niter; i++) {
      tick = fdd.measure_rpm_tick();
      ttl_tick += tick;
    }
    tick = ttl_tick / niter;
    Serial.print(F("++SPIN_TICK "));
    Serial.println(tick, DEC); // ms
  }
  if(cmd == 'T') {
    test_spi_sram();
  }
  if(cmd == 'S') {    // Set timer clock (for timer 1 calibration)
    unsigned long calibrated_clock;
    sscanf(cmdBuf, "+S %ld", &calibrated_clock);
    g_calibrated_clock = calibrated_clock;
    Serial.print(F("#CALIBRATED CLOCK="));
    Serial.println(g_calibrated_clock);
  }
  if(cmd == 'M') {
    // Measure timer1 clock speed for calibration
    noInterrupts();
    uint8_t TCCR1A_bkup = TCCR1A;
    uint8_t TCCR1B_bkup = TCCR1B;
    TCCR1A = 0x00;                    // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit
    TCCR1B = 0x03;                    // Timer1, WGM13,WGM12 = 0,0 / CS12,CS11,CS10 = 0,1,1 = clkIO/64

    Serial.print('S');
    Serial.flush();
    for(int i = 0; i < 40; i++) {         // 250KHz * 0x8000 * 40 = 5.24288 sec
      TCNT1 = 0;
      while(TCNT1 < 0x8000) /* nop */ ;   // 250KHz * 0x8000 = 0.131072 sec
    }
    TCCR1A = TCCR1A_bkup;                 // Restore timer1 setting
    TCCR1B = TCCR1B_bkup;
    Serial.print('E');
    Serial.flush();
    interrupts();
  }
  if(cmd == '@') {    // experimental code
    noInterrupts();
    uint8_t TCCR1A_bkup = TCCR1A;
    uint8_t TCCR1B_bkup = TCCR1B;
    //Serial.println(TCCR1A, BIN);
    //Serial.println(TCCR1B, BIN);
#if 0
    uint16_t count;
    while(true) {
      count = fdd.measure_rpm_tick();
      Serial.println(count, HEX);
    }
#endif
#if 1
    TCCR1A = 0x00;                    // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit
    TCCR1B = 0x03;                    // Timer1, WGM13,WGM12 = 0,0 / CS12,CS11,CS10 = 0,1,1 = clkIO/64
    uint16_t half_period;
    uint32_t calibrated_clock;
    sscanf(cmdBuf, "+@ %ld", &calibrated_clock);
    double target_time = 0.2f;
    half_period = calibrated_clock * target_time;

    for(uint8_t i=0; i<10; i++) {
      PORTC &= ~0x20;                 // WG_
      TCNT1 = 0;                      // Reset timer counter
      while(TCNT1 < half_period) /* NOP */ ;

      PORTC |= 0x20;                  // WG_
      TCNT1 = 0;                      // Reset timer counter
      while(TCNT1 < half_period) /* NOP */ ;
    }
#endif
#if 0
  // Oscillation output by compare match -> OC1A, OC1B pins
  TCCR1A = 0x50;  // OC1A/OC1B toggle on compare match
  TCCR1B = 0x03 + 0x08 /* WGM13,12 = 0,1 = CTC */;
  OCR1A = 0xffff;

  while(1);
#endif

    TCCR1A = TCCR1A_bkup;             // Restore timer1 setting
    TCCR1B = TCCR1B_bkup;
    interrupts();
  }
  //fdd.head(false);
  //fdd.motor(false);
}
