from cxr.state.state import StateManager
from cxr.math.base36 import Tridozenal as Td
from thinktank.components import Neuron

resource_rate_multiplier = Td(37)
resource_prod_rate_multiplier = Td(7)

prod_rate_multiplier = Td(137)


class Brain(StateManager):

    def __init__(self, key, name):
        super().__init__(key, name)
        self.initialize()

    def _initialize_ser(self,):
        self["science"] = Td(3) / Td(4)
        self["art"] = Td(137) / Td(100)
        self["literature"] = Td(37) / Td(100)
        self["philosophy"] = Td(11) / Td(10)

    def _initialize_nonser(self):
        self.nonser("player", None)
        self.nonser("neuron", StateManager.generate("neuron", Neuron, self.key + "_neuron"))
        self.nonser("timer", Td(120))

    def initialize(self):
        self._initialize_ser()
        self._initialize_nonser()

        @self.controller
        def brain_controller(event):
            self.neuron(event)
            if self.neuron.current_state() == "producing":
                self["timer"] -= Td.one() + self.neuron.brain_production_rate
                if self.timer <= Td.zero():
                    self.player.add_resources(self.science, self.art, self.literature, self.philosophy, self.neuron.synapse.level / resource_rate_multiplier)
                    self["timer"] = Td(120)

    def set_neuron(self, neuron):
        self["neuron"] = neuron

    def set_player(self, player):
        self["player"] = player
        self.neuron.set_player(player)

    def convert(self):
        global resource_rate_multiplier, prod_rate_multiplier, resource_prod_rate_multiplier
        resource_rate_multiplier = resource_rate_multiplier.convert()
        prod_rate_multiplier = prod_rate_multiplier.convert()
        resource_prod_rate_multiplier = resource_prod_rate_multiplier.convert()

        self["science"] = self.science.convert()
        self["art"] = self.art.convert()
        self["literature"] = self.literature.convert()
        self["philosophy"] = self.philosophy.convert()
        self["timer"] = self.timer.convert()
        self.neuron.convert()
