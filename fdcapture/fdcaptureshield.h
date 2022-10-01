#ifndef _FDCAPTURESHIELD_H_
#define _FDCAPTURESHIELD_H_

class FDCaptureShield {
  public:
    FDCaptureShield();

    void init(void);
    inline void enable_sampling_clock(void);
    inline void disable_sampling_clock(void);

    inline void connect(void);
    inline void connect_and_standby(void);
    inline void disconnect(void);
}; 

#define cmdBufSize (110)

#endif
