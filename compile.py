
import pathlib
import re
from zipfile import ZipFile
import shutil

FLAGS = {
         "NONE" : ("(^[\t ]*)# end", lambda s : s), # No aplica ninguna operacion a la línea
         "COMMENT" : ("(^[\t ]*)# begin remove", lambda s : "#" + s), # comenta lineas entre un begin remove y un end
         "REPLACE_IMPORT" : ("(^[\t ]*)# begin local import", lambda s : re.sub(r'(^.*)import', r'\1from . import', s)) # reemplaza imports de ficheros locales añadiendo la orden from . import modulo
        }

modules = ["archibuilder.zip", "filemanager.zip", "robotcontrol.zip", "utilities.zip"]

# Procesado de las etiquetas del código
def process_file(file, result):
    current_flag = FLAGS["NONE"]
    
    result_file = result / file
    
    result_file.parent.mkdir(parents=True, exist_ok=True)

    input_fid=open(file, "r", encoding="utf-8")
    output_fid=open(result_file, "w", encoding="utf-8")

    for line in input_fid:
        found_list = [v for k, v in FLAGS.items() if re.compile(v[0]).search(line) is not None]

        if len(found_list) > 0:
            current_flag = found_list[0]
        else:
            line_proc = current_flag[1](line)
            output_fid.write(line_proc)

    input_fid.close()
    output_fid.close()

# Comprime resultado en ZIP
def compress(outfolder):
    for folder in outfolder.iterdir():
        if folder.is_dir():
            zname = pathlib.Path(folder.name + '.zip')
            zfid = ZipFile(zname, 'w')
            for file in folder.iterdir():
                if file.is_file():
                    zfid.write(file, arcname=pathlib.Path(file.parent.name) / pathlib.Path(file.name))
            zfid.close()
            shutil.move(zname, outfolder / zname)

if __name__ == "__main__":
    is_empty = lambda f : len(list(f.iterdir())) == 0
    
    source_folder = pathlib.Path(".")
    result_folder = source_folder / pathlib.Path("releases")
    
    if result_folder.is_dir() and not is_empty(result_folder):
        print("[ERROR] Release folder is not empty")
        exit()
    
    # Procesado del codigo fuente
    for folder in source_folder.iterdir():
        if folder.is_dir():
            if folder.name == result_folder.name:
                continue
            
            for file in folder.iterdir():
                try:
                    process_file(file, result_folder)
                except Exception as e:
                    print(e)
    
    compress(result_folder)

    # Remove temporal code
    for fd in result_folder.iterdir():
        if fd.is_dir():
            shutil.rmtree(fd)
        
        if fd.is_file() and fd.name not in modules:
            fd.unlink()
