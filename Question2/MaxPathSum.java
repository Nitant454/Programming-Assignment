package Question2;

class TreeNode {
    int val;
    TreeNode left, right;

    TreeNode(int val) {
        this.val = val;
    }
}

public class MaxPathSum {

    static int maxSum = Integer.MIN_VALUE;

    public static int maxPath(TreeNode root) {
        calculate(root);
        return maxSum;
    }

    private static int calculate(TreeNode node) {
        if (node == null) return 0;

        int left = Math.max(0, calculate(node.left));
        int right = Math.max(0, calculate(node.right));

        maxSum = Math.max(maxSum, left + node.val + right);

        return node.val + Math.max(left, right);
    }

    public static void main(String[] args) {
        TreeNode root = new TreeNode(-10);
        root.left = new TreeNode(9);
        root.right = new TreeNode(20);
        root.right.left = new TreeNode(15);
        root.right.right = new TreeNode(7);

        System.out.println(maxPath(root));
    }
}

// the folder path should be \Programming Assignment Folder\Codes
//to run
// javac Question2\MaxPathSum.java
// java Question2.MaxPathSum

