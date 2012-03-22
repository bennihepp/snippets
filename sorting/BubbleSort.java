import java.io.*;

public class BubbleSort { 
    public static void sort(int[] x) {
         for (int i=0; i < x.length - 1; ++i) {
             for (int j=0; j < x.length - i - 1; ++j) {
                 if (x[j] > x[i + 1]) {
                     int tmp = x[j];
                     x[j] = x[j + 1];
                     x[j + 1] = tmp;
                 }
             }
         }
    }
    
    public static void main(String[] args) throws FileNotFoundException, IOException {
        DataInputStream in = new DataInputStream(
            new BufferedInputStream(
                new FileInputStream(args[0])
            )
        );
        int size = in.readInt();
        int[] array = new int[size];
        for (int i=0; i < size; ++i) {
            array[i] = in.readInt();
        }

        //int[] array2 = new int[array.length];
        System.out.println("Sorting " + size + " data points...");
        //for (int i=0; i < 5; ++i) {
        //    System.arraycopy(array, 0, array2, 0, array.length);
        //    sort(array2);
            sort(array);
        //}
        //for (int i=0; i < array.length; i++) 
        //    System.out.println(array[i]);    
        //} 
    }
}

