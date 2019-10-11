import smbus #Enables the python bindings for I2C
import time #Enables sleep functions
bus = smbus.SMBus(1) #Opens /dev/i2c-1
address = 0x52        #The Nunchuck I2C address
bus.write_byte_data(address, 0x40, 0x00)
bus.write_byte_data(address, 0xF0, 0x55)
bus.write_byte_data(address, 0xFB, 0x00)
time.sleep(0.1)
while True:
    try:
        bus.write_byte(address, 0x00)
        time.sleep(0.1)
        data0 = bus.read_byte(address)
        data1 = bus.read_byte(address)
        data2 = bus.read_byte(address)
        data3 = bus.read_byte(address)
        data4 = bus.read_byte(address)
        data5 = bus.read_byte(address)
        data = [data0, data1, data2, data3, data4, data5]
        joy_x = data[0]
        joy_y = data[1]
        accel_x = (data[2]<<2) + ((data[5]&0x0c)>>2)
        accel_y = (data[3]<<2) + ((data[5]&0x30)>>4)
        accel_z = (data[4]<<2) + ((data[5]&0xc0)>>6)
        print("joyX: %s  joyY: %s  " % (joy_x, joy_y) + \
              "acX: %s  acY: %s  acZ: %s" % (accel_x, accel_y, accel_z))
    except IOError as e:
        print e
