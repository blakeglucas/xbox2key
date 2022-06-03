import time
import usb
import usb.backend.libusb1

if __name__ == '__main__':
    for dev in usb.core.find(find_all=True):
        print(dev)
    # controller = usb.core.find(idVendor=0x045e, idProduct=0x0b00)
    # # Only one config
    # controller.set_configuration()
    # print(controller)
    # usb.util.claim_interface(controller, 0)
    # while True:
    #     try:
    #         time.sleep(0.1)
    #     except KeyboardInterrupt:
    #         break
    # controller_handle.reset()