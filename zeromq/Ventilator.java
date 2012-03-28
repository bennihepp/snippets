import org.zeromq.ZMQ;
import com.google.gson.Gson;
import java.util.HashMap;

public class Ventilator extends Thread {

    public int NUM;

    public Ventilator(int NUM) {
        super();
        this.NUM = NUM;
    }

    public void run()  {

        Gson gson = new Gson();

        // Initialize a zeromq context
        ZMQ.Context context = ZMQ.context(1);

        // Set up a channel to send work
        ZMQ.Socket ventilator_send = context.socket(ZMQ.PUSH);
        ventilator_send.bind("tcp://127.0.0.1:5557");

        try {
            // Give everything a second to spin up and connect
            Thread.sleep(500);
        } catch(InterruptedException ex) {
        }

        // Send the numbers between 1 and ten thousand as work messages
        for (int i=0; i < this.NUM; ++i) {
            String num = "num";
            HashMap<String, Integer> work_message = new HashMap<String, Integer>();
            Integer obj = new Integer(i);
            work_message.put(num, obj);
            String msg = gson.toJson(work_message);
            ventilator_send.send(msg.getBytes(), 0);
        }

        try {
            // Give everything a second to spin up and connect
            Thread.sleep(500);
        } catch(InterruptedException ex) {
        }
    }
}
