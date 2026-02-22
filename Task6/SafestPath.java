package Task6;

import java.util.*;

class Edge {
    int to;
    double weight;   // represents risk / cost (-log probability)

    Edge(int to, double weight) {
        this.to = to;
        this.weight = weight;
    }
}

public class SafestPath {

    public static void dijkstra(List<List<Edge>> graph, int src) {

        int n = graph.size();
        double[] dist = new double[n];
        boolean[] visited = new boolean[n];

        Arrays.fill(dist, Double.MAX_VALUE);
        dist[src] = 0;

        PriorityQueue<Edge> pq =
                new PriorityQueue<>(Comparator.comparingDouble(e -> e.weight));
        pq.add(new Edge(src, 0));

        while (!pq.isEmpty()) {
            Edge current = pq.poll();
            int u = current.to;

            if (visited[u]) continue;
            visited[u] = true;

            for (Edge e : graph.get(u)) {
                int v = e.to;
                double newDist = dist[u] + e.weight;

                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    pq.add(new Edge(v, newDist));
                }
            }
        }

        System.out.println("Safest distances from source:");
        System.out.println(Arrays.toString(dist));
    }

    // 🔹 MAIN METHOD
    public static void main(String[] args) {

        int vertices = 5;
        List<List<Edge>> graph = new ArrayList<>();

        for (int i = 0; i < vertices; i++) {
            graph.add(new ArrayList<>());
        }

        // Sample graph (weights represent risk values)
        graph.get(0).add(new Edge(1, 2.5));
        graph.get(0).add(new Edge(2, 1.2));
        graph.get(1).add(new Edge(2, 1.8));
        graph.get(1).add(new Edge(3, 2.0));
        graph.get(2).add(new Edge(3, 1.0));
        graph.get(3).add(new Edge(4, 3.0));

        int source = 0;
        dijkstra(graph, source);
    }
}


// the folder path should be \Programming Assignment Folder\Codes
//to run
// javac Task6\SafestPath.java
// java Task6.SafestPath
