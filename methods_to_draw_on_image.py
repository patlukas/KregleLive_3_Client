"""Module with methods for drawing text on an image."""
import shutil
from typing import Callable

from PIL import ImageFont, ImageDraw, Image

class MethodsToDrawOnImage:
    def __init__(self, on_add_log: Callable[[int, str, str, str, bool], None]):
        """
        __used_fonts - {<path_font>: {<size_font>: <object font PIL>}} - dictionary with loaded fonts
        __get_font(str, int) -> PIL.ImageFont.FreeTypeFont - zwraca potrzebną czcionkę

        """
        self.__used_fonts: dict = {}
        self._on_add_log: Callable[[int, str, str, str, bool], None] = on_add_log

    def __get_font(self, font_path: str, font_size: int) -> ImageFont.FreeTypeFont:
        """
        Method responsible for returning the required font.

        If the required font has not been used yet, then download it and save it in __used_fonts, and if it has been
        used, then return the font from __used_fonts.

        :param font_path: <str> path to font file
        :param font_size: <str> expected font size
        :return: <ImageFont.FreeTypeFont> object with font
        """
        if font_path in self.__used_fonts and font_size in self.__used_fonts[font_path]:
            return self.__used_fonts[font_path][font_size]
        font = ImageFont.truetype(font_path, font_size)
        if font_path not in self.__used_fonts:
            self.__used_fonts[font_path] = {}
        self.__used_fonts[font_path][font_size] = font
        return font

    @staticmethod
    def crop_img(img: Image.Image, left: int, top: int, width: int, height: int) -> Image.Image:
        return img.crop((left, top, left + width, top + height))

    @staticmethod
    def paste_img(img: Image.Image, part_img: Image.Image, left: int, top: int) -> Image.Image:
        img.paste(part_img, (left, top))
        return img

    @staticmethod
    def fill_cell_background(cell: Image.Image, background_color: tuple | list) -> Image.Image:
        w, h = cell.size
        cell.paste(tuple(background_color), (0, 0, w, h))
        return cell

    def load_image(self, path: str) -> Image.Image | None:
        try:
            image = Image.open(path)
            return image
        except FileNotFoundError:
            self._on_add_log(9, "MDI_LOADIMG_ERROR", "", f"Nie istnieje obrazek pod ścieżką: {path}", True)
            print(f"Plik '{path}' nie istnieje.")
        except OSError:
            self._on_add_log(9, "MDI_LOADIMG_ERROR", "", f"Plik nie jest obrazkiem: {path}", True)
            print(f"Plik '{path}' nie jest poprawnym obrazem.")
        return None

    @staticmethod
    def create_img(width: int, height: int, background: tuple) -> Image.Image:
        if type(background) == list:
            background = tuple(background)
        return Image.new("RGB", (width, height), background)

    def save_image(self, img: Image.Image, path: str) -> bool:
        """
        Method to save image in os.
        First, the image is saved to a temporary location and then replaced in the appropriate location.

        :param img: <Image.Image> image
        :param path: <str> path to place where file should be saved
        :return: <bool> was success or not
        """
        try:
            img.save(path + "_temp", "PNG")
            shutil.move(path + "_temp", path)
            return True
        except OSError as e:
            self._on_add_log(9, "MDI_SAVE_ERROR", "", f"Nie można zapisać obrazka: {path}: {e}", True)
            return False

    def draw_text_in_cell(self, img_cell: Image.Image, text: str, max_font_size: int, font_path: str,
                          color: tuple | list, width: int, height: int, align: str) -> Image.Image:
        """
        Return of the cell image with added vertically and horizontally centered text.

        :param img_cell: <Image.Image> cell image
        :param text: <str> the text to be added to the cell
        :param max_font_size: <int> the max size, if it does not fit, it will set the largest possible size
        :param font_path: <str>
        :param color: <tuple | list> font color saved in format (B, G, R)
        :param width: <int> cell width
        :param height: <int> cell height
        :param align: <str> "center", "right" or "left" - text position in cell
        :return: <Image.Image> cell with added centered text
        """
        if text == "":
            return img_cell
        color = tuple(color)
        draw = ImageDraw.Draw(img_cell)
        while True:
            try:
                font = self.__get_font(font_path, max_font_size)
            except OSError:
                return img_cell
            l, t, r, b = font.getbbox(text)
            w = r
            h = b
            if w <= width and h <= height:
                break
            max_font_size -= 1
            if max_font_size <= 0:
                break
        if align == "center":
            anchor = "mm"
            x = width / 2
        elif align == "right":
            anchor = "rm"
            x = width
        else:
            anchor = "lm"
            x = 0
        y = height / 2
        draw.text((x, y), text, font=font, fill=color, anchor=anchor)
        return img_cell
