from kivy.app import App
from kivy.factory import Factory
from kivy.lang import Builder, Parser
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout

class RootLayout(BoxLayout):
    screen_manager = ObjectProperty()

    def __init__(self, **kwargs):
        super(RootLayout, self).__init__(**kwargs)
        self.show_kv(None, 'Monitor')

    def show_kv(self, instance, value):
        self.screen_manager.current = value
        child = self.screen_manager.current_screen.children[0]
        with open(child.kv_file, 'rb') as file:
            self.language_box.text = file.read().decode('utf8')


class BeatsApp(App):
    def build(self):
        return RootLayout()

if __name__ == '__main__':
    BeatsApp().run()