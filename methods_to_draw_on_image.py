"""Module with methods for drawing text on an image."""
from typing import Callable

from PIL import ImageFont, ImageDraw, Image
#TODO: MAny func to del

class MethodsToDrawOnImage:
    def __init__(self, on_add_log: Callable[[int, str, str, str, bool], None]):
        """
        __used_fonts - {<path_font>: {<size_font>: <object font PIL>}} - dictionary with loaded fonts
        __get_font(str, int) -> PIL.ImageFont.FreeTypeFont - zwraca potrzebną czcionkę

        TODO: Dodaj dodawnaie logów
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
        #TODO sprawdź jakie najczęściej czcioniki są używane, do pokazywania wyników, które zawsze mają ten sam rozmiar
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

    def save_image(self, img: Image.Image, path: str):
        try:
            img.save(path, "PNG")
        except OSError as e:
            self._on_add_log(9, "MDI_SAVE_ERROR", "", f"Nie można zapisać obrazka: {path}: {e}", True)

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
        TODO 'x'
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
            x = (width - w) // 2
        elif align == "right":
            x = width - w
        else:
            x = 0
        x, y = width / 2, height / 2
        draw.text((x, y), text, font=font, fill=color, anchor="mm")
        return img_cell

    def draw_center_text_in_cell(self, img_cell: Image.Image, text: str | int | float, font_size: int,
                                 font_path: str, color: tuple | list, width: int, height: int) -> Image.Image:
        """
        Return of the cell image with added vertically and horizontally centered text.

        :param img_cell: <Image.Image> cell image
        :param text: <str | int | float> the text to be added to the cell
        :param font_size: <int> the largest size, if it does not fit, it will set the largest possible size
        :param font_path: <str>
        :param color: <tuple | list> font color saved in format (B, G, R)
        :param width: <int> cell width
        :param height: <int> cell height
        :return: <Image.Image> cell with added centered text
        """
        text = str(text)
        if text == "":
            return img_cell
        color = tuple(color)
        font_size = int(font_size)

        draw = ImageDraw.Draw(img_cell)
        while True:
            try:
                font = self.__get_font(font_path, font_size)
            except OSError:
                return img_cell
            w, h = draw.textsize(text, font=font)
            if w <= width and h <= height:
                break
            font_size -= 1
            if font_size <= 0:
                break
        x = (width - w) // 2
        y = (height - h) // 2
        draw.text((x, y), text, font=font, fill=color)
        return img_cell

    def draw_center_text_by_coord(self, img: Image.Image, text: str | int | float, font_size: int,
                                  font_path: str, color: tuple | list,
                                  coords: list[int, int, int, int] | tuple[int, int, int, int]) -> Image.Image:
        """
        Methods for drawing text on a cell image with an added caption centered vertically and horizontally.

        :param img: <Image.Image> cell image
        :param text: <str | int | float> the text to be added to the cell
        :param font_size: <int> the largest size, if it does not fit, it will set the largest possible size
        :param font_path: <str>
        :param color: <tuple | list> font color saved in format (B, G, R)
        :param coords: <list | tuple> coordinates: left, right, top, bottom
        :return: <Image.Image> cell with added centered text
        """
        return self.__draw_text_by_coord("center", img, text, font_size, font_path, color, coords)

    def draw_left_text_by_coord(self, img: Image.Image, text: str | int | float, font_size: int,
                                  font_path: str, color: tuple | list,
                                  coords: list[int, int, int, int] | tuple[int, int, int, int]) -> Image.Image:
        """
        Returns an image of a cell with a left-justified and leveled caption added.

        :param img: <Image.Image> cell image
        :param text: <str | int | float> the text to be added to the cell
        :param font_size: <int> the largest size, if it does not fit, it will set the largest possible size
        :param font_path: <str>
        :param color: <tuple | list> font color saved in format (B, G, R)
        :param coords: <list | tuple> coordinates: left, right, top, bottom
        :return: <Image.Image> cell with added text on the left edge
        """
        return self.__draw_text_by_coord("left", img, text, font_size, font_path, color, coords)

    def draw_right_text_by_coord(self, img: Image.Image, text: str | int | float, font_size: int,
                                 font_path: str, color: tuple | list,
                                 coords: list[int, int, int, int] | tuple[int, int, int, int]) -> Image.Image:
        """
        Returns an image of a cell with a right-justified and leveled caption added.

        :param img: <Image.Image> cell image
        :param text: <str | int | float> the text to be added to the cell
        :param font_size: <int> the largest size, if it does not fit, it will set the largest possible size
        :param font_path: <str>
        :param color: <tuple | list> font color saved in format (B, G, R)
        :param coords: <list | tuple> coordinates: left, right, top, bottom
        :return: <Image.Image> cell with added text on the right edge
        """
        return self.__draw_text_by_coord("right", img, text, font_size, font_path, color, coords)

    def __draw_text_by_coord(self, kind_position: str, img: Image.Image, text: str | int | float, font_size: int,
                             font_path: str, color: tuple | list,
                             coords: list[int, int, int, int] | tuple[int, int, int, int]) -> Image.Image:
        """
        Returns an image of the cell with the selected caption justified and leveled.

        :param kind_position: <str> how the text should be arranged: right/center/left
        :param img: <Image.Image> cell image
        :param text: <str | int | float> the text to be added to the cell
        :param font_size: <int> the largest size, if it does not fit, it will set the largest possible size
        :param font_path: <str>
        :param color: <tuple | list> font color saved in format (B, G, R)
        :param coords: <list | tuple> coordinates: left, right, top, bottom
        :return: <Image.Image> cell with added centered text
        """
        text = str(text)
        if text == "":
            return img
        color = tuple(color)
        font_size = int(font_size)

        width = coords[1] - coords[0]
        height = coords[3] - coords[2]

        draw = ImageDraw.Draw(img)
        while True:
            try:
                font = self.__get_font(font_path, font_size)
            except OSError:
                return img
            w, h = draw.textsize(text, font=font)
            if w <= width and h <= height:
                break
            font_size -= 1
            if font_size <= 0:
                break
        if kind_position == "right":
            x = coords[1] - w
        elif kind_position == "center":
            x = (width - w) // 2 + coords[0]
        else:
            x = coords[0]
        y = (height - h) // 2 + coords[2]
        draw.text((x, y), text, font=font, fill=color)
        return img