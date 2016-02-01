/*
 */

#include <util/atomic.h>
#include "iface_nrf24l01.h"
#include "crc8.h"

// ############ Wiring ################
#define PPM_pin   2  // PPM in
//SPI Comm.pins with nRF24L01
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
    AUX1,  // (CH5)  led light, or 3 pos. rate on CX-10, H7, or inverted flight on H101
    AUX2,  // (CH6)  flip control
    AUX3,  // (CH7)  still camera (snapshot)
    AUX4,  // (CH8)  video camera
    AUX5,  // (CH9)  headless
    AUX6,  // (CH10) calibrate Y (V2x2), pitch trim (H7), RTH (Bayang, H20), 360deg flip mode (H8-3D, H22)
    AUX7,  // (CH11) calibrate X (V2x2), roll trim (H7)
    AUX8,  // (CH12) Reset / Rebind
};

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
    PROTO_END
};

volatile uint8_t rcv_data[9];
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
    Serial.begin(57600);
    randomSeed((analogRead(A4) & 0x1F) | (analogRead(A5) << 5));
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW); //start LED off
    pinMode(MOSI_pin, OUTPUT);
    pinMode(SCK_pin, OUTPUT);
    pinMode(CS_pin, OUTPUT);
    pinMode(CE_pin, OUTPUT);
    pinMode(MISO_pin, INPUT);

    current_protocol = PROTO_CX10_BLUE;
    NRF24L01_Reset();
    NRF24L01_Initialize();
    CX10_init();
    CX10_bind();
    delay(4000);
    Serial.print(5);
}

void loop(){
    uint32_t timeout;
    if (rcv_complete == 1){
      process_serial_data();
      rcv_complete=0;
    }
    timeout = process_CX10();
    while(micros() < timeout)
    {   };

}



void serialEvent() {
  if (rcv_count <= 8){
    rcv_data[rcv_count] = Serial.read();
    rcv_count++;
  }
  else {
    rcv_complete = 1;
    rcv_count = 0;
  }
}


void process_serial_data(){

  /*uint8_t data[8] = {
    rcv_data[0],
    rcv_data[1],
    rcv_data[2],
    rcv_data[3],
    rcv_data[4],
    rcv_data[5],
    rcv_data[6],
    rcv_data[7]
  };
  uint8_t crc = CRC8(data,8);
  if (crc == rcv_data[8]){
    //ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {
*/
      ppm[THROTTLE] = ( (uint16_t) rcv_data[1] << 8) | rcv_data[0];
      ppm[AILERON] = ( (uint16_t) rcv_data[3] << 8) | rcv_data[2];
      ppm[ELEVATOR] = ( (uint16_t) rcv_data[5] << 8) | rcv_data[4];
      ppm[RUDDER] = ( (uint16_t) rcv_data[7] << 8) | rcv_data[6];
    //}
  //}
}
