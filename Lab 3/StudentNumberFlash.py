import pygame
import time

class StudentNumberMonitorFlasher:
    def __init__(self, student_numbers, screen_width=800, screen_height=600, display_duration=5, flash_duration=1):
        self.student_numbers = student_numbers
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.display_duration = display_duration
        self.flash_duration = flash_duration

        pygame.init()
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Student number flashing")

        self.font = pygame.font.SysFont("Arial", 36)

    def render_text(self, text, y_position):
        text_surface = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, y_position))
        return text_surface, text_rect

    def run(self):
        start_time = time.time()  
        current_time = 0  
        i = 0  

        running = True
        while running:
            self.screen.fill((0, 0, 0))  

            if i < len(self.student_numbers):
                number_start_time = time.time()  
                while time.time() - number_start_time < self.display_duration:
                    self.screen.fill((0, 0, 0)) 
                    text_surface, text_rect = self.render_text(self.student_numbers[i], self.screen_height // 4)
                    self.screen.blit(text_surface, text_rect)

                    if int(time.time()) % 2 == 0:
                        pygame.display.flip()  
                    else:
                        pygame.display.update()

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False

                    pygame.display.update()  

                i += 1  

            if i >= len(self.student_numbers):
                break

        pygame.quit()


# To run the program, instantiate the class and call the run method:
if __name__ == "__main__":
    student_numbers = ["20250224-01", "20250224-02", "20250224-03", "20250224-04"]
    monitor_flasher = MonitorFlasher(student_numbers)
    monitor_flasher.run()
