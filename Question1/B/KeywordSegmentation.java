package Question1.B;
import java.util.*;

public class KeywordSegmentation {
  public static List<String> wordBreak(String s, List<String> wordDict) {
        return backtrack(s, wordDict, new HashMap<>());
    }

    private static List<String> backtrack(String s, List<String> dict, Map<String, List<String>> memo) {
        if (memo.containsKey(s)) return memo.get(s);

        List<String> result = new ArrayList<>();
        if (s.length() == 0) {
            result.add("");
            return result;
        }

        for (String word : dict) {
            if (s.startsWith(word)) {
                List<String> subList = backtrack(s.substring(word.length()), dict, memo);
                for (String sub : subList) {
                    result.add(word + (sub.isEmpty() ? "" : " " + sub));
                }
            }
        }

        memo.put(s, result);
        return result;
    }

    public static void main(String[] args) {
        String query = "nepaltrekkingguide";
        List<String> dict = Arrays.asList("nepal", "trekking", "guide", "nepaltrekking");

        System.out.println(wordBreak(query, dict));
    }
}

// the folder path should be \Programming Assignment Folder\Codes
//to run
// javac Question1\B\KeywordSegmentation.java
// java Question1.B.KeywordSegmentation