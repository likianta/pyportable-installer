E:\programs\microsoft_visual_studio\build_tools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe /c /nologo /Ox /W3 /GL /DNDEBUG /MD -IE:\programs\python\Python39\include -IE:\programs\python\Python39\include -IE:\programs\microsoft_visual_studio\build_tools\VC\Tools\MSVC\14.29.30133\include -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\ucrt -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\shared -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\um -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\winrt -IC:\Program Files (x86)\Windows Kits\10\include\10.0.19041.0\cppwinrt /Tc%3\%1.c /Fo%4\%1.obj
E:\programs\microsoft_visual_studio\build_tools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\link.exe /nologo /INCREMENTAL:NO /LTCG /DLL /MANIFEST:EMBED,ID=2 /MANIFESTUAC:NO /LIBPATH:E:\programs\python\Python39\libs /LIBPATH:E:\programs\python\Python39\PCbuild\amd64 /LIBPATH:E:\programs\microsoft_visual_studio\build_tools\VC\Tools\MSVC\14.29.30133\lib\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.19041.0\ucrt\x64 /LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.19041.0\um\x64 /EXPORT:PyInit_%2 %4\%1.obj /OUT:%5\%2 /IMPLIB:%4\%1.lib

@REM %1 src_name
@REM %2 dst_name
@REM %3 src_dir
@REM %4 tmp_dir
@REM %5 dst_dir
