/*
 *
 *
 *
 *
 */

#include <util/atomic.h>
#include "iface_nrf24l01.h"
#include "crc8.h"

// Wiring
#define MOSI_pin  3  // MOSI - D3
#define SCK_pin   4  // SCK  - D4
#define CE_pin    5  // CE   - D5
#define MISO_pin  A0 // MISO - A0
#define CS_pin    A1 // CS   - A1

#define ledPin    13 // LED  - D13

// SPI outputs
#define MOSI_on PORTD |= _BV(3)  // PD3
#define MOSI_off PORTD &= ~_BV(3)// PD3
#define SCK_on PORTD |= _BV(4)   // PD4
#define SCK_off PORTD &= ~_BV(4) // PD4
#define CE_on PORTD |= _BV(5)    // PD5
#define CE_off PORTD &= ~_BV(5)  // PD5
#define CS_on PORTC |= _BV(1)    // PC1
#define CS_off PORTC &= ~_BV(1)  // PC1
// SPI input
#define  MISO_on (PINC & _BV(0)) // PC0

#define RF_POWER TX_POWER_80mW

// PPM stream settings
#define CHANNELS 12 // number of channels in ppm stream, 12 ideally
enum chan_order{
    THROTTLE,
    AILERON,
    ELEVATOR,
    RUDDER,
    AUX1,  // (CH5)  3 pos. rate on
    AUX2,  // (CH6)  flip control
    AUX3,  // (CH7)  still camera (snapshot)
    AUX4,  // (CH8)  video camera
    AUX5,  // (CH9)  headless
    AUX6,  // (CH10) calibrate Y (V2x2), pitch trim (H7), RTH (Bayang, H20), 360deg flip mode (H8-3D, H22)
    AUX7,  // (CH11) calibrate X (V2x2), roll trim (H7)
    AUX8,  // (CH12) Reset / Rebind
};

#define CMD_NONE              0
#define CMD_FLIP              1
#define CMD_SWITCH_TO_MODE_1  2
#define CMD_SWITCH_TO_MODE_2  3
#define CMD_SWITCH_TO_MODE_3  4
#define CMD_REBIND            5
#define CMD_RESET             6


#define PPM_MIN 1000
#define PPM_SAFE_THROTTLE 1050
#define PPM_MID 1500
#define PPM_MAX 2000
#define PPM_MIN_COMMAND 1300
#define PPM_MAX_COMMAND 1700
#define GET_FLAG(ch, mask) (ppm[ch] > PPM_MAX_COMMAND ? mask : 0)

// supported protocols
enum {
    PROTO_CX10_BLUE=0,
    PROTO_CX10_GREEN,
    PROTO_SYMAX5C1,
    PROTO_END
};

volatile uint8_t rcv_data[12];
volatile uint8_t rcv_complete = 0;
volatile uint8_t rcv_count = 0;
uint8_t transmitterID[4];
uint8_t current_protocol;
static volatile bool ppm_ok = false;
uint8_t packet[32];
static bool reset=true;
volatile uint16_t Servo_data[12];
static uint16_t ppm[12] = {PPM_MIN,PPM_MID,PPM_MID,PPM_MID,PPM_MID,PPM_MID,
                           PPM_MID,PPM_MID,PPM_MID,PPM_MID,PPM_MID,PPM_MID,};

void setup() {

    uint8_t init_proto;

    Serial.begin(57600);
    randomSeed((analogRead(A4) & 0x1F) | (analogRead(A5) << 5));
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); //start LED off
    pinMode(MOSI_pin, OUTPUT);
    pinMode(SCK_pin, OUTPUT);
    pinMode(CS_pin, OUTPUT);
    pinMode(CE_pin, OUTPUT);
    pinMode(MISO_pin, INPUT);
    NRF24L01_Reset();
    NRF24L01_Initialize();

    while (!Serial.available()){ }
    init_proto = Serial.read();
    switch (init_proto){
      case 1:
        current_protocol = PROTO_CX10_BLUE;
        CX10_init();
        CX10_bind();
        delay(4000);
        break;
      case 2:
        current_protocol = PROTO_SYMAX5C1;
        Symax_init();
        SymaX_bind();
        delay(2000);
        break;
    }

    Serial.print(5);
}

void loop(){
    uint32_t timeout;
    uint16_t aux2 = 1000;

    switch (current_protocol){
      case PROTO_CX10_BLUE:
        timeout = process_CX10();
        break;
      case PROTO_SYMAX5C1:
        timeout = process_SymaX();
        break;
    }

    if (Serial.available()>0){
      while (Serial.available()>0){
        if (rcv_count <= 8){
          rcv_data[rcv_count] = Serial.read();
          rcv_count++;
        }
        else {
          // Serial data order (8bit data): [t][t][a][a][e][e][r][r][cmd])
          ppm[THROTTLE] = ( (uint16_t) rcv_data[1] << 8) | rcv_data[0];
          ppm[AILERON]  = ( (uint16_t) rcv_data[3] << 8) | rcv_data[2];
          ppm[ELEVATOR] = ( (uint16_t) rcv_data[5] << 8) | rcv_data[4];
          ppm[RUDDER]   = ( (uint16_t) rcv_data[7] << 8) | rcv_data[6];
          //ppm[AUX2]     = ( (uint16_t) rcv_data[9] << 8) | rcv_data[8];
          aux2 = 1000;
          switch (rcv_data[8]){
            case CMD_FLIP:
              aux2 = 2000;
              break;
            case CMD_SWITCH_TO_MODE_1:
              ppm[AUX1] = 1000;
              break;
            case CMD_SWITCH_TO_MODE_2:
              ppm[AUX1] = 1500;
              break;
            case CMD_SWITCH_TO_MODE_3:
              ppm[AUX1] = 2000;
              break;
          }
          ppm[AUX2] = aux2;
          rcv_count = 0;
        }
      }
    }

    while(micros() < timeout)
    {   };

}
