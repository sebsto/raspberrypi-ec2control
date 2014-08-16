import threading, time
import boto.ec2

class EC2StatusMonitoring():

    def __init__(self, region, instanceID):

        self._thread     = None
        self._instanceID = None
        self._region     = None
        self._lastStatus = None

        self._isMonitoring = False
        self._listeners = []

        self._waittime = 1

        self._instanceID = instanceID
        self._region     = region

    def _monitor(self):
        while self._isMonitoring :
            status = self.getInstanceStatus()
            for l in self._listeners:
                l(self, status)
            time.sleep(self._waittime)


    def instance_id(self):
        return self._instanceID

    def startMonitoring(self):
        self._isMonitoring = True
        self._thread = threading.Thread(target=self._monitor)
        self._thread.start()

    def stopMonitoring(self):
        self._isMonitoring = False

    def addMonitoringListener(self, listener):
        self._listeners.append(listener)

    def removeMonitoringListener(self, listener):
        self._listeners.remove(listener)

    def startInstance(self):
        conn = boto.ec2.connect_to_region(self._region)
        instances = conn.get_only_instances(instance_ids = [ self._instanceID ])
        if len(instances) == 0:
            print "EC2Monitoring can not find instance %s" % self._instanceID
        else:
            conn.start_instances(instance_ids = [ self._instanceID ])

    def stopInstance(self):
        conn = boto.ec2.connect_to_region(self._region)
        instances = conn.get_only_instances(instance_ids = [ self._instanceID ])
        if len(instances) == 0:
            print "EC2Monitoring can not find instance %s" % self._instanceID
        else:
            conn.stop_instances(instance_ids = [ self._instanceID ])

    def getInstanceStatus(self):
        result = None

        conn = boto.ec2.connect_to_region(self._region)
        instances = conn.get_only_instances(instance_ids = [ self._instanceID ])

        if len(instances) == 0:
            print "EC2Monitoring can not find instance %s" % self._instanceID
        else:
            i = instances[0]
            self._lastStatus = result = i.state_code

        return result

    def lastStatus(self):
        return self._lastStatus