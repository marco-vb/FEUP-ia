from state import State
from solver import Solver
from gui import GUI


def main():
    state = State()
    solver = Solver(state)
    gui = GUI(state, solver)

    gui.run()


if __name__ == "__main__":
    main()
