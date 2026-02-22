package Question4.a;

import java.util.*;

class TouristSpot {
    String name;
    int fee;
    String tag;

    TouristSpot(String name, int fee, String tag) {
        this.name = name;
        this.fee = fee;
        this.tag = tag;
    }
}

public class TouristOptimizer {

    public static void main(String[] args) {

        int budget = 500;
        String interest = "Culture";

        List<TouristSpot> spots = new ArrayList<>();
        spots.add(new TouristSpot("Pashupatinath", 100, "Culture"));
        spots.add(new TouristSpot("Swayambhunath", 200, "Culture"));
        spots.add(new TouristSpot("Garden of Dreams", 150, "Nature"));

        spots.sort(Comparator.comparingInt(s -> s.fee));

        int totalCost = 0;
        System.out.println("Selected Tourist Spots:");

        for (TouristSpot s : spots) {
            if (s.tag.equals(interest) && totalCost + s.fee <= budget) {
                totalCost += s.fee;
                System.out.println("- " + s.name);
            }
        }

        System.out.println("Total Cost: Rs. " + totalCost);
    }
}

// the folder path should be \Programming Assignment Folder\Codes
//to run
// javac Question4\a\TouristOptimizer.java
// java Question4.a.TouristOptimizer