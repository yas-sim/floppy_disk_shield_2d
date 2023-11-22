#ifndef _FDCAPTURESHIELD_H_
#define _FDCAPTURESHIELD_H_

#define MACRO_ENABLE_SAMPLING_CLOCK()  PORTC |= 0b00000010;
#define MACRO_DISABLE_SAMPLING_CLOCK() PORTC &= 0b11111101;

#define MACRO_FDCAP_CONNECT_AND_STANDBY() PORTD &= 0b11110111; MACRO_DISABLE_SAMPLING_CLOCK();
#define MACRO_FDCAP_CONNECT()             PORTD &= 0b11110111; MACRO_ENABLE_SAMPLING_CLOCK();

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
