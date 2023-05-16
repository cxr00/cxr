## Choix de Bruxelles / Brussels' Choice

CDB is a simple algorithm:

* Start with a number in any base;
* Select a substring from that number;
* Take the number created by the substring and either double it, or halve it if it is even;
* Put the number back together to get a new number.

For example, if we have the number 22 in base 3, we can select the first 2 and halve it to 1, then combine it with the remaining 2 to get 12.

We can also double it to 4, which resolves to 11, and combine it back to get 112.

Another example would be the number 131 in base 5. We take 13, halve it to 4, then recombine to get 41.

`choix_de_bruxelles.py` is concerned with finding the *maximum number of distinct numbers* produced by performing CDB *n* times starting with 1. So in base 3 you can perform it three times by doubling it to 2, then again to 11, then double the left digit to get 21. But there are actually 6 total numbers you can reach:

```
1 -> 2 -> 11
11 -> 12
11 -> 21
11 -> 22
```

In the OEIS, the sequence [A323289](https://oeis.org/A323289) showcases this process in base ten (the number following 9). I personally submitted sequence [A356511](https://oeis.org/A356511) to compute it in duodecimal (12) and [A356715](https://oeis.org/A356715) in ternary (3).

This becomes an expensive operation quite quickly. Extending this sequence beyond 18-20 will need distributed processes to test every possible combination of doubling/halving.

Currently I have no plans to add any other CDB sequences to the OEIS besides 12 and 3. However, if there is sufficient interest, I would next add either base 7, 13, 17, or 19, as the prime bases probably have the most interesting patterns.

If the base is a power of 2, then the resultant sequence is [A000027](https://oeis.org/A000027), the positive integers, and the limit of CDB-N as N approaches infinity is as well.