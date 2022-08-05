## cxr.htd

Htd stands for "hyper-tridozenal". An Htd is a Tridozenal whose digits are themselves Tridozenals.

As such, it has two bases: the hyperbase, which is to the Htd as the base is to a Tridozenal; and the implicit base, which is the base of the Htd's digits.

The purpose of Htd is to extend the range of the hyperbase beyond base 36 while preserving readibility. If we tried to use standard base 20, let's say, then you need to add the characters A-J to your digit set. You need to know the entire character set, and that entails learning its additions and multiplications as well. But if we have an implicit base of ten, then we simply use the numbers 10 through 19. This means you can more easily function in a given base by treating it as an extension of base ten.

Hypernumbers already exist and see some use! In fact, IPv6 is a six-digit number in hyperbase 65336, with implicit base 16 and a colon separator. IPv4, on the other hand, is hyperbase 256 with implicit base 10 and a period separator.

The class Htd is nearly identical to Td, but instead of submitting sequences of primitive ints, you submit sequences of Tds.

Like Td, I had to manually copy snr's Seq arithmetic which works with Tds, so that I could quickly implement Htd arithmetic. This process can be repeated, but for now I'm letting it stay theoretical while I work with Htd. I'm certain that properties of Hhtd, etc, will largely depend on the properties of Htd.

### Encryption

If you have a set of hyperbases `h` and a set of implicit bases `b`, you can encrypt a string with `Htd.encrypt`. This is done by converting each character into an Htd. `h` and `b` do not necessarily need to be the same length.

```python
from cxr.htd import Htd

h = [10, 11, 12]
b = [3, 5]

s = "Hello world"

s_enc = Htd.encrypt(s, h, b)
```

Decryption is performed by submitting the encrypted string (along with `h` and `b`) to `Htd.decrypt`.

```python
s_de = Htd.decrypt(s_enc, h, b)
```

There's nothing preventing decryption using the incorrect keys, but the results won't be very useful.

So why does this even exist? Well, I thought it would be an interesting exercise to encode using Htds, then I realized I could encode each byte with a different hyperbase and implicit base. It meant that, without knowing both of those numbers, that single character couldn't be reliably decoded. So I started referring to `h` and `b` as keys and tested for potential attack vectors. Ultimately I determined that you need some knowledge of what exactly you're looking for. It's sort of like how Enigma was cracked because of the consistency of how every message was ended.

For this to be most effective, one should aim to satisfy the condition `h_(n % len(h)) >= b_(n % len(b))`. Since key length does not seem to impact encryption time, the longer the better.

### Character attack

A character attack is an attempt to brute force an Htd ciphertext by analyzing each Htd and determining the range of characters it can be decrypted to. The set of character sets may then be analyzed further to deduce the contents of the encrypted message.

A basic character attack of a randomly-encrypted "Hello world" (only accounting for alphanumeric characters and spaces) is (probably) infeasible to compute without social engineering, especially because collision is inherently very high. I've started referring to this property as *gaslighting*, as in a gaslighting encryption algorithm.

See `tests.htd.character_attack` for a more in-depth explanation.

### Echo attack

Another way to attack an Htd ciphertext is to try and figure out the cycle which the keys create and decrypt multiple characters at a time. The cycle itself is `math.lcm(len(h), len(b)` for keys `h` and `b`. The smaller the cycle, the easier it is to crack.

It is not usually feasible to perform this type of attack unless you know that the cycle is very short (like 2 or 3). Frequency analysis also fails, because one representation of an Htd such as "1,0,0" cannot be distinguished from another, so one cannot reliably assume that two instances of the same number represent the same characters, **even if the cycle seems coherent**.

See `tests.htd.echo_attack` for an example.