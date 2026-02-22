package Question4.b;

class WeatherThread extends Thread {
    String city;

    WeatherThread(String city) {
        this.city = city;
    }

    public void run() {
        try {
            Thread.sleep(1000);
            System.out.println("Fetched weather for " + city);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

public class WeatherApp {

    public static void main(String[] args) {

        String[] cities = {
            "Kathmandu", "Pokhara", "Biratnagar",
            "Nepalgunj", "Dhangadhi"
        };

        long start = System.currentTimeMillis();

        Thread[] threads = new Thread[cities.length];
        for (int i = 0; i < cities.length; i++) {
            threads[i] = new WeatherThread(cities[i]);
            threads[i].start();
        }

        for (Thread t : threads) {
            try {
                t.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        long end = System.currentTimeMillis();
        System.out.println("Multithreaded Time: " + (end - start) + " ms");
    }
}

// the folder path should be \Programming Assignment Folder\Codes
//to run
// javac Question4\b\WeatherApp.java
// java Question4.b.WeatherApp