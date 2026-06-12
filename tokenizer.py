from collections import Counter


class BPETokenizer:
    """BPE-based subword tokenizer trained on a key document."""

    def __init__(self, vocab_size=500):
        self.vocab_size = vocab_size
        self.merges = []           # ordered list of ((left, right), merged)
        self.vocab = set()         # all known tokens (strings)

    def train(self, text):
        """Learn BPE merges from the given text."""
        # Start with all unique characters
        chars = sorted(set(text))
        self.vocab = set(chars)

        # Split text into words (by whitespace) and count frequencies
        words = text.split()
        word_freqs = Counter(words)

        # Each word starts as a list of individual characters
        word_tokens = {word: list(word) for word in word_freqs}

        # Count initial adjacent pairs across all words
        pair_counts = Counter()
        for word, freq in word_freqs.items():
            tokens = word_tokens[word]
            for i in range(len(tokens) - 1):
                pair_counts[(tokens[i], tokens[i + 1])] += freq

        target_merges = self.vocab_size - len(chars)
        for _ in range(target_merges):
            if not pair_counts:
                break

            # Pick the most frequent pair
            (left, right), _ = pair_counts.most_common(1)[0]
            merged = left + right

            self.merges.append(((left, right), merged))
            self.vocab.add(merged)

            # Apply this merge to every word and re-count pairs
            new_pair_counts = Counter()
            for word, freq in word_freqs.items():
                tokens = word_tokens[word]
                new_tokens = []
                i = 0
                while i < len(tokens):
                    if i < len(tokens) - 1 and tokens[i] == left and tokens[i + 1] == right:
                        new_tokens.append(merged)
                        i += 2
                    else:
                        new_tokens.append(tokens[i])
                        i += 1
                word_tokens[word] = new_tokens

                for i in range(len(new_tokens) - 1):
                    new_pair_counts[(new_tokens[i], new_tokens[i + 1])] += freq

            pair_counts = new_pair_counts

    def tokenize(self, text):
        """Tokenize text using the learned BPE merges.

        Splits into words by whitespace and inserts explicit space tokens
        between them, so that spaces are preserved in the output.
        Returns a list of token strings.
        """
        words = text.split()
        result = []
        for i, word in enumerate(words):
            if i > 0:
                result.append(" ")  # explicit space token between words
            tokens = list(word)
            for (left, right), merged in self.merges:
                new_tokens = []
                j = 0
                while j < len(tokens):
                    if (
                        j < len(tokens) - 1
                        and tokens[j] == left
                        and tokens[j + 1] == right
                    ):
                        new_tokens.append(merged)
                        j += 2
                    else:
                        new_tokens.append(tokens[j])
                        j += 1
                tokens = new_tokens
            result.extend(tokens)
        return result
