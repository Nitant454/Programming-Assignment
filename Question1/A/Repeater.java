package Question1.A;
import java.util.HashMap;

public class Repeater {
    public static int maxPoints(int[][] p) {
        int max = 0;

        for (int i = 0; i < p.length; i++) {
            HashMap<Double, Integer> map = new HashMap<>();
            for (int j = i + 1; j < p.length; j++) {
                double slope = (p[i][0] == p[j][0]) ?
                        Double.POSITIVE_INFINITY :
                        (double)(p[j][1] - p[i][1]) / (p[j][0] - p[i][0]);

                map.put(slope, map.getOrDefault(slope, 1) + 1);
                max = Math.max(max, map.get(slope));
            }
        }
        return max;
    }
 // 🔹 MAIN METHOD (required to run)
    public static void main(String[] args) {
        int[][] customers = {{1,1}, {2,2}, {3,3}};
        System.out.println("Maximum customers covered: " + maxPoints(customers));
    }
}


//to run
// javac Question1/A/Repeater.java
// java Question1.A.Repeater