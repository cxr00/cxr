import re

"""
* annotation verification: the process through which a prompt's annotations
are verified to be accurate, usually with the assistance of the model.

* annotation forgery: the act of intentionally creating false or
misleading annotations in an attempt to destabilise prompt security.

This module's function perform annotation verification on the given input.
"""


def annotation_verification(user_input, lr, log=False):
    """
    Checks the annotations of a given string for signs of forgery

    :param user_input: the text which is being checked for signs of forgery
    :param lr: the characters used to wrap annotation tags
    :param log: whether or not to display logs
    :return: check result
    """
    pattern = f"\\{lr[0]}/*[\\w\\-\\s]+\\{lr[1]}"
    tag_re = re.compile(pattern)  # Finds [tag] and [/tag]

    # Construct tags
    def open_tag(tag): return lr[0] + tag + lr[1]
    def close_tag(tag): return lr[0] + "/" + tag + lr[1]

    # Construct regices
    def make_open_re(tag): return "\\" + lr[0] + tag + "\\" + lr[1]
    def make_close_re(tag): return "\\" + lr[0] + "/" + tag + "\\" + lr[1]

    def find_all_tags(pattern, string):
        n = 0
        output = []
        while n < len(string):
            tag = pattern.search(string[n:])
            if tag is None:
                break
            output.append(tag.group(0)[1:-1])
            n = n + tag.span()[1]
        return output

    # Gather tags
    tags = find_all_tags(tag_re, user_input)
    if log:
        print(f"user input:\n{user_input}")
        print("tags:", tags)
    only_open_tags = [tag for tag in tags if "/" not in tag]

    # Check for uneven number of tags, the most obvious sign of annotation forgery.
    if len(tags) % 2:
        return f"Error: uneven number of tags."

    # Check that there is a corresponding [/tag] for every [tag]
    for tag in only_open_tags:
        if user_input.count(open_tag(tag)) != user_input.count(close_tag(tag)):
            return f"Error: unequal number of closing and opening tags for {tag}."

    # Check that there is an equal amount of opening and closing tags
    tag_count = sum([1 for tag in tags if "/" in tag])
    if tag_count != len(tags) // 2:
        return f"Error: unequal distribution of opening and closing tags."

    # Check that there are no overlapping tags
    for tag_a in only_open_tags:
        tmp = user_input
        n = 0
        count = only_open_tags.count(tag_a)
        while n < count:
            open_point = re.search(make_open_re(tag_a), tmp).span()[0]
            close_point = re.search(make_close_re(tag_a), tmp).span()[1]
            if open_point >= close_point:
                return f"Error: closing tag '{lr[0]}/{tag_a}{lr[1]}' appears before '{lr[0]}{tag_a}{lr[1]}'."
            substring = tmp[open_point:close_point]
            for tag_b in only_open_tags:
                if tag_a != tag_b and (
                    (open_tag(tag_b) in substring and close_tag(tag_b) not in substring)
                    or
                    (close_tag(tag_b) in substring and open_tag(tag_b) not in substring)
                ):
                    return f"Error: tag '{tag_b}' overlaps with '{tag_a}'."
            n += 1
            tmp = tmp[close_point:]
    return "Pass"


if __name__ == "__main__":
    print(annotation_verification("[a]la[b]ti[/b][/a][c]do[/c]", "[]", True))
    print()
    print(annotation_verification("<a><b>la</b></a>", "<>", True))
    print()
    print(annotation_verification("{ }{b}c{/b}{/ }", "{}", True))
    print()
    print(annotation_verification("{/a} test {a}", "{}", True))
    print()
    print(annotation_verification("<a>test<b>test</a>test</b>", "<>", True))
    print()
    print(annotation_verification("{a}test{b}test2{/b}", "{}", True))
    print()
    print(annotation_verification("[a]test[b]test[/b][/b]", "[]", True))
