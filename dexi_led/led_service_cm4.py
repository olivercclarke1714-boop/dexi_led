import rclpy
from rclpy.node import Node
from dexi_interfaces.srv import LEDPixelColor, LEDRingColor, LEDEffect
import board
import neopixel
import threading
import time
from enum import Enum
import colorsys

from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.color import (
    RED as red,
    YELLOW as yellow,
    ORANGE as orange,
    GREEN as green,
    TEAL as teal,
    CYAN as cyan,
    BLUE as blue,
    PURPLE as purple,
    MAGENTA as magenta,
    WHITE as white,
    BLACK as black,
    GOLD as gold,
    PINK as pink,
    AQUA as aqua,
    JADE as jade,
    AMBER as amber,
    OLD_LACE as old_lace
)

class LEDService(Node):

    def __init__(self):
        super().__init__('led_service')
        self.led_pixel_service = self.create_service(LEDPixelColor, '~/set_led_pixel_color', self.set_led_pixel_callback)
        self.led_color_service = self.create_service(LEDRingColor, '~/set_led_ring_color', self.set_led_ring_callback)
        self.effect_service = self.create_service(LEDEffect, '~/set_led_effect', self.effect_callback)
        
        self.pixel_pin = board.D12
        self.num_pixels = 45
        self.pixel_order = neopixel.GRB
        self.pixels = neopixel.NeoPixel(self.pixel_pin, self.num_pixels, brightness=0.2, auto_write=False, pixel_order=self.pixel_order)
        
        # Add effect control variables
        self.effect_thread = None
        self.effect_running = False
        self._is_shutting_down = False


    def set_led_pixel_callback(self, request, response):
        self.get_logger().info(str(request))
        self.pixels[request.index] = (request.r, request.g, request.b)
        self.pixels.show()
        response.success = True
        return response

    def set_led_ring_callback(self, request, response):
        self.get_logger().info(str(request))
        try:
            # Stop any running effect first
            self.stop_current_effect()
            
            color = eval(request.color)
            solid = Solid(self.pixels, color=color)
            solid.animate()
            response.success = True
            response.message = "Successfully set LED ring color"
        except:
            response.success = False
            response.message = "LED ring color not available"

        return response

    def blink_effect(self, color_name, delay=0.5):
        """Creates a blinking effect with specified color and delay"""
        color_map = {
            'red': red,
            'green': green,
            'blue': blue,
            'yellow': yellow,
            'purple': purple,
            'cyan': cyan,
            'white': white,
            'orange': orange,
            'teal': teal,
            'magenta': magenta,
            'gold': gold,
            'pink': pink,
            'aqua': aqua,
            'jade': jade,
            'amber': amber,
            'old_lace': old_lace,
            'black': black
        }
        
        if color_name not in color_map:
            self.get_logger().error(f"Unknown color: {color_name}")
            return
            
        color = color_map[color_name]
        
        while self.effect_running:
            if not self.effect_running:
                break
                
            # Turn all LEDs to specified color
            self.pixels.fill(color)
            self.pixels.show()
            time.sleep(delay)
            
            if not self.effect_running:
                break
                
            # Turn all LEDs off
            self.pixels.fill(black)
            self.pixels.show()
            time.sleep(delay)

    def rainbow_effect(self):
        """Creates a rainbow effect with rotating colors"""
        colors = [
            red,      # Red
            orange,   # Orange
            yellow,   # Yellow
            green,    # Green
            blue,     # Blue
            (75, 0, 130),   # Indigo
            purple    # Violet
        ]

        num_colors = len(colors)
        while self.effect_running:
            for offset in range(self.num_pixels):
                if not self.effect_running:
                    break
                for i in range(self.num_pixels):
                    self.pixels[i] = colors[(i + offset) % num_colors]
                self.pixels.show()
                time.sleep(0.05)

    def meteor_effect(self):
        """Creates a meteor shower effect with random colors and positions"""
        import random
        meteor_length = 10
        delay = 0.1

        while self.effect_running:
            meteor_start = random.randint(0, self.num_pixels - 1)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Meteor falling animation
            for i in range(meteor_start, meteor_start + meteor_length):
                if not self.effect_running:
                    break

                self.pixels.fill(black)
                for j in range(meteor_length):
                    if i - j >= 0 and i - j < self.num_pixels:
                        # Calculate fading intensity based on position
                        fade = 1 - (j / meteor_length)
                        r = int(color[0] * fade)
                        g = int(color[1] * fade)
                        b = int(color[2] * fade)
                        self.pixels[i - j] = (r, g, b)

                self.pixels.show()
                time.sleep(delay)

    def comet_effect(self):
        """Creates a comet effect with a trailing fade"""
        delay = 0.1
        color = blue  # Blue color
        trail_length = 10  # Length of the comet trail

        while self.effect_running:
            for i in range(self.num_pixels + trail_length):
                if not self.effect_running:
                    break

                self.pixels.fill(black)  # Clear the strip
                for j in range(trail_length):
                    if 0 <= i - j < self.num_pixels:
                        # Calculate fading intensity
                        intensity = 1 - (j / trail_length)
                        r = int(color[0] * intensity)
                        g = int(color[1] * intensity)
                        b = int(color[2] * intensity)
                        self.pixels[i - j] = (r, g, b)

                self.pixels.show()
                time.sleep(delay)

    def galaxy_spiral_effect(self):
        """Creates a spiral galaxy effect with multiple rotating color arms"""
        import random
        delay = 0.05
        # Define multiple color arms for the spiral
        arms = [
            magenta,    # Purple
            (0, 100, 255),    # Light Blue
            white,  # White
            (255, 50, 0)      # Orange-Red
        ]
        num_arms = len(arms)
        spacing = self.num_pixels // num_arms
        fade_length = spacing // 2

        while self.effect_running:
            for offset in range(self.num_pixels):
                if not self.effect_running:
                    break

                self.pixels.fill(black)

                # Create multiple rotating arms
                for arm_idx, color in enumerate(arms):
                    # Calculate the starting point for each arm
                    arm_offset = (offset + (arm_idx * spacing)) % self.num_pixels

                    # Create the spiral arm with fading
                    for i in range(fade_length):
                        # Calculate two positions: forward and backward from the arm center
                        pos_forward = (arm_offset + i) % self.num_pixels
                        pos_backward = (arm_offset - i) % self.num_pixels

                        # Calculate fade intensity based on distance from arm center
                        intensity = 1 - (i / fade_length)
                        # Add some shimmer with random variation
                        intensity *= (0.85 + random.random() * 0.15)

                        r = int(color[0] * intensity)
                        g = int(color[1] * intensity)
                        b = int(color[2] * intensity)

                        # Set LEDs on both sides of the arm center
                        self.pixels[pos_forward] = (r, g, b)
                        self.pixels[pos_backward] = (r, g, b)

                self.pixels.show()
                time.sleep(delay)

    def ripple_effect(self):
        """Creates a ripple effect with color waves moving outward from center"""
        delay = 0.1
        color = blue  # Blue color
        center = self.num_pixels // 2  # Center of the strip
        ripple_length = 10  # Length of the ripple wave

        while self.effect_running:
            for radius in range(self.num_pixels // 2 + ripple_length):
                if not self.effect_running:
                    break

                self.pixels.fill(black)
                # Create fading ripple on both sides of center
                for j in range(ripple_length):
                    # Calculate fading intensity
                    intensity = 1 - (j / ripple_length)
                    r = int(color[0] * intensity)
                    g = int(color[1] * intensity)
                    b = int(color[2] * intensity)

                    # Set LEDs symmetrically from center with fade
                    if center - (radius - j) >= 0:
                        self.pixels[center - (radius - j)] = (r, g, b)
                    if center + (radius - j) < self.num_pixels:
                        self.pixels[center + (radius - j)] = (r, g, b)

                self.pixels.show()
                time.sleep(delay)

    def loading_effect(self):
        """Creates a loading bar effect with a single moving LED"""
        delay = 0.1
        color = green  # Green color

        while self.effect_running:
            for i in range(self.num_pixels):
                if not self.effect_running:
                    break

                self.pixels.fill(black)  # Clear the strip
                self.pixels[i] = color  # Set current LED to green
                self.pixels.show()
                time.sleep(delay)
                
    def gradient_effect(self):
        """Creates a gradient effect"""
        hue_increment = 0.01
        hue = 0.0
        delay = 0.025

        while self.effect_running: 
            r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
            color = (int(r*255), int(g*255), int(b*255))

            self.pixels.fill(color)
            self.pixels.show()

            hue += hue_increment   
            hue %= 1.0            

            time.sleep(delay)

    def wave_effect(self):
        """Creates a wave the propagates from the center"""
        delay = 0.05
        colors = [
            red,      # Red
            orange,   # Orange
            yellow,   # Yellow
            green,    # Green
            blue,     # Blue
            (75, 0, 130),   # Indigo
            purple    # Violet
        ]

        while self.effect_running:
            for i in range(len(colors)):
                for j in range((self.num_pixels // 2) + 1): 
                    if not self.effect_running:
                        break   

                    self.pixels[j] = colors[i]
                    if not j == 0:
                        self.pixels[self.num_pixels - j] = colors[i]
                    
                    self.pixels.show()
                    time.sleep(delay)
                

    def snake_effect(self):
        """Creates a gradient snake effect"""
        hue_increment = 0.00667
        hue = 0.0
        delay = 0.035
        
        while self.effect_running:
            for i in range(self.num_pixels):
                if not self.effect_running:
                    break
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                color = (int(r*255), int(g*255), int(b*255))

                self.pixels[i] = color
                self.pixels.show()

                hue += hue_increment   
                hue %= 1.0            

                time.sleep(delay)

    def festive_effect(self):
        """Creates alterating festive lights"""
        delay = 0.4
        ring_state_even = []
        ring_state_odd = []
        colors = [
            green,
            red
        ]
        
        for i in range(self.num_pixels):
            if (i // 2) % 2 == 0: ring_state_even.append(colors[0])
            else: ring_state_even.append(colors[1])

        ring_state_odd = ring_state_even[2:] + ring_state_even[:2]

        while self.effect_running:
            self.pixels[:] = ring_state_even
            self.pixels.show()

            time.sleep(delay)

            if not self.effect_running:
                break

            self.pixels[:] = ring_state_odd
            self.pixels.show()

            time.sleep(delay)
            
    def stop_current_effect(self):
        self.effect_running = False
        if self.effect_thread is not None:
            self.effect_thread.join()
            self.effect_thread = None

    def effect_callback(self, request, response):
        """Service callback for setting LED effects"""
        self.get_logger().info(f'Setting LED effect to: {request.effect_name}')

        try:
            # Stop any currently running effect
            self.stop_current_effect()

            if request.effect_name.lower() == 'rainbow':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.rainbow_effect)
                self.effect_thread.start()
                self.get_logger().info("Started rainbow effect")
                response.success = True
                response.message = "Successfully started rainbow effect"
            elif request.effect_name.lower() == 'gradient':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.gradient_effect)
                self.effect_thread.start()
                self.get_logger().info("Started gradient effect")
                response.success = True
                response.message = "Successfully started gradient effect"
            elif request.effect_name.lower() == 'wave':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.wave_effect)
                self.effect_thread.start()
                self.get_logger().info("Started wave effect")
                response.success = True
                response.message = "Successfully started wave effect"
            elif request.effect_name.lower() == 'snake':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.snake_effect)
                self.effect_thread.start()
                self.get_logger().info("Started snake effect")
                response.success = True
                response.message = "Successfully started snake effect" 
            elif request.effect_name.lower() == 'festive':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.festive_effect)
                self.effect_thread.start()
                self.get_logger().info("Started festive effect")
                response.success = True
                response.message = "Successfully started festive effect"
            elif request.effect_name.lower() == 'meteor':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.meteor_effect)
                self.effect_thread.start()
                self.get_logger().info("Started meteor effect")
                response.success = True
                response.message = "Successfully started meteor effect"
            elif request.effect_name.lower() == 'comet':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.comet_effect)
                self.effect_thread.start()
                self.get_logger().info("Started comet effect")
                response.success = True
                response.message = "Successfully started comet effect"
            elif request.effect_name.lower() == 'galaxy':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.galaxy_spiral_effect)
                self.effect_thread.start()
                self.get_logger().info("Started galaxy spiral effect")
                response.success = True
                response.message = "Successfully started galaxy spiral effect"
            elif request.effect_name.lower() == 'ripple':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.ripple_effect)
                self.effect_thread.start()
                self.get_logger().info("Started ripple effect")
                response.success = True
                response.message = "Successfully started ripple effect"
            elif request.effect_name.lower() == 'loading':
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.loading_effect)
                self.effect_thread.start()
                self.get_logger().info("Started loading effect")
                response.success = True
                response.message = "Successfully started loading effect"
            elif request.effect_name.lower().startswith('blink_'):
                # Extract color from effect name (e.g., "blink_cyan" -> "cyan")
                color_name = request.effect_name.lower().replace('blink_', '')
                self.effect_running = True
                self.effect_thread = threading.Thread(target=self.blink_effect, args=(color_name,))
                self.effect_thread.start()
                self.get_logger().info(f"Started {color_name} blink effect")
                response.success = True
                response.message = f"Successfully started {color_name} blink effect"
            elif request.effect_name.lower() == 'stop':
                self.get_logger().info("Stopped current effect")
                response.success = True
                response.message = "Successfully stopped effect"
            else:
                self.get_logger().warning("Unknown effect requested")
                response.success = False
                response.message = "Unknown effect requested"
            
        except Exception as e:
            response.success = False
            response.message = f"Failed to set effect: {str(e)}"
            self.get_logger().error(f"Failed to set effect: {str(e)}")
        
        return response

    def cleanup(self):
        """Clean up resources"""
        if self._is_shutting_down:
            return
            
        self._is_shutting_down = True
        print('Cleaning up LED resources...')
        
        # Stop any running effect
        self.stop_current_effect()
        
        # Turn off LEDs
        try:
            self.pixels.fill(black)
            self.pixels.show()
        except Exception as e:
            print(f'Error during LED cleanup: {str(e)}')

    def destroy_node(self):
        """Override destroy_node to ensure cleanup"""
        self.cleanup()
        super().destroy_node()

    def rainbow(self):
        return

    def fill (self):
        return


def main(args=None):
    try:
        rclpy.init(args=args)
        led_service = LEDService()
        
        try:
            rclpy.spin(led_service)
        except KeyboardInterrupt:
            print('Keyboard interrupt received, shutting down...')
            led_service.cleanup()
        finally:
            led_service.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()
    except Exception as e:
        print(f'Error initializing node: {str(e)}')


if __name__ == '__main__':
    main()
