#ifndef _FDCAPTURESHIELD_H_
#define _FDCAPTURESHIELD_H_

class FDCaptureShield {
  public:
    FDCaptureShield();

    void init(void);
    inline void enable(void);
    inline void disable(void);
}; 

#define cmdBufSize (110)

#endif
