#ifndef _SPI_SRAM_
#define _SPI_SRAM_

class SPISRAM {
  public:
    const unsigned long SPI_CLK = 4e6;
    const unsigned long SPISRAM_CAPACITY_BYTE = 2 * 65536UL; // 1Mbit SRAM (bytes)

    SPISRAM();

    void init(void);
    inline uint8_t transfer(uint8_t dt);
    inline void hold(uint8_t state);
    void reset(void);
    inline void beginAccess(void);
    inline void endAccess(void);
    void setMode(void);
    void beginWrite(void);
    void beginRead(void);
    void disconnect(void);
    void connect(void);
    void fill(byte a);
    void clear(void);
    void dump(int count);
};

#endif
