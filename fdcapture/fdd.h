#ifndef _FDD_H_
#define _FDD_H_

#define STEP_RATE     (10)  /* ms */

//#define MACRO_WAIT_INDEX() { uint8_t curr, prev; prev = PINC & 0x01; while(true) { curr = PINC & 0x01; if(prev==1 && curr==0) break; prev = curr; }}
#define MACRO_WAIT_INDEX() \
  while((PINC & 0x01)==1) ; \
  while((PINC & 0x01)==0) ; \
  while((PINC & 0x01)==1) ;

#define MACRO_ENABLE_WG()  PORTC &= 0b11011111;
#define MACRO_DISABLE_WG() PORTC |= 0b00100000; 

// This class changes the configuration of Timer 1 for disc rotate speed measurement purpose
class FDD {
  private:
    int drive_type;     // 0=2D, 1=2DD/2HD
    int media_type;     // 0=2D, 1=2DD/2HD
    bool write_gate_safeguard;
  public:
    FDD();

    enum ENUM_DRV_MODE {
      mode_2d  = 0,
      mode_2dd = 1
    };

    enum ENUM_MEDIA_TYPE {
      media_2d = 0,
      media_2dd = 1,
      media_2hd = 2
    };


    void init( void );
    void set_drive_type(enum ENUM_DRV_MODE mode);
    inline enum ENUM_DRV_MODE get_drive_type(void);
    void set_media_type(enum ENUM_DRV_MODE mode);
    inline enum ENUM_DRV_MODE get_media_type(void);
    inline void step1(void);
    void step(void);
    void setStepDir(uint8_t dir);
    inline uint8_t readIndex(void);
    uint8_t readTRK00(void);
    void stepIn(void);
    void stepOut(void);
    void track00(void);
    inline void waitIndex(void);
    void seek(int current, int target);
    void side(int side);
    void motor(bool onoff);
    void head(bool onoff);
    void detect_drive_type(void);
    float measure_rpm();
    uint16_t measure_rpm_tick();

    // FDD write gate control functions !! DANGER !!
    inline void enableWriteGate(void);
    inline void disableWriteGate(void);
    inline void setWriteGateSafeguard(void);
    inline void releaseWriteGateSafeguard(void);
    inline bool isWriteProtected(void);
};

#endif
