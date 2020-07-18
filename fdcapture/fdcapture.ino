#include <SPI.h>

#include <avr/pgmspace.h>

#define SPISRAM_HOLD  (A4)
#define FD_TRK00      (A3)  /* A3 */
#define FD_READY      (A2)  /* A2 */
#define CAP_ACTIVE    (A1)  /* A1 */
#define FD_INDEX      (A0)  /* A0 */
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
#define FD_WP         (2)

// This class changes the configuration of Timer 1 for disc rotate speed measurement purpose
class FDD {
  private:
    int drive_mode;     // 0=2D, 1=2DD/2HD
  public:
    enum ENUM_DRV_MODE {
      mode_2d,
      mode_2dd
    };

    FDD() {
      //init();
    }
    
    void init( void ) {
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

      set_drive_mode(0); // 2D

      motor(true);      // motor on
      head(true);       // head load on
      side(0);          // side 0
      
      track00();
      side(0);
    }

    void set_drive_mode(int mode) {
      drive_mode = mode;
    }

    void step(void) {
      int iter = drive_mode==ENUM_DRV_MODE::mode_2dd ? 2 : 1;
      for(int i=0; i<iter; i++) {
        digitalWrite(FD_STEP, LOW);
        delay(10);
        digitalWrite(FD_STEP, HIGH);
        delay(10);
      }
    }

    void setStepDir(uint8_t dir) {
      digitalWrite(FD_DIR, dir);
    }

    uint8_t readIndex(void) {
      return digitalRead(FD_INDEX);
    }

    uint8_t readTRK00(void) {
      return digitalRead(FD_TRK00);
    }

    void stepIn(void) {   // Step towards inner track (trk#++)
      setStepDir(LOW);
      step();
    }

    void stepOut(void) {  // Step towards outer track (trk#--)
      setStepDir(HIGH);
      step();
    }
    
    void track00(void) {
      while (readTRK00() == HIGH) {
        stepOut();
      }
    }
    
    inline void waitIndex(void) {      // wait for the index hole detection
      while (readIndex() == LOW);
      delay(10);
      while (readIndex() == HIGH);
    }
    
    void seek(int current, int target) {
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
    
    void side(int side) {
      switch (side) {
        case 0: digitalWrite(FD_SIDE1, HIGH); break;
        case 1: digitalWrite(FD_SIDE1, LOW ); break;
        default: break;
      }
    }

    void motor(bool onoff) {
      if(onoff) {
        digitalWrite(FD_MOTOR, LOW);    // Motor start
      } else {
        digitalWrite(FD_MOTOR, HIGH);   // Motor stop
      }
    }

    void head(bool onoff) {
      if(onoff) {
        digitalWrite(FD_HEAD_LOAD,  LOW);   // Head load on
      } else {
        digitalWrite(FD_HEAD_LOAD, HIGH);   // Head load off
     }
    }

    
    // TCNT1 = 250KHz count
    // INDEX pulse = 4.33ms negative pulse
    
    long measure_rpm() {
      uint8_t TCCR1A_bkup = TCCR1A;
      TCCR1A = TCCR1A & 0xfc;   // Timer1, 16b timer, WGM11,WGM10 = 0,0 = Normal mode. default = 0,1 = PWM, Phase correct, 8-bit

      long tcnt1_, tcnt1;
      waitIndex();
      tcnt1_ = TCNT1;
      waitIndex();
      tcnt1 = TCNT1;
      tcnt1 = tcnt1 > tcnt1_ ? tcnt1 - tcnt1_ : tcnt1 - tcnt1_ + 65535;
      Serial.println(((tcnt1*1000)/250e3), DEC);   // ms

      TCCR1A = TCCR1A_bkup;
      return tcnt1;
    }
} FDD;



class FDCapture {
  public:
    FDCapture() {
      init();
    }
    void init(void) {
      disable();
      pinMode(CAP_RST,      OUTPUT);
      pinMode(CAP_EN,       OUTPUT);
      pinMode(CAP_ACTIVE,   OUTPUT);
    }

    inline void enable(void) {
      digitalWrite(CAP_RST,    HIGH);
      digitalWrite(CAP_EN,     LOW);
      digitalWrite(CAP_ACTIVE, HIGH);
    }

    inline void disable(void) {
      digitalWrite(CAP_ACTIVE, LOW);
      digitalWrite(CAP_EN,     HIGH);
      digitalWrite(CAP_RST,    LOW);
    }

} FDCap;


class SPISRAM {
  private:
    const unsigned long SPI_CLK = 4e6;
  public:
    //const unsigned long SPISRAM_CAPACITY = 2*65535UL;   // 1Mbit SRAM
    const unsigned long SPISRAM_CAPACITY = 65535UL;   // 512Kbit SRAM
    //const unsigned long SPISRAM_CAPACITY = 200UL;

    SPISRAM() {
      init();
    }
    
    void init(void) {
      SPI.begin();
      digitalWrite(SPISRAM_HOLD, HIGH);
      pinMode(SPISRAM_HOLD, OUTPUT);
      reset();
      setMode();
    }

    inline uint8_t transfer(uint8_t dt) {
      return SPI.transfer(dt);
    }
  
    inline void hold(uint8_t state) {
      digitalWrite(SPISRAM_HOLD, state);
    }

    void reset(void) {
      for (int i = 0; i < 5; i++) {
        beginAccess();
        transfer(0xff); // RSTIO
        endAccess();
      }
    }
    
    inline void beginAccess(void) {
      digitalWrite(SPI_SS, LOW);
      SPI.beginTransaction(SPISettings(SPI_CLK, MSBFIRST, SPI_MODE0));
    }

    inline void endAccess(void) {
      digitalWrite(SPI_SS, HIGH);
      SPI.endTransaction();
    }

    void setMode(void) {
      beginAccess();
      transfer(0x01); // WRMR
      transfer(0x40); // Mode=sequential
      endAccess();
    }
    
    void beginWrite(void) {
      beginAccess();
      transfer(0x02); // Write command
      transfer(0x00); // Address 2 (Required by 1Mbit SRAM, 23LC1024)
      transfer(0x00); // Address 1
      transfer(0x00); // Address 0
    }
    
    void beginRead(void) {
      beginAccess();
      transfer(0x03); // Read command
      transfer(0x00); // Address 2 (Required by 1Mbit SRAM, 23LC1024)
      transfer(0x00); // Address 1
      transfer(0x00); // Address 0
    }

    void disconnect(void) {
      digitalWrite(SPI_SCK, LOW);
      pinMode(SPI_SS,   OUTPUT);
      pinMode(SPI_SCK,  INPUT);
      pinMode(SPI_MOSI, INPUT);
      pinMode(SPI_MISO, INPUT);
      SPCR &= ~0x40;    // SPE=0, SPI I/F disable
    }
    
    void connect(void) {
      digitalWrite(SPI_SCK, LOW);
      pinMode(SPI_SS,   OUTPUT);
      pinMode(SPI_SCK,  OUTPUT);
      pinMode(SPI_MOSI, OUTPUT);
      pinMode(SPI_MISO, INPUT);
      SPCR |= 0x40;    // SPE=1, SPI I/F enable
    }

    void fill(byte a) {
      beginWrite();
      for (unsigned long i = 0; i < SPISRAM_CAPACITY; i++) {
        transfer(a + i);
      }
      endAccess();
    }
    
    void clear(void) {
      beginWrite();
      for (unsigned long i = 0; i < SPISRAM_CAPACITY; i++) {
        transfer(0);
      }
      endAccess();
    }
    
    void dump(int count) {
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
} SPISRAM;




// TCNT1 = 250KHz count


void trackRead(void) {
  SPISRAM.beginWrite();
  SPISRAM.hold(LOW);
  SPISRAM.disconnect();

  FDD.waitIndex();

  // Start captuering
  SPISRAM.hold(HIGH);
  FDCap.enable();
  delay(100);                     // wait for 100ms == half rotation

  FDD.waitIndex();
  delay(5);                       // Capture the top of the 2nd rotation

  // Stop capturing
  digitalWrite(SPI_SS, HIGH);

  FDCap.disable();
  SPISRAM.connect();
  SPISRAM.endAccess();
}


void print8BIN(byte dt) {
  for (int i = 7; i >= 0; i--) {
    Serial.print((dt >> i) & 1, DEC);
  }
}

void printHex(byte dt) {
  if(dt<0x10) {
    Serial.print(F("0"));
  }
  Serial.print(dt, HEX);
}

//const unsigned long TRACK_CAPACITY =  25000UL; // 200ms*1MHz /8bit
const unsigned long TRACK_CAPACITY   = 100000UL; // 200ms*4MHz /8bit

void dumpTrack_bit(unsigned long bytes=0UL) {
  SPISRAM.beginRead();

  if(bytes==0) bytes = TRACK_CAPACITY;
  for (unsigned long i = 0; i < bytes; i++) {
    byte dt = SPISRAM.transfer(0);
    print8BIN(dt);
    //Serial.print(F(" "));
  }
  Serial.println(F(" "));
  SPISRAM.endAccess();
}

void dumpTrack_hex(unsigned long bytes=0UL) {

  Serial.println(F("TRACK_DUMP_START ========================================="));
  SPISRAM.beginRead();

  if(bytes==0) bytes = TRACK_CAPACITY;
  for (unsigned long i = 0; i < bytes; i++) {
    byte dt = SPISRAM.transfer(0);
    printHex(dt);
    if(i % 64==63) {
      Serial.println(F(""));
    }
  }
  SPISRAM.endAccess();
  Serial.println(F("TRACK_DUMP_END   ========================================="));
}

void dumpTrack_encode(unsigned long bytes=0UL) {

  SPISRAM.beginRead();

  if(bytes==0) bytes = TRACK_CAPACITY;

  int prev = 0;
  int count = 1;
  int b;
  char str[2] = {' ', '\0'};
  int chr_count = 0;
  for (unsigned long i = 0; i < bytes; i++) {
    int dt = SPISRAM.transfer(0);
    for(int p=0; p<8; p++) {
      b = ((dt & 0x80u) == 0x80u) ? 1 : 0;
      dt <<= 1;
      if(b==prev) {
        count++;
      } else {
        if(count > 'z'-' ') count = 'z'-' ';
        str[0] = count + ' ';
        if(chr_count % 100==0) {
          Serial.print("~");    // Start line code
        }
        Serial.print(str);
        count = 1;
        chr_count++;
        if(chr_count % 100==99) {
          chr_count = 0;
          Serial.println(F(""));
        }
      }
      prev = b;
    }
  }
  SPISRAM.endAccess();
  Serial.println(F(""));
}

void histogram(unsigned long bytes=0UL) {
  unsigned int histo[10];
  for(int i=0; i<10; i++) histo[i]=0UL;

  SPISRAM.beginRead();

  if(bytes==0) bytes = TRACK_CAPACITY;

  int prev = 0;
  int count = 1;
  for(unsigned long i = 0; i < bytes; i++) {
    byte dt = SPISRAM.transfer(0);
    for(int j=0; j<8; j++) {
      int b = (dt & 0x80)==0x80 ? 1 : 0;
      dt <<= 1;
      if(b == prev) {
        count++;     
      } else {
        prev = b;
        histo[count]++;
        count = 1;
      }
    }
  }
  SPISRAM.endAccess();

  for(int i=0; i<10; i++) {
    Serial.print(i);
    Serial.print(F(" : "));
    Serial.println(histo[i]);
  }
}
// Calibrate motor speed
void revolution_calibration(void) {
  while(1) {
    FDD.measure_rpm();
    //trackRead();
    //histogram();
  }
}


// Read single track
void read_single_track(void) {
  FDD.track00();
  FDD.seek(0,1);
  FDD.side(1);
  SPISRAM.clear();
  Serial.println(F("**TRACK_READ 0 0"));
  trackRead();
  dumpTrack_encode(TRACK_CAPACITY);
  //dumpTrack_hex(0x2000);
  //dumpTrack_hex(TRACK_CAPACITY);
  Serial.println(F("**TRACK_END"));
  Serial.print("Completed.");
  while(1) ;
}

// Read tracks
void read_tracks(int start_track, int start_side, int end_track, int end_side) {
  FDD.track00();
  size_t curr_trk = 0;
  for(int trk=start_track; trk<=end_track; trk++) {
    FDD.seek(curr_trk, trk);
    curr_trk = trk;
    for(int side=start_side; side<=end_side; side++) {
      FDD.side(side);    
      SPISRAM.clear();
      trackRead();

      Serial.print(F("**TRACK_READ "));
      Serial.print(trk);
      Serial.print(F(" "));
      Serial.println(side); 
      dumpTrack_encode(TRACK_CAPACITY);
      Serial.println(F("**TRACK_END"));
    }
  }
  //dumpTrack_hex(TRACK_CAPACITY);
  //dumpTrack_bit(10);
  Serial.println(F("Completed."));

  FDD.motor(false);
  FDD.head(false);
  while(true) ;
}

// Memory test
void memory_test(void) {
  static int c = 0;
  FDD.waitIndex();
  SPISRAM.fill(c++);
  SPISRAM.dump(40);
  //dumpTrack_bit();
}

void timing_light(int freq) {
  int period = 1000/freq;
  while(1) {
    digitalWrite(CAP_ACTIVE, HIGH);
    delay(period*0.2);
    digitalWrite(CAP_ACTIVE, LOW);
    delay(period*0.8);
  }
}


void setup() {
  // Make sure that the FD_capture board doesn't drive MOSI and SCK lines
  FDCap.init();
  SPISRAM.init();

  Serial.begin(115200);

  FDD.init();                   // Motor on, Head load on
  FDD.set_drive_mode(FDD::ENUM_DRV_MODE::mode_2dd);
  delay(500);
  for (int i = 0; i < 20; i++) {
    FDD.stepIn();
  }
  FDD.track00();

  FDD.seek(0,2);
  SPISRAM.clear();
}

void loop() {
  //timing_light(50);
  //revolution_calibration();

  read_tracks(0,0, 39,1);
  //read_tracks(3,1, 3,1);
}
