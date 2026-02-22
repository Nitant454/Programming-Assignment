public class CommodityTrading {

    public static int maxProfit(int k, int[] prices) {
        if (prices.length == 0) return 0;

        int[] buy = new int[k + 1];
        int[] sell = new int[k + 1];

        for (int i = 0; i <= k; i++)
            buy[i] = Integer.MIN_VALUE;

        for (int price : prices) {
            for (int i = 1; i <= k; i++) {
                buy[i] = Math.max(buy[i], sell[i - 1] - price);
                sell[i] = Math.max(sell[i], buy[i] + price);
            }
        }
        return sell[k];
    }

    public static void main(String[] args) {
        int[] prices = {2000, 4000, 1000};
        int maxTrades = 2;
        System.out.println(maxProfit(maxTrades, prices));
    }
}
