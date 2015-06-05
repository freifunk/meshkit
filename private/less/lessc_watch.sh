#!/bin/bash                                                                     
# Detect changes in all .less files in this directory and automatically compile
# into .css

SOURCE="./main.less"
OUTPUT="../../static/css/main.css"
FONTPATH='"../fonts"'

inotifywait . -m -r -e close_write | while read x op f; do   
    ext=${f##*.}

    if [ "$ext" = "less" ]; then                                                
        echo "Change detected. Recompiling...";                                    
        lessc --verbose --global-var="fontPath=$FONTPATH" "$SOURCE" > "$OUTPUT" && echo "`date`: COMPILED";                                                                                                                           
    fi                                                                             
done 

