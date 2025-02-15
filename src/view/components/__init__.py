# Import all components here directly


import os

from kivy.lang import Builder

from .chevron import Chevron
from .custom_button.custom_button import CustomButton
from .custom_slider.custom_slider import CustomSlider
from .dropdown.custom_dropdown import CustomDropDown
from .help_indicator.help_indicator import HelpIndicator
from .numeric_input.numeric_input import NumericInput
from .textfield.custom_textfield import CustomTextField

# Get the absolute path of the components directory
components_dir = os.path.dirname(__file__)

# # Walk through all subdirectories and load kv files
for root, dirs, files in os.walk(components_dir):
    for file in files:
        if file.endswith(".kv"):
            kv_file = os.path.join(root, file)
            Builder.load_file(kv_file)
