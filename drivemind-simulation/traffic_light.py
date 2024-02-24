import time


class TrafficLight:
    def __init__(self, green_duration, yellow_duration, red_delay):
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.red_delay = red_delay
        self.last_change_time = time.time()
        self.state = "red"
        self.visual_state = "red"

    def update(self):
        current_time = time.time()
        time_elapsed = current_time - self.last_change_time

        if self.state == "green" and time_elapsed > self.green_duration:
            self._switch_to_yellow(current_time)
        elif self.state == "yellow" and time_elapsed > self.yellow_duration:
            self._switch_to_red(current_time)
        elif self.state == "red" and time_elapsed > self.red_delay:
            self.state = "red_delayed"

    def _switch_to_yellow(self, current_time):
        self.last_change_time = current_time
        self.state = "yellow"
        self.visual_state = "yellow"

    def _switch_to_red(self, current_time):
        self.last_change_time = current_time
        self.state = "red"
        self.visual_state = "red"

    def switch_to_green(self):
        if self.state == "red_delayed":
            self.state = "green"
            self.visual_state = "green"
            self.last_change_time = time.time()

    def get_state(self):
        return self.state

    def get_visual_state(self):
        return self.visual_state

    def is_red_delayed(self):
        return self.state == "red_delayed"

    def is_green(self):
        return self.state == "green"
