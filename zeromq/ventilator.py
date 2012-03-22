import time
import zmq
from  multiprocessing import Process

NUM = 100000
NUM_OF_PROCS = 100

def ventilator():
    # Initialize a zeromq context
    context = zmq.Context()

    # Set up a channel to send work
    ventilator_send = context.socket(zmq.PUSH)
    ventilator_send.bind("tcp://127.0.0.1:5557")

    # Give everything a second to spin up and connect
    time.sleep(1)

    # Send the numbers between 1 and ten thousand as work messages
    for num in xrange(NUM):
        work_message = { 'num' : num }
        ventilator_send.send_json(work_message)

    time.sleep(1)

def worker(wrk_num):
    # Initialize a zeromq context
    context = zmq.Context()

    print('{}> Trying to connect...'.format(wrk_num))

    # Set up a channel to receive work from the ventilator
    work_receiver = context.socket(zmq.PULL)
    work_receiver.connect("tcp://127.0.0.1:5557")

    # Set up a channel to send result of work to the results reporter
    results_sender = context.socket(zmq.PUSH)
    results_sender.connect("tcp://127.0.0.1:5558")

    # Set up a channel to receive control messages over
    control_receiver = context.socket(zmq.SUB)
    control_receiver.connect("tcp://127.0.0.1:5559")
    control_receiver.setsockopt(zmq.SUBSCRIBE, "")

    # Set up a poller to multiplex the work receiver and control receiver channels
    poller = zmq.Poller()
    poller.register(work_receiver, zmq.POLLIN)
    poller.register(control_receiver, zmq.POLLIN)

    # Loop and accept messages from both channels, acting accordingly
    while True:
        socks = dict(poller.poll())

        # If the message came from work_receiver channel, square the number
        # and send the answer to the results reporter
        if socks.get(work_receiver) == zmq.POLLIN:
            work_message = work_receiver.recv_json()
            product = work_message['num'] * work_message['num']
            answer_message = {'worker': wrk_num,
                              'result': product,
                              'input': work_message['num']}
            results_sender.send_json(answer_message)

        # If the message came over the control channel, shut down the worker.
        if socks.get(control_receiver) == zmq.POLLIN:
            control_message = control_receiver.recv_json()
            if control_message == "FINISHED":
                print("{}> Received FINSHED, quitting!".format(wrk_num))
                break

def result_manager():
    # Initialize a zeromq context
    context = zmq.Context()

    # Set up a channel to receive results
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://127.0.0.1:5558")

    # Set up a channel to send control commands
    control_sender = context.socket(zmq.PUB)
    control_sender.bind("tcp://127.0.0.1:5559")

    for task_nbr in xrange(NUM):
        result_message = results_receiver.recv_json()
        #print "Worker %i answered: %i" % (result_message['worker'], result_message['result'])
        assert result_message['result'] == result_message['input'] * result_message['input']

        # Signal to all workers that we are finsihed
    control_sender.send_json("FINISHED")
    time.sleep(1)

if __name__ == "__main__":

    # Create a pool of workers to distribute work to
    worker_pool = range(NUM_OF_PROCS)
    workers = []
    for wrk_num in range(len(worker_pool)):
        w = Process(target=worker, args=(wrk_num,))
        w.start()
        workers.append(w)

    # Fire up our result manager...
    result_manager = Process(target=result_manager, args=())
    result_manager.start()

    # Start the ventilator!
    ventilator = Process(target=ventilator, args=())
    ventilator.start()

    print 'joining...'

    for worker in workers:
        worker.join()
    result_manager.join()
    ventilator.join()

    print 'done'

