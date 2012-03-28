import time
from org.zeromq import ZMQ
from com.google.gson import Gson
from java.util import HashMap
from java.lang import Thread
import Ventilator

NUM = 1000
NUM_OF_PROCS = 20

#class Ventilator(Thread):

    #def run(self):
        #gson = Gson()

        ## Initialize a zeromq context
        #context = ZMQ.context(1)

        ## Set up a channel to send work
        #ventilator_send = context.socket(ZMQ.PUSH)
        #ventilator_send.bind("tcp://127.0.0.1:5557")

        ## Give everything a second to spin up and connect
        #time.sleep(1)

        ## Send the numbers between 1 and ten thousand as work messages
        #for num in xrange(NUM):
            #work_message = HashMap()
            #work_message['num'] = num
            #msg = gson.toJson(work_message)
            #ventilator_send.send(msg, 0)

        #time.sleep(1)

class Worker(Thread):

    def __init__(self, wrk_num):
        self.wrk_num = wrk_num
        Thread.__init__(self)

    def run(self):
        gson = Gson()

        # Initialize a zeromq context
        context = ZMQ.context(1)

        #print('{}> Trying to connect...'.format(wrk_num))

        # Set up a channel to receive work from the ventilator
        work_receiver = context.socket(ZMQ.PULL)
        work_receiver.connect("tcp://127.0.0.1:5557")

        # Set up a channel to send result of work to the results reporter
        results_sender = context.socket(ZMQ.PUSH)
        results_sender.connect("tcp://127.0.0.1:5558")

        # Set up a channel to receive control messages over
        control_receiver = context.socket(ZMQ.SUB)
        control_receiver.connect("tcp://127.0.0.1:5559")
        control_receiver.subscribe("")

        # Set up a poller to multiplex the work receiver and control receiver channels
        poller = context.poller(2)
        poller.register(work_receiver, ZMQ.Poller.POLLIN)
        poller.register(control_receiver, ZMQ.Poller.POLLIN)

        # Loop and accept messages from both channels, acting accordingly
        while True:
            poller.poll()

            # If the message came from work_receiver channel, square the number
            # and send the answer to the results reporter
            #if socks.get(work_receiver) == zmq.POLLIN:
            if poller.pollin(0):
                msg = work_receiver.recv(0)
                msg = msg.tostring()
                work_message = gson.fromJson(msg, HashMap)
                num = work_message.get('num')
                product = num * num
                answer_message = HashMap()
                answer_message.put('worker', self.wrk_num)
                answer_message.put('result', product)
                answer_message.put('input', num)
                msg = gson.toJson(answer_message)
                results_sender.send(msg, 0)

            # If the message came over the control channel, shut down the worker.
            #if socks.get(control_receiver) == zmq.POLLIN:
            if poller.pollin(1):
                msg = control_receiver.recv(0)
                control_message = msg.tostring()
                if control_message == "FINISHED":
                    #print("{}> Received FINSHED, quitting!".format(wrk_num))
                    break

class ResultManager(Thread):

    def run(self):
        gson = Gson()

        # Initialize a zeromq context
        context = ZMQ.context(1)

        # Set up a channel to receive results
        results_receiver = context.socket(ZMQ.PULL)
        results_receiver.bind("tcp://127.0.0.1:5558")

        # Set up a channel to send control commands
        control_sender = context.socket(ZMQ.PUB)
        control_sender.bind("tcp://127.0.0.1:5559")

        for task_nbr in xrange(NUM):
            msg = results_receiver.recv(0)
            msg = msg.tostring()
            result_message = gson.fromJson(msg, HashMap)
            #print "Worker %i answered: %i" % (result_message['worker'], result_message['result'])
            assert result_message['result'] == result_message['input'] * result_message['input']

            # Signal to all workers that we are finsihed
        control_sender.send("FINISHED", 0)
        time.sleep(1)

if __name__ == "__main__":

    # Create a pool of workers to distribute work to
    worker_pool = range(NUM_OF_PROCS)
    workers = []
    for wrk_num in range(len(worker_pool)):
        w = Worker(wrk_num)
        w.start()
        workers.append(w)

    # Fire up our result manager...
    result_manager = ResultManager()
    result_manager.start()

    # Start the ventilator!
    ventilator = Ventilator(NUM)
    ventilator.start()

    print 'joining...'

    for worker in workers:
        worker.join()
    result_manager.join()
    ventilator.join()

    print 'done'
