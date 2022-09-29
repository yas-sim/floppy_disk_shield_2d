// 2D/2DD Floppy disk capture shield control software

#include <stdio.h>
#include <limits.h>

#include <SPI.h>
#include <avr/pgmspace.h>

#include "fdd.h"
#include "spi_sram.h"
#include "fdcaptureshield.h"

uint8_t cmdBuf[cmdBufSize+1];
  
size_t g_spin_ms;         // FDD spin speed (ms)

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
// read_overlap: overlap percentage to a spin. '5' means +5% (in total 105%) of 1 spin time.
void trackRead(int read_overlap) {
  spisram.beginWrite();
  spisram.hold(LOW);
  spisram.disconnect();           // Disconnect SPI SRAM from Arduino

  fdd.waitIndex();

  // Start captuering
  spisram.hold(HIGH);
  FDCap.enable();
  delay(g_spin_ms / 10);          // wait for 10% of spin

  fdd.waitIndex();
  delay((g_spin_ms * read_overlap) / 100);  // (overlap)% over capturing (read overlap)

  // Stop capturing
  digitalWrite(SPI_SS, HIGH);

  FDCap.disable();
  spisram.connect();
  spisram.endAccess();
}


// Read tracks  (track # = 0-79 (,83))
void read_tracks(int start_track, int end_track, int read_overlap) {
  fdd.track00();

  Serial.print("**SAMPLING_RATE 4000000\n");    // 4MHz is the default sampling rate of the Arduino FD shidld.

  const unsigned long capture_capacity_byte = 
    (unsigned long)((float)spisram.SPI_CLK * (float)g_spin_ms * ((float)(read_overlap+100)/100.f) ) / 8 / 1000;
  Serial.print(";CAPACITY[bytes]:");
  Serial.print(capture_capacity_byte);
  Serial.print("\n");

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

    trackRead(read_overlap);

    dumpTrack_encode(capture_capacity_byte);    // Dump captured data
    //dumpTrack_encode(TRACK_CAPACITY_BYTE);    // SPI SRAM full dump
    Serial.println(F("**TRACK_END"));
  }
}


// =================================================================


// Write single track
void trackWrite(uint32_t bits_to_write) {
  spisram.beginRead();
  spisram.hold(LOW);
  spisram.disconnect();           // Disconnect SPI SRAM from Arduino

  fdd.releaseWriteGateSafeguard(); // Release write gate safeguard
  fdd.waitIndex();

  // Start writing
  spisram.hold(HIGH);
  fdd.writeGate(true);            // Enable WG
  FDCap.enable();
  delay(g_spin_ms / 10);          // wait for 10% of spin

  fdd.waitIndex();
  fdd.writeGate(false);           // Disable WG right after the next index hole detection

  digitalWrite(SPI_SS, HIGH);
  FDCap.disable();
  spisram.connect();
  spisram.endAccess();
  fdd.setWriteGateSafeguard();
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
  uint8_t test = 0;

  uint8_t mode = 0;     // Command mode
  uint8_t dist = 0;    // data pulse distance
  uint8_t bit_dt = 0;
  Serial.println(F("++READY"));
  while(true) {
    readLine(cmdBuf, cmdBufSize);
    uint8_t cmdLen = strlen(cmdBuf);
    if(cmdLen > cmdBufSize) cmdLen = cmdBufSize;
    if(cmdBuf[0] == '*' && cmdBuf[1] == '*') {          // CMD
      if(cmdBuf[2] == 'T' && cmdBuf[8] == 'R') {        // **TRACK_READ 0 0
        mode = 1;   // Read track data mode
        sscanf(cmdBuf+12, "%d %d", &trk, &sid);
        fdd.seek(curr_trk, trk);
        fdd.side(sid);
        curr_trk = trk;
        spisram.fill(0xff);
        spisram.beginWrite();
      } else if(cmdBuf[2] == 'T' && cmdBuf[8] == 'E') { // **TRACK_END
        mode = 0;   // Command mode
        spisram.flush();
        spisram.endAccess();
        uint32_t bits = spisram.getLength();
        trackWrite(bits);
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
              dist = (dist+4) & 0x00f8u;      // assuming the bit cell width is 8.
            }
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


// Calibrate motor speed
void revolution_calibration(void) {
  float spin;
  while (1) {
    spin = fdd.measure_rpm();
    Serial.println(spin * 1000, DEC); // ms
  }
}

// Measure FDD spindle speed (measure time for 5 spins)
void report_spindle_speed(void) {
    float spin = 0.f;
    for(int i=0; i<5; i++) {
      spin += fdd.measure_rpm();
    }
    spin /= 5;
    Serial.print(F("**SPIN_SPD "));
    Serial.println(spin,8);
    g_spin_ms = (int)(spin*1000);
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

    int max_capture_time_ms = (int)(((spisram.SPISRAM_CAPACITY_BYTE*8.f) / spisram.SPI_CLK)*1000.f);
    int capture_time_ms     = (int)(g_spin_ms * (1.f + read_overlap/100.f));
    if(capture_time_ms > max_capture_time_ms) {
      read_overlap = (int)((((float)max_capture_time_ms / (float)g_spin_ms) - 1.f) * 100.f);
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
    Serial.println(F("**Revolution calibration mode"));
    revolution_calibration();
  }
  fdd.head(false);
  fdd.motor(false);
}
