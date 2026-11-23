"""LibreOffice Python macro: refresh fields / indexes, save DOCX and PDF.
Paths come from env vars REPORT_IN, REPORT_OUT_DOCX, REPORT_OUT_PDF. Called by finalize_report.sh."""
import os
import uno
from com.sun.star.beans import PropertyValue


def _p(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p


def finalize(*args):
    ctx = XSCRIPTCONTEXT.getComponentContext()  # noqa: F821 (provided by LibreOffice)
    desktop = ctx.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)
    src, out_docx, out_pdf = (os.environ[k] for k in ("REPORT_IN", "REPORT_OUT_DOCX", "REPORT_OUT_PDF"))
    doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(src), "_blank", 0, (_p("Hidden", True),))
    doc.getTextFields().refresh()
    for _ in range(3):
        idx = doc.getDocumentIndexes()
        for k in range(idx.getCount()):
            idx.getByIndex(k).update()
        doc.refresh()
    doc.storeToURL(uno.systemPathToFileUrl(out_docx), (_p("FilterName", "MS Word 2007 XML"),))
    doc.storeToURL(uno.systemPathToFileUrl(out_pdf), (_p("FilterName", "writer_pdf_Export"),))
    with open(out_pdf + ".log", "w") as fh:
        fh.write("indexes=%d\n" % doc.getDocumentIndexes().getCount())
    doc.close(True)
    desktop.terminate()


g_exportedScripts = (finalize,)
