#ifndef _FDD_H_
#define _FDD_H_

#define STEP_RATE     (10)  /* ms */

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

    // FDD write gate control functions !! DANGER !!
    inline void writeGate(bool onOff);
    inline void setWriteGateSafeguard(void);
    inline void releaseWriteGateSafeguard(void);
};

#endif
