import random

class MarkovChain:

    def __init__(self, n=2):
        self.n = n
        self.memory = {}

    def _learn_key(self, key, value):
        if key not in self.memory:
            self.memory[key] = []

        self.memory[key].append(value)

    def learn(self, text):
        tokens = [token.strip('()') for token in text.split(" ")]
        if self.n==2:
            ngrams = [(tokens[i], tokens[i+1]) for i in range(0, len(tokens) - 1)]
        else:
            # n==3
            ngrams = [(tokens[i], tokens[i+1], tokens[i+2]) for i in range(0, len(tokens) - 2)]
        for ngram in ngrams:
            if self.n==2:
                self._learn_key(ngram[0], ngram[1])
            else:
                self._learn_key((ngram[0], ngram[1]), ngram[2])

    def _next(self, current_state):
        next_possible = self.memory.get(current_state)

        if not next_possible:
            if self.n==2:
                next_possible = self.memory.keys()
            else:
                next_possible = [key[0] for key in self.memory.keys()]

        return random.sample(next_possible, 1)[0]

    def babble(self, amount, state=''):
        if not amount:
            return state

        next_word = self._next(state)
        return state + ' ' + self.babble(amount - 1, next_word)

txt_file = open('data/cleaned.txt')
txt = txt_file.read().replace('\n', ' ')

markov = MarkovChain(2)
markov.learn(txt)

def compose_tweet(model, prompt):
    tweet = model._next(prompt)
    next_word = model._next(tweet)
    while len(tweet) < 100 or len(tweet + next_word) <= 280:
        tweet += ' ' + next_word
        next_word = model._next(next_word)
        if len(tweet) > 150 and tweet[-1] in ['.', '!', '?']:
            break
    return tweet

print(compose_tweet(markov, 'Whew!'))