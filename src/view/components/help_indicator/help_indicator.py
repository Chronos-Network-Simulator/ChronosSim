from kivy.properties import StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.dialog import MDDialog, MDDialogIcon, MDDialogHeadlineText, MDDialogSupportingText
from kivymd.uix.label import MDIcon

from theme import ThemeManager


class HelpIndicator(ButtonBehavior,MDIcon):


    help_text = StringProperty("This is a help message.")

    icon = "help-circle"

    icon_color = ThemeManager().secondary_text_color

    def on_press(self):
        """
        Display a dialog with the help text
        :return:
        """
        MDDialog(
            MDDialogIcon(icon="help-circle", theme_text_color="Custom", text_color=ThemeManager().text_color),
            MDDialogHeadlineText(text="Help", theme_text_color="Custom", text_color=ThemeManager().text_color),
            MDDialogSupportingText(text=self.help_text, theme_text_color="Custom", text_color=ThemeManager().secondary_text_color),
            md_bg_color=ThemeManager().bg_color, theme_bg_color="Custom",
        ).open()
