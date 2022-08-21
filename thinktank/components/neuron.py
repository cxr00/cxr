from cxr.state.state import StateManager
from cxr.math.base36 import Tridozenal as Td


class NeuronPart:

    def __init__(self, name, dep=None):
        self.name = name
        self.dep = dep
        self.level = Td.one()
        self.cost_multiplier = Td(113) / Td(100)
        self.cost = self.level * self.cost_multiplier + Td(4)

    def __str__(self):
        output = str(self.level)
        if self.dep:
            output += "/" + str(self.dep.level)
        return output

    def can_level_up(self):
        if not self.dep:
            return True
        elif self.level < self.dep.level:
            return True
        return False

    def gain_level(self, auto=False):
        self.level += Td.one()
        if not auto:
            self.cost = (self.cost + Td(5) * (self.level / Td(3))) * self.cost_multiplier

    def convert(self):
        self.level = self.level.convert()
        self.cost_multiplier = self.cost_multiplier.convert()
        self.cost = self.cost.convert()


class Neuron(StateManager):
    def __init__(self, key, name):
        super().__init__(key, name)
        self.initialize()

    def _initialize_ser(self):

        self["energy"] = Td(150)
        self["max_energy"] = Td(150)
        self["soma_growth"] = Td.zero()

        self["soma"] = NeuronPart("soma")

        self["membrane"] = NeuronPart("membrane", self.soma)
        self["dendrites"] = NeuronPart("dendrites", self.soma)
        self["hilcock"] = NeuronPart("hilcock", self.soma)

        self["axon"] = NeuronPart("axon", self.hilcock)

        self["terminal"] = NeuronPart("terminal", self.axon)
        self["ranvier"] = NeuronPart("ranvier", self.axon)
        self["sheath"] = NeuronPart("sheath", self.axon)

        self["synapse"] = NeuronPart("synapse", self.terminal)

    def _initialize_nonser(self):
        self.nonser("soma_cost", Td.zero())
        self.nonser("soma_growth_rate", Td.zero())
        self.nonser("soma_growth_point", Td(1000))
        self.nonser("membrane_cost", Td.zero())
        self.nonser("dendrites_cost", Td.zero())
        self.nonser("hilcock_cost", Td.zero())
        self.nonser("axon_cost", Td.zero())
        self.nonser("terminal_cost", Td.zero())
        self.nonser("ranvier_cost", Td.zero())
        self.nonser("sheath_cost", Td.zero())
        self.nonser("synapse_cost", Td.zero())
        self.nonser("degeneration_reduction", Td.zero())
        self.nonser("regeneration_rate", Td(2) * (1 + self.ranvier.level / Td(10)))

        self.nonser("brain_production_rate", Td.zero())

        self.nonser("player", None)

    def initialize(self):
        self._initialize_ser()
        self._initialize_nonser()

        @self.controller
        def neuron_controller(event):
            if self.energy <= Td.zero():
                self["energy"] = Td.zero()
                self.change_state("regenerating")
            elif self.energy >= self.max_energy:
                self.change_state("producing")

        @self.add_state("producing")
        def producing(event):
            self["soma_growth"] += self.soma_growth_rate
            if self.soma_growth >= self.soma_growth_point:
                self.soma.gain_level(auto=True)
                self["soma_growth"] = Td.zero()
                self["soma_growth_point"] = ((self.soma_growth_point + Td(1200)) * Td(15) / Td(11)).as_int()
            if self.degeneration_reduction < Td.one():
                self["energy"] -= Td.one() * (Td.one() - self.degeneration_reduction)

        @self.add_state("regenerating")
        def regenerating(event):
            self["energy"] += self.regeneration_rate

    def set_player(self, player):
        self["player"] = player

    def show_stats(self, screen, font):
        text = font.render(f"soma: {self.soma}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 10))
        screen.blit(text, text_rect)

        text = font.render(f"growth: {str(self.soma_growth)} / {self.soma_growth_point}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 40))
        screen.blit(text, text_rect)

        text = font.render(f"growth rate: {str(self.soma_growth_rate)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 70))
        screen.blit(text, text_rect)

        text = font.render(f"energy: {str(self.energy.as_int())} / {str(self.max_energy)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 100))
        screen.blit(text, text_rect)

        text = font.render(f"membrane: {str(self.membrane)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 130))
        screen.blit(text, text_rect)

        text = font.render(f"dendrites: {str(self.dendrites)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 160))
        screen.blit(text, text_rect)

        text = font.render(f"hilcock: {str(self.hilcock)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 190))
        screen.blit(text, text_rect)

        text = font.render(f"axon: {str(self.axon)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(400, 220))
        screen.blit(text, text_rect)

        text = font.render(f"terminal: {str(self.terminal)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(600, 130))
        screen.blit(text, text_rect)

        text = font.render(f"ranvier: {str(self.ranvier)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(600, 160))
        screen.blit(text, text_rect)

        text = font.render(f"sheath: {str(self.sheath)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(600, 190))
        screen.blit(text, text_rect)

        text = font.render(f"synapse: {str(self.synapse)}", True, (255, 255, 255), "black")
        text_rect = text.get_rect(topleft=(600, 220))
        screen.blit(text, text_rect)

    def convert(self):
        self.soma.convert()
        self["soma_growth"] = self.soma_growth.convert()
        self["soma_growth_rate"] = self.soma_growth_rate.convert()
        self["soma_growth_point"] = self.soma_growth_point.convert()

        self.membrane.convert()
        self.dendrites.convert()
        self.hilcock.convert()

        self.axon.convert()

        self.terminal.convert()
        self.ranvier.convert()
        self.sheath.convert()

        self.synapse.convert()

        self["energy"] = self.energy.convert()
        self["max_energy"] = self.max_energy.convert()
        self["degeneration_reduction"] = self.degeneration_reduction.convert()
