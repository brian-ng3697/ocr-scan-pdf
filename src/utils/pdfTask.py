import re
import base64
from typing import List
from pikepdf import Pdf, Page


class TaskError(Exception):
    pass


class ErrorInvalidActionString(TaskError):
    def __init__(self, msg: str):
        super().__init__("Invalid action string:  %s" % msg)
    pass


class TaskAction:
    index: int
    rotate: int
    startPage: int
    length: int

    def __init__(self, actStr: str):
        self.__parse(actStr)

    def __eq__(self, other):
        return isinstance(other, TaskAction) and (
            self.index == other.index and self.rotate == other.rotate
        ) and self.startPage == other.startPage and self.length == other.length

    def __parse(self, actStr: str):
        """Parse string to task action

        Format: [object_index]:[start_page]-[length]#[rotate_angle]
        Example: "0:1-2#180": means get 2 pages of object index 0 from first page and rotate all page in range 180 degree.
                TaskAction(index=0, startPage=1, len=2, rotate=180)

        Args:
            actStr (str): _description_
        """
        m = re.match(
            r'^(?P<index>\d+):(?P<startPage>\d+)-(?P<length>\d+)#(?P<rotate>0|-90|90|180)$', actStr)
        if m is None:
            raise ErrorInvalidActionString(actStr)

        g = m.groupdict()

        self.index = int(g['index'])
        self.startPage = int(g['startPage'])
        self.length = int(g['length'])
        self.rotate = int(g['rotate'])


class PdfTask:
    __objs: List[Pdf]

    def __init__(self, pdfObjects: List[Pdf]):
        """Simple task to organize PDF objects

        Args:
            pdfObjects (List[Pdf]): list input PDF objects
        """
        self.__objs = pdfObjects

    def parseStringToActions(self, taskStr: str) -> List[TaskAction]:
        """Parse string to task actions 

        Args:
            taskStr (str): list action to build new PDF object

                + Format: [object_index]:[start_page]-[lenght]#[rotate_angle]

                + Example: "0:1-2#180": means get 2 pages of object index 0 from first page and rotate all page in range 180 degree.

        Returns:
            List[TaskAction]: list action to build new PDF object
        """
        acts = []
        actsStr = taskStr.split(",")

        for actS in actsStr:
            act = TaskAction(actS)
            acts.append(act)

        return acts

    def buildFromString(self, taskStr: str) -> Pdf:
        """Rebuild new PDF by task string

        Args:
            taskStr (str): list action to build new PDF object

                + Format: [object_index]:[start_page]-[lenght]#[rotate_angle]

                + Example: "0:1-2#180": means get 2 pages of object index 0 from first page and rotate all page in range 180 degree.

        Returns:
            Pdf: new PDF object
        """
        actions = self.parseStringToActions(taskStr)
        return self.build(actions)

    def build(self, acts: List[TaskAction]) -> Pdf:
        """Rebuild new PDF by task actions

        Args:
            acts (List[TaskAction]): list action to build new PDF object

        Returns:
            Pdf: new PDF object
        """
        res = Pdf.new()

        if len(acts) == 0:
            return

        for act in acts:
            pages = self.__getPDFPages(
                act.index, act.startPage, act.length, act.rotate)
            for p in pages:
                res.pages.append(p)

        return res

    def __getPDFPages(self, objIdx: int, startPage: int, pageLen: int, rotate: int) -> List[Page]:
        pages = []
        obj = self.__objs[objIdx]

        for i in range(pageLen):
            p = obj.pages.p(i + startPage)
            if rotate != 0:
                p.rotate(rotate, False)
            pages.append(p)

        return pages

def parseFilesPassword(strPw: str):
    rs = dict()
    pws = strPw.split(",")

    for pw in pws:
        m = re.match(r'^(?P<index>\d+):(?P<base64Pw>.*)$', pw)
        if m is None:
            continue
        g = m.groupdict()
        decodedPw = base64.b64decode(g['base64Pw']).decode('utf-8')
        rs[g['index']] = decodedPw.rstrip()

    return rs