#ifndef _SPI_SRAM_
#define _SPI_SRAM_

#define MACRO_ENABLE_SPI_HOLD()    PORTC &= 0b11101111;
#define MACRO_DISABLE_SPI_HOLD()   PORTC |= 0b00010000;

#define SPI_MEMORY_23LC1024   (0)
#define SPI_MEMORY_CY15B104Q  (1)
#define SPI_MEMORY_TYPE SPI_MEMORY_CY15B104Q
//#define SPI_MEMORY_TYPE SPI_MEMORY_23LC1024

class SPIMEMORY {
  public:
    const uint32_t SPI_CLK = 4e6;
#if SPI_MEMORY_TYPE == SPI_MEMORY_CY15B104Q
    const uint32_t SPIMEMORY_CAPACITY_BYTE = (1024UL * 1024UL * 4UL)/8; // 4Mbit FRAM (bytes)
#elif SPI_MEMORY_TYPE == SPI_MEMORY_23LC1024
    const uint32_t SPIMEMORY_CAPACITY_BYTE = (1024UL * 1024UL * 1UL)/8; // 1Mbit SRAM (bytes)
#endif
    uint8_t curr_bit_ptn;
    uint8_t curr_byte;
    uint8_t default_val;   // default value for the curr_byte
    uint32_t write_count;  // byte unit
    SPIMEMORY();

    void init(void);
    void setDefaultValue(uint8_t val);
    inline uint8_t transfer(uint8_t dt);
    void writeBit(uint8_t dt);
    void flush(void);
    inline uint32_t getLength( void ) { return write_count; }
    inline void hold(uint8_t state);
    void reset(void);
    inline void beginAccess(void);
    inline void endAccess(void);
    void setSramWriteMode(void);
    void beginWrite(void);
    void beginRead(void);
    void disconnect(void);
    void connect(void);
    void fill(uint8_t a);
    void clear(void);
    void dump(int count);

    void framWriteEnable(void);

};

#endif
