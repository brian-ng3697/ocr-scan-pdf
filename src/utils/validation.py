import re

class Validations:
    def __init__(self):
        pass

    def isNumber(v):
        isN = False
        result = re.match("[-+]?\d+$", v)
        if result is not None:
            isN = True
        return isN

    def isValidString(self, text: str) -> bool:
        special_characters = "!@#$%^&*()-+?_=,<>/"
        if any(c in special_characters for c in text):
            return True
        else:
            return False


class PdfPageSize:
    def __init__(self):
        pass

    def get(page):
        if '/CropBox' in page:
        # use CropBox if defined since that's what the PDF viewer would usually display
            relevant_box = page.CropBox
        elif '/MediaBox' in page:
            relevant_box = page.MediaBox
        else:
            # fall back to ANSI A (US Letter) if neither CropBox nor MediaBox are defined
            # unlikely, but possible
            relevant_box = [0, 0, 612, 792]

        # actually there could also be a viewer preference ViewArea or ViewClip in
        # pdf.Root.ViewerPreferences defining which box to use, but most PDF readers 
        # disregard this option anyway

        # check whether the page defines a UserUnit
        userunit = 1
        if '/UserUnit' in page:
            userunit = float(page.UserUnit)

        # convert the box coordinates to float and multiply with the UserUnit
        relevant_box = [float(x)*userunit for x in relevant_box]

        # obtain the dimensions of the box
        width  = abs(relevant_box[2] - relevant_box[0])
        height = abs(relevant_box[3] - relevant_box[1])

        rotation = 0
        if '/Rotate' in page:
            rotation = page.Rotate

        # if the page is rotated clockwise or counter-clockwise, swap width and height
        # (pdf rotation modifies the coordinate system, so the box always refers to 
        # the non-rotated page)
        if (rotation // 90) % 2 != 0:
            width, height = height, width

        # now you have width and height in points
        # 1 point is equivalent to 1/72in (1in -> 2.54cm)

        return width / 72, height / 72
