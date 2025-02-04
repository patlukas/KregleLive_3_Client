import os
from datetime import datetime
APP_VERSION = os.getenv('NEW_VERSION_WITH_BUILD')
now = datetime.now()
BUILD_DATE = (now.year, now.month, now.day, now.hour, now.minute)
APP_VERSION_COMMA = APP_VERSION.replace(".", ",")
YEAR = now.year

version_info = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({APP_VERSION_COMMA}),
    prodvers=({APP_VERSION_COMMA}),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date={BUILD_DATE} 
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '041504b0', 
        [
          StringStruct('CompanyName', 'Patlukas'),
          StringStruct('FileDescription', 'Kręgle Live 3 - Client'),
          StringStruct('FileVersion', '{APP_VERSION}'),
          StringStruct('InternalName', 'KL3C.exe'),
          StringStruct('LegalCopyright', 'Copyright (C) {YEAR} Patlukas'),
          StringStruct('OriginalFilename', 'KL3C.exe'),
          StringStruct('ProductName', 'KręgleLive3-Client'),
          StringStruct('ProductVersion', '{APP_VERSION}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [0x0415, 1200])])
  ]
)"""

with open("version.py", "w", encoding="utf-8") as f:
    f.write(version_info)

print("Generated version.py with version: ", APP_VERSION, " | Date: ", BUILD_DATE)