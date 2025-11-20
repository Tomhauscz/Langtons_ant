@echo off

echo Cleaning build folder ...
rmdir /s /q build

echo Building project ...
python setup.py build


if exist "build\exe.win-amd64-3.13" (
    echo Creating project package ZIP archive
    powershell -Command "Compress-Archive -Path 'build\exe.win-amd64-3.13\*' -DestinationPath 'LangtonsAnt.zip'"
    echo Project package copied and zipped
) else (
    echo Could not create ZIP archive. Project build folder not found!
)

