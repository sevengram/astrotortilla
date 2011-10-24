import os
filelist=[]
if ".zip" in __file__:
    import zipfile
    zip = zipfile.ZipFile(__file__[:__file__.index(".zip")+4])
    modPath = os.path.dirname(__file__[__file__.index(".zip")+5:].replace("\\", "/"))+"/"
    filelist = [f.filename for f in zip.filelist if f.filename.startswith(modPath)]
    __all__ = [ os.path.basename(f)[:-4] for f in filelist]
else:
    import glob
    filelist = glob.glob(os.path.dirname(__file__)+"/*.py")
    __all__ = [ os.path.basename(f)[:-3] for f in filelist]
