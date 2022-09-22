#ifndef _SPI_SRAM_
#define _SPI_SRAM_

class SPISRAM {
  public:
    const uint32_t SPI_CLK = 4e6;
    const uint32_t SPISRAM_CAPACITY_BYTE = 2 * 65536UL; // 1Mbit SRAM (bytes)
    uint32_t curr_bit_pos;
    uint8_t curr_byte;
    uint8_t default_val;   // default value for the curr_byte
    SPISRAM();

    void init(void);
    void setDefaultValue(uint8_t val);
    inline uint8_t transfer(uint8_t dt);
    void writeBit(uint8_t dt);
    void flush(void);
    inline uint32_t getLength( void ) { return curr_bit_pos; }
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
