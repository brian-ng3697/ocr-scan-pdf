import uuid
from src.services.imageHandling import ImageHandling
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch, cm
from PIL import Image
from pikepdf import Pdf, Page
from ..config.config import settings
from ..utils.validation import PdfPageSize
from pdfminer.high_level import extract_text

class PdfHandling:
    #constructor
    def __init__(self):
        super(PdfHandling, self).__init__()

    def generateTextWatermark(self, msg, whPdf):
        outFolder = ImageHandling.printTmpDir()
        wpdf, hpdf = whPdf
        strUUID = uuid.uuid4().hex
        pathFile = '%s/%s.pdf' % (outFolder, strUUID)
        c = canvas.Canvas(pathFile)
        c.setPageSize((wpdf * inch, hpdf * inch))

        c.setFillColor(HexColor('#f2f2f2'))
        c.setFont("Helvetica-Bold", 40)
        # c.translate(10*cm, 10*cm) 
        c.rotate(30)

        textWidth = stringWidth(msg, 'Helvetica-Bold', 40)
        for n in range(0, 9):
            y = (textWidth * n) + ((1 * n) * inch)
            for n in range(0, 5):
                x = (textWidth * n) + ((2 * n) * inch)
                c.drawString(x, y, msg)
            
        c.save()
        return pathFile

    def addImageSignature(self, pathImage, whPdf, xy):
        wpdf, hpdf = whPdf
        x, y = xy
        outFolder = ImageHandling.printTmpDir()
        strUUID = uuid.uuid4().hex
        pathFile = '%s/%s.pdf' % (outFolder, strUUID)
        c = canvas.Canvas(pathFile)
        c.setPageSize((wpdf * inch, hpdf * inch))

        im = Image.open(pathImage)
        imwidthpx, imheightpx = im.size

        c.drawImage(pathImage, x * inch, y * inch, width=float(imwidthpx/96) * inch, height=float(imheightpx/96) * inch)
        c.save()
        return pathFile
    
    def addWatermark(self, filePath, watermarkText=""):
        arrFileDel = []
        text = settings.WatermarkSettings.Text
        if len(watermarkText) > 0:
            text = watermarkText

        with Pdf.open(filePath, allow_overwriting_input=True) as pdf:
            for n, _ in enumerate(pdf.pages):
                destinationPage = Page(pdf.pages[n])
                w, h = PdfPageSize.get(destinationPage)
                watermarkPath = self.generateTextWatermark(text, (w, h))
                arrFileDel.append(watermarkPath)
                with Pdf.open(watermarkPath) as watermarkPDF:
                    watermarkPage = Page(watermarkPDF.pages.p(1))
                    destinationPage.add_underlay(watermarkPage)

            pdf.save(filePath)
        
        for i in arrFileDel:
            ImageHandling().cleanSingleImage(filePathWithName=str(i))
        
        return filePath
    
    def extractionTextPath(self, pdfPath: str) -> str:
        ptep = '%s/%s.pdf' % (ImageHandling.printTmpDir(), uuid.uuid4().hex)
        with Pdf.open(pdfPath) as pdf:
            pdf.save(ptep)
        return ptep
    
    def extractingText(self, filePath: str):
        return extract_text(filePath)

    def validationPassword(self, passwd: str):
        val = True
        if len(passwd) < 3:
            val = False
        if len(passwd) > 8:
            val = False
        if any(char.isspace() for char in passwd):
            val = False
        if not any(char.isdigit() for char in passwd):
            val = False
        if not any(char.isupper() for char in passwd):
            val = False
        if not any(char.islower() for char in passwd):
            val = False

        return val