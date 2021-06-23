import time
from typing import List, Optional, Tuple

import numpy as np
import PIL
import pyscreenshot as pyss
from pynput.mouse import Button, Controller


class DoorCracker:
    def __init__(
        self,
        button_distance: int,
        start_x: int,
        start_y: int,
        validation_bar_x: int,
        validation_bar_y: int,
        gray_color: Tuple[int],
        entry_field_bbox: Tuple[int],
        time_delta: float
    ):
        self.delete: Tuple[int] = (
            start_x + button_distance, start_y + 3 * button_distance)
        self.coords: List[Tuple[int]] = [
            (start_x, start_y + 3 * button_distance)]

        for i in range(1, 10):
            self.coords.append(
                (start_x + (i-1) % 3 * button_distance,
                 start_y + (i - 1) // 3 * button_distance)
            )

        self.gray_color = gray_color
        self.validation_bar_x = validation_bar_x
        self.validation_bar_y = validation_bar_y
        self.entry_field_box = entry_field_bbox
        self.dt = time_delta

        self.mouse = Controller()

    def click_on_button(self, btn: int, dt: int) -> None:
        if btn < 0:
            self.mouse.position = self.delete
        else:
            self.mouse.position = self.coords[btn]

        time.sleep(dt)

        assert self.mouse.position in [self.delete, self.coords[btn]]
        self.mouse.click(Button.left)

    def button_is_grayed_out(self) -> bool:
        color = pyss.grab([
            self.validation_bar_x,
            self.validation_bar_y,
            self.validation_bar_x + 1,
            self.validation_bar_y + 1
        ]).getpixel((0, 0))

        return color == self.gray_color

    def entry_field_is_clear(self) -> bool:
        colors = np.array(pyss.grab(self.entry_field_box, False))
        out = (colors is not None) and (colors == 255).all()
        return out

    def crack(self, start: int = 0, repeat_delete_clicks: int = 10, delete_dt: int = 0.05) -> Optional[int]:
        for num in (str(i).zfill(4) for i in range(start, 10_000)):
            try:
                for _ in range(repeat_delete_clicks):
                    self.click_on_button(-1, delete_dt)

                for c in num:
                    self.click_on_button(int(c), self.dt)
            except AssertionError as e:
                raise e(num)

            if not self.button_is_grayed_out():
                return num


if __name__ == '__main__':
    #(1270, 445, 1290, 446)
    dc = DoorCracker(120, 1160, 580, 1000, 1050,
                     (134, 134, 134), (1230, 440, 1330, 480), 0.10)
    time.sleep(5)
    print(dc.crack(1200))
