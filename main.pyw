import pygame
import numpy
import math
import datetime
import requests


class Watch:

    def __init__(self):
        self.now = datetime.datetime.utcnow()
        self.delta_time = 0
        self.clock = pygame.time.Clock()
        self.gotten_report_recently = False
        self.running = True
        self.full_screen = False
        self.settings = {"Settings Shown": False, "Colourful": False, "Roman Numerals": False, "Numbers Shown": True,
                         "Full Screen": False, "Weather Dials Shown": True, "Date Shown": True,
                         "Millisecond Hand Shown": False, "Mouse Visible": True}
        self.screen = pygame.display.set_mode([400, 400], pygame.RESIZABLE)
        self.colour_theta = 0.5 * numpy.pi
        self.colour = [0, 0, 0]
        self.background_colour = [255, 255, 255]
        self.current_temp = 0
        self.current_humidity = 0
        self.current_wind_speed = 0
        self.clock_center = [self.screen.get_width()/2, self.screen.get_height()/2]
        self.clock_rad = (min(self.screen.get_width(), self.screen.get_height()) / 2) * 0.9
        pygame.display.set_icon(pygame.image.load("clock.png"))

    def get_report(self):
        api_key = "7d1101afcf32e84c30a5f48afdf16dc2"
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = "Oxford"
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        report = response.json()
        print(report)
        self.current_temp, self.current_humidity, self.current_wind_speed = 0, 0, 0
        if report["cod"] != "404":
            main = report["main"]
            wind = report["wind"]
            self.current_wind_speed = wind["speed"]
            self.current_temp = main["temp"]
            self.current_humidity = main["humidity"]

    def run(self):
        while self.running:
            self.now = datetime.datetime.now()
            click_pos = self.check_input()
            self.update_settings()
            pygame.display.set_caption("Clock: (" + str(self.now.hour) + ":" + str(self.now.minute) + ":" + str(self.now.second) + ")")
            self.clock_center = [self.screen.get_width()/2, self.screen.get_height()/2]
            self.clock_rad = (min(self.screen.get_width(), self.screen.get_height()) / 2) * 0.9
            self.delta_time = self.clock.tick(60) / 1000
            self.set_colour()
            self.screen.fill(self.background_colour)
            self.draw_dials()
            self.draw_clock_face(self.clock_rad, self.clock_center, 60, 5, 0, 1, False)
            self.draw_month_counter()
            self.draw_numbers()
            self.draw_hands()
            self.draw_settings(click_pos)
            pygame.display.update()

    def update_settings(self):
        if pygame.mouse.get_visible() and not self.settings["Mouse Visible"]:
            pygame.mouse.set_visible(False)
        elif not pygame.mouse.get_visible() and self.settings["Mouse Visible"]:
            pygame.mouse.set_visible(True)
        if not self.settings["Full Screen"] and self.full_screen:
            self.full_screen = False
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode([400, 400], pygame.RESIZABLE)
            pygame.display.set_icon(pygame.image.load("clock.png"))
        elif self.settings["Full Screen"] and not self.full_screen:
            self.full_screen = True
            self.screen = pygame.display.set_mode([0, 0], pygame.FULLSCREEN)

    def draw_settings(self, click_pos):
        if not self.settings["Settings Shown"]:
            return
        width = max(int(self.clock_rad * 0.015), 1)
        pygame.draw.rect(self.screen, self.background_colour, pygame.Rect(width/2, width/2, min(self.screen.get_width(), self.screen.get_height()) * (1/2), min(self.screen.get_width(), self.screen.get_height()) * (7/10)))
        pygame.draw.rect(self.screen, self.colour, pygame.Rect(width/2, width/2, min(self.screen.get_width(), self.screen.get_height()) * (1/2), min(self.screen.get_width(), self.screen.get_height()) * (7/10)), width)
        font = pygame.font.SysFont("bahnschrift", int(self.clock_rad * 0.12))
        settings_text_surface = font.render("Settings:", True, self.colour)
        self.screen.blit(settings_text_surface, [self.clock_rad * 0.03, self.clock_rad * 0.025])
        for index, setting in enumerate(self.settings):
            font = pygame.font.SysFont("bahnschrift", int(self.clock_rad * 0.07))
            text_surface = font.render(setting, True, self.colour)
            pos = [self.clock_rad * 0.03, (self.clock_rad * 0.025 + index * text_surface.get_height()) + settings_text_surface.get_height()]
            self.screen.blit(text_surface, pos)
            checkbox_pos = [pos[0] + min(self.screen.get_width(), self.screen.get_height()) * 0.45, pos[1] + 0.1 * text_surface.get_height()]
            if self.draw_checkbox(self.settings[setting], checkbox_pos, text_surface.get_height() * 0.9, click_pos):
                self.settings[setting] = self.toggle(self.settings[setting])
                if setting == "Mouse Visible" and not self.settings["Mouse Visible"] and self.settings["Settings Shown"]:
                    self.settings["Settings Shown"] = False

    def draw_checkbox(self, state, pos, size, click_pos):
        width = int(size * 0.1)
        if state:
            width = 0
        pygame.draw.rect(self.screen, self.colour, pygame.Rect(pos[0], pos[1], size, size), width)
        if pos[0] < click_pos[0] < pos[0] + size and pos[1] < click_pos[1] < pos[1] + size:
            return True

    def draw_dials(self):
        if self.settings["Weather Dials Shown"]:
            self.check_report()
            self.draw_temp_clock()
            self.draw_wind_clock()
            self.draw_humidity_clock()

    def check_report(self):
        if self.now.second % 60 == 0 and self.now.minute % 5 == 0 and not self.gotten_report_recently:
            self.gotten_report_recently = True
            self.get_report()
        if self.now.second % 60 != 0:
            self.gotten_report_recently = False

    def draw_temp_clock(self):
        center = [self.clock_center[0] - self.clock_rad / 2.5, self.clock_center[1]]
        angle = ((self.current_temp - 273.15) * (numpy.pi / 43.75)) - (numpy.pi * (11/10))
        self.draw_clock_face(self.clock_rad/4, center, 5, 1, -0.5 * numpy.pi, 2.7, True, "C°", (-10, 60), numpy.pi * (4/5))
        self.draw_hand(angle, self.clock_rad/6, int(self.clock_rad * 0.02), center)

    def draw_wind_clock(self):
        center = [self.clock_center[0], self.clock_center[1] + self.clock_rad / 2.5]
        angle = (self.current_wind_speed * (numpy.pi / 18.75)) - (numpy.pi * (13/10))
        self.draw_clock_face(self.clock_rad/4, center, 5, 1, -0.5 * numpy.pi, 2.7, True, "m/s", (0, 30), numpy.pi * (4/5))
        self.draw_hand(angle, self.clock_rad/6, int(self.clock_rad * 0.02), center)

    def draw_humidity_clock(self):
        center = [self.clock_center[0] + self.clock_rad / 2.5, self.clock_center[1]]
        angle = (self.current_humidity * (numpy.pi / 62.5)) - (numpy.pi * (13/10))
        self.draw_clock_face(self.clock_rad/4, center, 5, 1, -0.5 * numpy.pi, 2.7, True, "%", (0, 100), numpy.pi * (4/5))
        self.draw_hand(angle, self.clock_rad/6, int(self.clock_rad * 0.02), center)

    def draw_numbers(self):
        clock_rad = (min(self.screen.get_width(), self.screen.get_height()) / 2) * 0.9
        center = [self.screen.get_width()//2, self.screen.get_height()//2]
        numerals = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
        if self.settings["Numbers Shown"]:
            for dot in range(0, 60):
                if dot % 5 == 0:
                    angle = dot * (numpy.pi / 30)
                    small_center = [center[0] + math.cos(angle) * (clock_rad * 0.8), center[1] + math.sin(angle) * (clock_rad * 0.8)]
                    font = pygame.font.SysFont("bahnschrift", int(clock_rad * 0.12))
                    if self.settings["Roman Numerals"]:
                        text_surface = font.render(str(numerals[(dot // 5 + 3) % 12]), True, self.colour)
                    else:
                        text_surface = font.render(str((dot // 5 + 2) % 12 + 1), True, self.colour)
                    self.screen.blit(text_surface, [small_center[0] - 0.5 * text_surface.get_width(), small_center[1] - 0.5 * text_surface.get_height()])

    def set_colour(self):
        if self.settings["Colourful"]:
            self.colour_theta += numpy.pi * self.delta_time
            r = int(127.5 * (numpy.sin(self.colour_theta) + 1))
            g = int(127.5 * (numpy.cos(self.colour_theta) + 1))
            b = int(127.5 * (numpy.cos(self.colour_theta + (0.5 * numpy.pi)) + 1))
            self.colour = [r, g, b]
            self.background_colour = [255 - r, 255 - g, 255 - b]
        else:
            self.colour = [0, 0, 0]
            self.background_colour = [255, 255, 255]

    def draw_month_counter(self):
        if not self.settings["Date Shown"]:
            return
        center = [self.screen.get_width()//2, self.screen.get_height()//2]
        clock_rad = (min(self.screen.get_width(), self.screen.get_height()) / 2) * 0.9
        font = pygame.font.SysFont("bahnschrift", int(clock_rad * 0.15))
        text_surface = font.render(str(self.now.day) + " " + self.now.strftime("%b").upper() + " " + str(self.now.year)[-2:], True, self.colour)
        self.screen.blit(text_surface, [center[0] - 0.5 * text_surface.get_width(), center[1] - clock_rad * 0.53])
        pygame.draw.rect(self.screen, self.colour, pygame.Rect(center[0] - 0.54 * text_surface.get_width(), center[1] - clock_rad * 0.53, text_surface.get_width() * 1.08, text_surface.get_height()), max(int(clock_rad*0.02), 1))

    def draw_hands(self):
        millisecond_angle = (((self.now.microsecond / 1000) % 1000) - 250) * (numpy.pi / 500)
        second_angle = (self.now.second - 15 + self.now.microsecond / 1000000) * (numpy.pi / 30)
        minute_angle = (self.now.minute - 15 + self.now.second / 60) * (numpy.pi / 30)
        hour_angle = ((self.now.hour % 12) - 3 + self.now.minute / 60) * (numpy.pi / 6)
        if self.settings["Millisecond Hand Shown"]:
            self.draw_hand(millisecond_angle, self.clock_rad * 0.9, int(self.clock_rad * 0.01), self.clock_center, overhang=0.1)
        self.draw_hand(minute_angle, self.clock_rad * 0.9, int(self.clock_rad * 0.03), self.clock_center, overhang=0.1)
        self.draw_hand(hour_angle, self.clock_rad * 0.5, int(self.clock_rad * 0.05), self.clock_center, overhang=0.1)
        self.draw_hand(second_angle, self.clock_rad * 0.9, int(self.clock_rad * 0.015), self.clock_center, overhang=0.1, colour=(200, 0, 0))

    def draw_hand(self, angle, length, width, center, overhang=0.0, colour=None):
        if colour is None or self.settings["Colourful"]:
            colour = self.colour
        end_pos = [center[0] + math.cos(angle) * length, center[1] + math.sin(angle) * length]
        start_pos = [center[0] - math.cos(angle) * length * overhang, center[1] - math.sin(angle) * length * overhang]
        pygame.draw.line(self.screen, colour, center, end_pos, max(width, 1))
        pygame.draw.line(self.screen, colour, start_pos, center, max(width, 1))

    def draw_clock_face(self, radius, center, dots, big_dot_mod, angle_offset, width_multiplier, with_units, unit="", unit_range=(0, 0), unit_angle=0):
        if with_units:
            self.draw_units(radius, center, unit_range, unit, unit_angle, width_multiplier)
        pygame.draw.circle(self.screen, self.colour, center, radius, max(int(radius * 0.03 * width_multiplier), 1))
        pygame.draw.circle(self.screen, self.colour, center, radius * 0.03 * width_multiplier, 0)
        self.draw_dots(radius, center, dots, big_dot_mod, angle_offset, width_multiplier)

    def draw_units(self, radius, center, unit_range, unit, unit_angle, width_multiplier):
        font = pygame.font.SysFont("bahnschrift", int(radius * 0.3))
        text_surface = font.render(unit, True, self.colour)
        self.screen.blit(text_surface, [center[0] - 0.5 * text_surface.get_width(), center[1] - radius * 0.53])
        hypotenuse = ((radius * 0.96) - (radius * 0.06 * width_multiplier))
        text_surface = font.render(str(unit_range[0]), True, self.colour)
        small_center = [center[0] + math.cos(-(0.5 * numpy.pi) - unit_angle) * hypotenuse, center[1] - (text_surface.get_height() * 0.6) + math.sin(-(0.5 * numpy.pi) - unit_angle) * hypotenuse]
        self.screen.blit(text_surface, [small_center[0] - 0.5 * text_surface.get_width(), small_center[1] - 0.5 * text_surface.get_height()])
        text_surface = font.render(str(unit_range[1]), True, self.colour)
        small_center = [center[0] + math.cos(-(0.5 * numpy.pi) + unit_angle) * hypotenuse, center[1] - (text_surface.get_height() * 0.6) + math.sin(-(0.5 * numpy.pi) + unit_angle) * hypotenuse]
        self.screen.blit(text_surface, [small_center[0] - 0.5 * text_surface.get_width(), small_center[1] - 0.5 * text_surface.get_height()])

    def draw_dots(self, radius, center, dots, big_dot_mod, angle_offset, width_multiplier):
        for dot in range(0, dots):
            dot_radius = radius * 0.015
            if dot % big_dot_mod == 0:
                dot_radius = radius * 0.03
            angle = dot * (numpy.pi / (dots / 2)) + angle_offset
            hypotenuse = ((radius * 0.96) - (radius * 0.06 * width_multiplier))
            small_center = [center[0] + math.cos(angle) * hypotenuse, center[1] + math.sin(angle) * hypotenuse]
            pygame.draw.circle(self.screen, self.colour, small_center, dot_radius * width_multiplier, 0)

    def check_input(self):
        click_pos = (-1, -1)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    click_pos = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.settings["Full Screen"] = self.toggle(self.settings["Full Screen"])
                if event.key == pygame.K_n:
                    self.settings["Numbers Shown"] = self.toggle(self.settings["Numbers Shown"])
                if event.key == pygame.K_r:
                    self.settings["Roman Numerals"] = self.toggle(self.settings["Roman Numerals"])
                if event.key == pygame.K_c:
                    self.settings["Colourful"] = self.toggle(self.settings["Colourful"])
                if event.key == pygame.K_w:
                    self.settings["Weather Dials Shown"] = self.toggle(self.settings["Weather Dials Shown"])
                if event.key == pygame.K_d:
                    self.settings["Date Shown"] = self.toggle(self.settings["Date Shown"])
                if event.key == pygame.K_m:
                    self.settings["Millisecond Hand Shown"] = self.toggle(self.settings["Millisecond Hand Shown"])
                if event.key == pygame.K_TAB:
                    self.settings["Settings Shown"] = self.toggle(self.settings["Settings Shown"])
                    if self.settings["Settings Shown"] and not self.settings["Mouse Visible"]:
                        self.settings["Mouse Visible"] = True
                if event.key == pygame.K_h:
                    self.settings["Mouse Visible"] = self.toggle(self.settings["Mouse Visible"])
                    if self.settings["Settings Shown"] and not self.settings["Mouse Visible"]:
                        self.settings["Settings Shown"] = False
        return click_pos

    @staticmethod
    def toggle(value):
        if value:
            value = False
        else:
            value = True
        return value


pygame.init()
pygame.display.init()
pygame.font.init()

watch = Watch()
watch.get_report()

watch.run()

pygame.quit()
