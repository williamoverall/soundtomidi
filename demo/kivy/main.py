from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.factory import Factory
from kivy.lang import Builder, Parser
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')

class RootLayout(BoxLayout):
    screen_manager = ObjectProperty()

class BeatsApp(App):
    def build(self):
        return RootLayout()

if __name__ == '__main__':
    BeatsApp().run()
