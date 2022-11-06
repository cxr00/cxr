from cxr import Clq, UndefinedError
from cxr import Seq
from cxr import SMR, SM, SMF
import random


def generate_operand(functions):
    output_str = "_"
    functions = list([*functions])
    role_choices = [str(n) for n in range(len(functions))]
    while functions and role_choices:
        r = random.choice(functions)
        functions.pop(functions.index(r))
        r2 = random.choice(role_choices)
        role_choices.pop(role_choices.index(r2))
        output_str += r + r2
    return Clq.decompile(output_str)


class ClqManager(SM):
    def __init__(self, key, name):
        super().__init__(key, name)
        self._initialise()

    def process(self, interaction, to_perform_on):
        self.new_dataset.add(str(interaction))
        self.current_dataset.remove(to_perform_on)

    def random(self):
        return random.choice(list(self.full_dataset))

    def _initialise(self):
        self.toggle_ser_priority(False)

        self["start_clq"] = generate_operand("0123456789")
        self["full_dataset"] = set()
        self.full_dataset.add(str(self.start_clq))
        self["current_dataset"] = set()
        self.current_dataset.add(str(self.start_clq))
        self["new_dataset"] = set()
        self["previous_operand"] = -1
        self["recently_added"] = 1

        @self.controller
        def controller(event):
            if self.current_dataset:
                r = random.randint(0, 3)
                if r == self.previous_operand:
                    r = random.randint(0, 3)
                match r:
                    case 0 | 4:
                        self.change_state("including")
                    case 1 | 5:
                        self.change_state("rejecting")
                    case 2 | 6:
                        self.change_state("isolating")
                    case 3 | 7 | 8:
                        self.change_state("reducing")

                self["previous_operand"] = r
            else:
                self.change_state("compiling")

        @self.add_state("including")
        def including(event):
            to_perform_on = list(self.current_dataset).pop(0)
            interaction = Clq(to_perform_on) + generate_operand(Clq(to_perform_on).compile()[2::2])
            self.process(interaction, to_perform_on)

        @self.add_state("rejecting")
        def rejecting(event):
            to_perform_on = list(self.current_dataset).pop(0)
            interaction = Clq(to_perform_on) - generate_operand(Clq(to_perform_on).compile()[2::2])
            self.process(interaction, to_perform_on)

        @self.add_state("isolating")
        def isolating(event):
            to_perform_on = list(self.current_dataset).pop(0)
            interaction = Clq(to_perform_on) * generate_operand(Clq(to_perform_on).compile()[2::2])
            self.process(interaction, to_perform_on)

        @self.add_state("reducing")
        def reducing(event):
            to_perform_on = list(self.current_dataset).pop(0)
            interaction = Clq(to_perform_on) / generate_operand(Clq(to_perform_on).compile()[2::2])
            self.process(interaction, to_perform_on)

        @self.add_state("compiling")
        def compiling(event):
            added = 0
            for each in self.new_dataset:
                if str(each) not in self.full_dataset:
                    added += 1
                    self.full_dataset.add(str(each))
            self["recently_added"] = added
            # print(f"added {added}...")
            self["current_dataset"] = set(self.full_dataset)
            self["new_dataset"] = set()
            if event["target"] <= len(self.full_dataset):
                self.change_state("terminating")

        @self.add_state("terminating")
        def terminating(event):
            pass


def main():
    SMR.initialize("clqscape")
    clq_factory = SMF("clq", ClqManager)

    rand_sequences = []
    rand_clqs = []

    for j in range(10):
        clq = clq_factory.make()
        event = {"target": 1000}
        s_ = []

        for i in range(1000):
            try:
                clq(event)
                if clq.current_state() == "compiling":
                    s_.append(clq.recently_added)
            except UndefinedError as exc:
                pass
            if clq.current_state() == "terminating":
                break

        buckets = [[] for _ in range(10)]
        for e in clq.full_dataset:
            buckets[len(e)-2] += [e]
        rand_sequences.append(Seq(s_).i().f(l=10))
        rand_clqs.append(clq.random())

    for seq in rand_sequences:
        print(seq)
    print()

    for clq in rand_clqs:
        print(clq)
    print()


if __name__ == "__main__":
    main()
