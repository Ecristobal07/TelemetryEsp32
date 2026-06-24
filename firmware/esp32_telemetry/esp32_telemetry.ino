#include "DHT.h"
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

// ---------- Pin Definitions ----------
#define DHTPIN 4
#define DHTTYPE DHT22

#define LIGHT_SENSOR_PIN 36
#define LED_PIN 23

// ---------- Thresholds ----------
#define LIGHT_THRESHOLD 800
#define TEMP_WARNING 30.0
#define ACCEL_WARNING 15.0   // m/s^2, adjust later

// ---------- Sensor Objects ----------
DHT dht(DHTPIN, DHTTYPE);
Adafruit_MPU6050 mpu;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Start DHT22
  dht.begin();

  // Start analog reading for light sensor
  analogSetAttenuation(ADC_11db);

  // LED setup
  pinMode(LED_PIN, OUTPUT);

  // Start I2C for MPU6050
  Wire.begin(21, 22); // SDA = GPIO21, SCL = GPIO22

  if (!mpu.begin()) {
    Serial.println("MPU6050_ERROR: Failed to find MPU6050 chip");
    while (1) {
      delay(10);
    }
  }

  // Optional MPU settings
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  Serial.println("Satellite Telemetry System");
  Serial.println("time_ms,temp_c,humidity_percent,light_raw,light_status,accel_x,accel_y,accel_z,gyro_x,gyro_y,gyro_z,system_status");
}

void loop() {
  // ---------- Read DHT22 ----------
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // ---------- Read photoresistor ----------
  int lightValue = analogRead(LIGHT_SENSOR_PIN);

  // ---------- Read MPU6050 ----------
  sensors_event_t accel;
  sensors_event_t gyro;
  sensors_event_t temp;
  mpu.getEvent(&accel, &gyro, &temp);

  float ax = accel.acceleration.x;
  float ay = accel.acceleration.y;
  float az = accel.acceleration.z;

  float gx = gyro.gyro.x;
  float gy = gyro.gyro.y;
  float gz = gyro.gyro.z;

  // ---------- Light status ----------
  String lightStatus;

  if (lightValue < 40) {
    lightStatus = "Dark";
  } else if (lightValue < 800) {
    lightStatus = "Dim";
  } else if (lightValue < 2000) {
    lightStatus = "Light";
  } else if (lightValue < 3200) {
    lightStatus = "Bright";
  } else {
    lightStatus = "Very bright";
  }

  // ---------- LED control ----------
  if (lightValue > LIGHT_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  // ---------- System status ----------
  String systemStatus = "NOMINAL";

  if (isnan(temperature) || isnan(humidity)) {
    systemStatus = "DHT_ERROR";
  } 
  else if (temperature > TEMP_WARNING) {
    systemStatus = "THERMAL_WARNING";
  } 
  else if (lightValue < LIGHT_THRESHOLD) {
    systemStatus = "LOW_LIGHT";
  } 
  else if (abs(ax) > ACCEL_WARNING || abs(ay) > ACCEL_WARNING || abs(az) > ACCEL_WARNING) {
    systemStatus = "MOTION_WARNING";
  }

  // ---------- Print telemetry packet ----------
  Serial.print(millis());
  Serial.print(",");

  if (isnan(temperature)) Serial.print("NaN");
  else Serial.print(temperature);

  Serial.print(",");

  if (isnan(humidity)) Serial.print("NaN");
  else Serial.print(humidity);

  Serial.print(",");
  Serial.print(lightValue);
  Serial.print(",");
  Serial.print(lightStatus);
  Serial.print(",");

  Serial.print(ax);
  Serial.print(",");
  Serial.print(ay);
  Serial.print(",");
  Serial.print(az);
  Serial.print(",");

  Serial.print(gx);
  Serial.print(",");
  Serial.print(gy);
  Serial.print(",");
  Serial.print(gz);
  Serial.print(",");

  Serial.println(systemStatus);

  delay(1000);
}
