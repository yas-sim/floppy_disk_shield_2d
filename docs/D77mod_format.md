# D77mod Disk Image Format Specifications

**Header (0x2b0 bytes)**
|offset|size|Contents|
|:----:|:----:|:----|
|0x0000|17|image name (ASCIIZ)|
|0x0011|1|<span style="color: blue; ">(mod)**raw track data support flag (0x00=not support, 0x10=supported)**</span>|
|0x0012|8|reserve (0x00)|
|0x001a|1|write protect flag (0x00: no protect, 0x10: write protected)|
|0x001b|1|disk type (0x00: 2D, 0x10: 2DD, 0x20: 2HD)|
|0x001c|4|total disk image size|
|0x0020|4 * 164 (0x290)|sector data table (0-163 track)|
|0x02b0|4 * 164 (0x290)|<span style="color: blue; ">(mod)**track data table (0-163 track) 0=No track data or dirty track**</span>|
  
<br>

<span style="color: blue; ">**(mod)Track data (+0x540 (=0x20+0x290+0x290))**</span>  
|offset|size|contents|
|:----:|:----:|:----|
|0x0000|4|<span style="color: blue; ">(mod)**track data size**</span>|
|0x0004|variable|<span style="color: blue; ">(mod)**track data**</span>|

<br>
  
**Sector data** (+0x2b0 when without track data, +??? with track data)  
|offset|size|contents|
|:----:|:----:|:----|
|0x0000|1|C|
|0x0001|1|H|
|0x0002|1|R|
|0x0003|1|N|
|0x0004|2|# of sectors in this track|
|0x0006|1|density (0x00: double density, 0x40: single density)|
|0x0007|1|Deleted data (0x00: normal, 0x10: deleted data)XM7: 0x10 => RECORD_TYPE_ERR|
|0x0008|1|status (0x00: normal end, others: disk BIOS status) XM7: 0xb0 => Data CRC_ERR|
|0x0009|2|<span style="color: blue; ">(mod)**sector position (MFM byte)**</span>|
|0x000b|1|<span style="color: blue; ">(mod)**Status extension. 0x01 = ID_CRC error**</span>|
|0x000c|2|<span style="color: blue; ">(mod)**ID_CRC values**</span>|
|0x000e|2|sector size|
|0x0010|variable|sector data|
