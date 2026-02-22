package Question4;

import java.util.*;

class EnergySource {
    String name;
    int capacity;
    double cost;

    EnergySource(String name, int capacity, double cost) {
        this.name = name;
        this.capacity = capacity;
        this.cost = cost;
    }
}

public class SmartGrid {
    public static void main(String[] args) {

        int[] demand = {20, 15, 25}; // District A, B, C

        List<EnergySource> sources = new ArrayList<>();
        sources.add(new EnergySource("Solar", 50, 1.0));
        sources.add(new EnergySource("Hydro", 40, 1.5));

        sources.sort(Comparator.comparingDouble(s -> s.cost));

        int remaining = Arrays.stream(demand).sum();
        double totalCost = 0;

        for (EnergySource s : sources) {
            int used = Math.min(s.capacity, remaining);
            remaining -= used;
            totalCost += used * s.cost;
            System.out.println(s.name + " used: " + used + " kWh");
        }

        System.out.println("Total Cost: Rs. " + totalCost);
    }
}

// the folder path should be \Programming Assignment Folder\Codes
//to run
// javac Question4\SmartGrid.java
// java Question4.SmartGrid
