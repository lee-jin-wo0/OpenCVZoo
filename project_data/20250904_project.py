import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class Sprite:
    def __init__(self, x, y, image_data):
        self.x = x
        self.y = y
        self.image = image_data
    
    def blit(self, canvas):
        h, w = self.image.shape[:2]
        if self.y + h > canvas.shape[0] or self.x + w > canvas.shape[1]:
            return
        
        roi = canvas[self.y:self.y+h, self.x:self.x+w]
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        img_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        img_fg = cv2.bitwise_and(self.image, self.image, mask=mask)
        dst = cv2.add(img_bg, img_fg)
        canvas[self.y:self.y+h, self.x:self.x+w] = dst

class TextSprite(Sprite):
    def __init__(self, x, y, korean_text, font_size, color):
        font_path = 'data/NanumPenScript-Regular.ttf'
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()

        temp_img = Image.new('RGBA', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), korean_text, font=font)
        
        margin = 5
        img_width = bbox[2] - bbox[0] + margin * 2
        img_height = bbox[3] - bbox[1] + margin * 2

        pil_img = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(pil_img)
        draw.text((margin - bbox[0], margin - bbox[1]), korean_text, font=font, fill=color)
        
        open_cv_img = cv2.cvtColor(np.array(pil_img.convert('RGB')), cv2.COLOR_RGB2BGR)
        super().__init__(x, y, open_cv_img)

class LogoSprite(Sprite):
    def __init__(self, x, y):
        try:
            logo = cv2.imread("data/googlelogo.jpg", cv2.IMREAD_COLOR)
            logo = cv2.resize(logo, (100, 100))
            logo = cv2.bitwise_not(logo)
        except:
            logo = np.ones((100, 100, 3), np.uint8) * 128
        
        super().__init__(x, y, logo)
class Maindraw:
    def __init__(self, screen_width=800, screen_height=600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.image = np.zeros((screen_width, screen_height, 3), np.uint8)
        self.mouse_position = (0, 0)
        self.mouse_on = False
        self.selected_channel = 'r'
        self.bgr_values = [0, 0, 0]

        # Use the new classes for sprites
        self.logo_sprite = LogoSprite(10, 10)
        self.text_sprite = TextSprite(120, 10, "즐거운 OpenCV 수업!", 30, (255, 0, 0, 0))

    def draw_bgr_info(self, img):
        info_text = f"B:{self.bgr_values[0]} G:{self.bgr_values[1]} R:{self.bgr_values[2]}"
        if self.selected_channel:
            info_text += f" | Selected: {self.selected_channel.upper()}"
        cv2.putText(img, info_text, (10, self.screen_height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return img

    def update_img(self, image):
        # Use sprite blit methods
        self.logo_sprite.blit(image)
        self.text_sprite.blit(image)
        image = self.draw_bgr_info(image)
        return image

    def on_mouse(self, event, x, y, flags, param):
        clone_img = self.image.copy()

        if event == cv2.EVENT_MOUSEMOVE:
            if self.mouse_on:
                cv2.circle(clone_img, (x, y), 10, (0, 255, 0), -1)
                cv2.line(clone_img, self.mouse_position, (x, y), (255, 255, 255), 2)
            else:
                cv2.rectangle(clone_img, (x-10, y-10), (x+10, y+10), (255, 0, 0), -1)
        elif event == cv2.EVENT_LBUTTONDOWN:
            if not self.mouse_on:
                self.mouse_position = (x, y)
            self.mouse_on = True
        elif event == cv2.EVENT_LBUTTONUP:
            cv2.line(self.image, self.mouse_position, (x, y), (255, 255, 255), 2)
            self.mouse_on = False

        clone_img = self.update_img(clone_img)
        cv2.imshow("main", clone_img)

    def handle_channel_selection(self, key):
        if key == ord('r'):
            self.selected_channel = 'r'
        elif key == ord('g'):
            self.selected_channel = 'g'
        elif key == ord('b'):
            self.selected_channel = 'b'

    def handle_value_adjustment(self, key):
        if key == 65362 or key == 2490368:
            if self.selected_channel == 'r':
                self.bgr_values[2] = min(255, self.bgr_values[2] + 5)
            elif self.selected_channel == 'g':
                self.bgr_values[1] = min(255, self.bgr_values[1] + 5)
            elif self.selected_channel == 'b':
                self.bgr_values[0] = min(255, self.bgr_values[0] + 5)
            self.image[::] = self.bgr_values
        elif key == 65364 or key == 2621440:
            if self.selected_channel == 'r':
                self.bgr_values[2] = max(0, self.bgr_values[2] - 5)
            elif self.selected_channel == 'g':
                self.bgr_values[1] = max(0, self.bgr_values[1] - 5)
            elif self.selected_channel == 'b':
                self.bgr_values[0] = max(0, self.bgr_values[0] - 5)
            self.image[::] = self.bgr_values

    def run(self):
        cv2.namedWindow("main")
        cv2.setMouseCallback("main", self.on_mouse)

        # Initial display
        self.logo_sprite.blit(self.image)
        self.text_sprite.blit(self.image)
        cv2.imshow("main", self.image)

        while True:
            key = cv2.waitKeyEx(30)
            if key == 27:
                break
            
            if key in [ord('r'), ord('g'), ord('b')]:
                self.handle_channel_selection(key)
            elif key in [65362, 65364, 2621440, 2490368]:
                self.handle_value_adjustment(key)
            
            if key in [ord('r'), ord('g'), ord('b'), 65362, 65364, 2621440, 2490368]:
                cloned_img = self.image.copy()
                cloned_img = self.update_img(cloned_img)
                cv2.imshow("main", cloned_img)

        cv2.destroyAllWindows()

def main():
    app = Maindraw()
    app.run()

if __name__ == "__main__":
    main()