import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class IdealCompletion {

    public static class RunLengthCodec {

        public static class Token {
            public char character;
            public int count;

            public Token(char character, int count) {
                this.character = character;
                this.count = count;
            }

            @Override
            public String toString() {
                return "Token(" + "'" + character + "'" + ", " + count + ")";
            }

            @Override
            public boolean equals(Object obj) {
                if (this == obj) return true;
                if (obj == null || getClass() != obj.getClass()) return false;
                Token other = (Token) obj;
                return character == other.character && count == other.count;
            }

            @Override  
            public int hashCode() {
                return 31 * character + count;
            }
        }

        public static String encode(String input) {
            if (!canEncode(input)) {
                throw new IllegalArgumentException("Input string cannot be encoded.");
            }

            StringBuilder encoded = new StringBuilder();
            List<String> groups = groupByCharacters(input);

            for (String group : groups) {
                encoded.append(group.charAt(0)).append(group.length());
            }

            return encoded.toString();
        }

        public static String decode(String input) {
            if (!canDecode(input)) {
                throw new IllegalArgumentException("Input string cannot be decoded.");
            }

            List<Token> tokens = tokenize(input);
            StringBuilder decoded = new StringBuilder();

            for (Token token : tokens) {
                for (int i = 0; i < token.count; i++) {
                    decoded.append(token.character);
                }
            }

            return decoded.toString();
        }

        public static boolean canEncode(String input) {
            return input != null && input.matches("^[a-zA-Z]+$");
        }

        public static boolean canDecode(String input) {
            if (input == null || input.isEmpty()) {
                return false;
            }
            // Must match the pattern: sequences of letters optionally followed by digits
            if (!input.matches("^([a-zA-Z]+\\d*)+$")) {
                return false;
            }
            // Allow single-character strings even without count
            if (input.length() == 1 && Character.isLetter(input.charAt(0))) {
                return true;
            }
            // Ensure at least one character has a digit (i.e., is encoded)
            Pattern pattern = Pattern.compile("[a-zA-Z]+\\d+");
            Matcher matcher = pattern.matcher(input);
            return matcher.find();
        }

        public static List<String> groupByCharacters(String input) {
            List<String> groups = new ArrayList<>();
            if (input == null || input.isEmpty()) {
                return groups;
            }

            StringBuilder currentGroup = new StringBuilder();
            char[] chars = input.toCharArray();
            currentGroup.append(chars[0]);

            for (int i = 1; i < chars.length; i++) {
                if (chars[i] == chars[i - 1]) {
                    currentGroup.append(chars[i]);
                } else {
                    groups.add(currentGroup.toString());
                    currentGroup.setLength(0);
                    currentGroup.append(chars[i]);
                }
            }

            groups.add(currentGroup.toString());
            return groups;
        }

        public static List<Token> tokenize(String input) {
            List<Token> tokens = new ArrayList<>();
            if (input == null || input.isEmpty()) {
                return tokens;
            }

            Pattern pattern = Pattern.compile("([a-zA-Z]+)(\\d*)");
            Matcher matcher = pattern.matcher(input);

            while (matcher.find()) {
                String chars = matcher.group(1);
                String countStr = matcher.group(2);
                int count = countStr.isEmpty() ? 1 : Integer.parseInt(countStr);

                for (char character : chars.toCharArray()) {
                    tokens.add(new Token(character, count));
                }
            }

            return tokens;
        }
    }
}
