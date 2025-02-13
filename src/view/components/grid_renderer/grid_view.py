from kivy.uix.boxlayout import BoxLayout


class GridView(BoxLayout):
    """
    This component is responsible for rendering the current grid onto the screen.
    All grids must be broken down into regions. Each of these regions are rendered
    as individual components inside the grid.  The node on the grid are rendered as
    graphic instructions instead to make rendering easier.
    """


    def draw_grid(self, grid):
        """
        Draws the grid with all of its regions onto the screen. This is designed to be
        only called when the grid has changed and not when the simulation is running.
        :param grid:
        :return:
        """
        pass