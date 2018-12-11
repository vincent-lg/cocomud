REM This file prepares the folder in which CocoMUD runs and store logs

if not exist "%BASE_PATH%\client" (
    echo "%BASE_PATH%\client not found; creating it..."
    mkdir "%BASE_PATH%\client"

    echo "Copying translations ..."
    mkdir "%BASE_PATH%\client\translations\""
    xcopy "%BASE_PATH%\src\translations" "%BASE_PATH%\client\translations\" /e

    echo ""
    echo "Adding default configuration ..."
    mkdir %BASE_PATH%\client\settings\
    copy %BASE_PATH%\settings\options.conf %BASE_PATH%\client\settings\

    echo "Creating the forlder for worlds..."
    mkdir %BASE_PATH%\client\worlds
)
