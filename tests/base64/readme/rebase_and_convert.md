## Rebase and Convert

This module explores the rebase-convert iteration function R(c, r, k)

`c` is the base of the starting value `c ** k`. It is also the base which the current value is converted to after every rebase. Unlike rebasing, converting preserves the quantity represented by the original base interpretation. For example, 100 in base 10 converts to 202 in base 7. Same quantity, different representations.

`r` is the rebasing base. To rebase a number means to treat the digits of the number as if they are in base r. When this is done, the quantity the number represents fundamentally changes. 100 in base 10 means 100, but if we rebase it to 7 then its digits are still 100, but its equivalent base 10 value is 49.

When c > r, N > R(N, r).

The algorithm takes the starting value and rebases it to base r. It then converts the result back to base c. The process is repeated until the value is less than c ** (k-1) - 1, meaning it is a base c number with k-1 or fewer digits, and that value is the result of the function.

While originally testing the iteration, I would use a starting value of c ** 2 and would iterate until reaching c-1 or less, but decided to add a parameter k to replace 2. Then I started selecting a particular k, then looping through every c from 3 to 36, and every r from 2 to c-1.

I noticed that, as c increased, the results of this nested loop started to look like `2**k`, `3**k`, `4**k`, and so on. I also noticed that the first time this would happen for a particular value of r, it would always be with converting base r+1.

So I wondered: For any c with r=c-d for some value of d, what is the minimum value of k where R(c, r, k) = r ** k ?

The convergence point for a given c, or C(c, d, n) is precisely that. It is computed by compute_convergence_sequence(d, n). Due to the limitations of cxr.base36, we can only analyze up to c = 36. Once d reaches 4, the sequence increases by 1 each time. 

`count_steps` can be used to track the total number of times a number is (rebased then converted) before it reaches the target value.
Fun fact: when k=2, the number of steps of R(c, c-2, k) is always c-2, and the steps of R(c, c-1, k) is always c-1. No idea why, though.
