import numpy as np
from PIL import Image

def tooth_check(x, y, teeth):
    """Проверяет 8 соседей вокруг пикселя (вспомогательная)."""
    a = 0
    if teeth[x-1, y-1] == 255: a += 1
    if teeth[x-1, y]   == 255: a += 1
    if teeth[x-1, y+1] == 255: a += 1
    if teeth[x, y-1]   == 255: a += 1
    if teeth[x, y]     == 255: a += 1
    if teeth[x, y+1]   == 255: a += 1
    if teeth[x+1, y-1] == 255: a += 1
    if teeth[x+1, y]   == 255: a += 1
    if teeth[x+1, y+1] == 255: a += 1
    return a

def apply_segmentation(state):
    """
    Выполняет сегментацию зуба (оригинальный алгоритм).
    Изменяет state.original_image.
    """
    img = np.array(state.original_image)
    koef_wh = 140
    koef_bl = 190

    teeth0 = img[:, :, 0]
    teeth1 = img[:, :, 1]
    teeth2 = img[:, :, 2]

    teeth01 = np.where(teeth0 > koef_wh, 255, 0)
    teeth11 = np.where(teeth1 > koef_wh, 255, 0)
    teeth21 = np.where(teeth2 > koef_wh, 255, 0)

    teeth3 = np.where(teeth0 < koef_bl, 255, 0)
    teeth4 = np.where(teeth1 < koef_bl, 255, 0)
    teeth5 = np.where(teeth2 < koef_bl, 255, 0)

    teeth3 -= teeth01
    teeth4 -= teeth11
    teeth5 -= teeth21

    teeth = np.zeros_like(img)
    for x in range(img.shape[0]-1, 0, -1):
        for y in range(img.shape[1]-1, 0, -1):
            if teeth3[x,y] == teeth4[x,y] == teeth5[x,y] and teeth3[x,y] != 0:
                teeth[x,y,1] = 255

    teeth = np.where(teeth[:,:,1] == 255, 0, 255)
    teeth244 = np.zeros_like(img)

    for x in range(teeth.shape[0]-2, 0, -1):
        for y in range(teeth.shape[1]-2, 0, -1):
            if tooth_check(x, y, teeth) >= 9:
                teeth244[x,y,2] = 255

    teeth244[:,:,1] = teeth
    result = Image.fromarray(teeth244.astype(np.uint8))

    # Сохраняем историю
    state.push_history()
    state.original_image = result