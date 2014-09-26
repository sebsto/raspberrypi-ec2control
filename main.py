import os
import RPi.GPIO as GPIO

from led import Led
from ir  import IREventListener
from ec2 import EC2StatusMonitoring

class Main:


    GPIO.setmode(GPIO.BOARD) # Use board pin numbering
    GPIO.setwarnings(False)  # don't tell us "the Channel is already in use"

    # GPIO PIN assignments
    BOARD = { 0:11, 1:12, 2:14, 3:15, 4:16, 5:18, 6:22, 7:7 }

    STATUS_PENDING     = 0x0000
    STATUS_RUNNING     = 0x0010
    STATUS_SHUTINGDOWN = 0x0020
    STATUS_TERMINATED  = 0x0030
    STATUS_STOPPING    = 0x0040
    STATUS_STOPPED     = 0x0050

    def handleIR_OKbutton(self, irlistener):
        print "received OK"
        irlistener.stopListening()
        self.led_green.off()
        self.led_red.off()
        os._exit(0)

    def handleIR_PlayPausebutton(self, irlistener):
        print "Play / Pause"

        if self.ec2monitor.lastStatus() == Main.STATUS_RUNNING:
            print "Stopping"
            self.ec2monitor.stopInstance()

        if self.ec2monitor.lastStatus() == Main.STATUS_STOPPED:
            print "Starting"
            self.ec2monitor.startInstance()

    def ec2listener(self, ec2monitor, status):
        if status == None:
            self.led_green.off()
            self.led_red.off()
            return

        print "Status : %s" % format(status, '02x')

        if status == Main.STATUS_RUNNING:
            print "Running"
            self.led_red.off()
            self.led_green.on()
        elif status == Main.STATUS_PENDING:
            print "Pending"
            self.led_red.off()
            self.led_green.start_blinking(0.5)
        elif status == Main.STATUS_TERMINATED:
            print "Terminated"
            self.led_red.off()
            self.led_green.off()
        elif status == Main.STATUS_STOPPED:
            print "Stopped"
            self.led_red.on()
            self.led_green.off()
        elif status == Main.STATUS_SHUTINGDOWN or status == Main.STATUS_STOPPING:
            print "Shutting down or stopping"
            self.led_green.off()
            self.led_red.start_blinking(0.5)

    def main(self):
        print 'Starting ...'

        self.irlistener = None
        self.ec2monitor = None

        #self.led_blue = Led(Main.BOARD[7])
        self.led_green = Led(Main.BOARD[6])
        self.led_red   = Led(Main.BOARD[5])

        print "Start listening IR"
        self.irlistener = IREventListener('pylirc', './ec2control/config/lircrc')
        self.irlistener.addListener(u'ok', self.handleIR_OKbutton)
        self.irlistener.addListener(u'playpause', self.handleIR_PlayPausebutton)
        self.irlistener.startListening()

        print "Start Monitoring EC2 instance"
        self.ec2monitor = EC2StatusMonitoring('eu-west-1', 'i-8687eac5')
        self.ec2monitor.addMonitoringListener(self.ec2listener)
        self.ec2monitor.startMonitoring()


if (__name__ == "__main__"):
    Main().main()