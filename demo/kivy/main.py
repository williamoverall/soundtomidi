from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout

class MainScreen(Screen):
    def start(self):
        pass

    def update(self,dt):
        print("Updating")

class SettingsScreen(Screen):
    pass

class BeatsScreenManager(ScreenManager):
    def __init__(self):
        ScreenManager.__init__(self)
        self.add_widget(MainScreen(name='main'))
        self.add_widget(SettingsScreen(name='settings'))

    def start(self):
        pass

    def update(self,dt):


class BeatsApp(App):
    def build(self):
        clock_update_interval = 1.0/60.0
        screen_manager = BeatsScreenManager()
        screen_manager.start()

        Clock.max_iteration = 40
        Clock.schedule_interval(screen_manager.update, clock_update_interval)
        return screen_manager

if __name__ == '__main__':
    BeatsApp().run()