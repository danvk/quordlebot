declare class MersenneTwister {
  constructor(seed: number);
  random_int31(): number;
}

function generateWords(seed: number, wordBank: string[], blacklist: Set<string>) {
  let words: string[];
  const r = new MersenneTwister(seed);
  r.random_int31(), r.random_int31(), r.random_int31(), r.random_int31();
  do {
    words = [
      wordBank[r.random_int31() % wordBank.length],
      wordBank[r.random_int31() % wordBank.length],
      wordBank[r.random_int31() % wordBank.length],
      wordBank[r.random_int31() % wordBank.length]
    ];
  } while (
    words[0] === words[1] ||
    words[0] === words[2] ||
    words[0] === words[3] ||
    words[1] === words[2] ||
    words[1] === words[3] ||
    words[2] === words[3] ||
    blacklist.has(words[0]) ||
    blacklist.has(words[1]) ||
    blacklist.has(words[2]) ||
    blacklist.has(words[3])
  );
  return words
};

