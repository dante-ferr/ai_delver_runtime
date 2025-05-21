from .simulation import Simulation


class SimulationController:
    def __init__(self, level):
        self.level = level
        self.all_simulations: list[Simulation] = []
        self.current_simulation: Simulation = Simulation(level)

    def start_new_simulation(self):
        self.current_simulation = Simulation(self.level)
