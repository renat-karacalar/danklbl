# danklbl

small python cli tool to convert DHL-Labels into a single pdf file into the dimensions 6"x4" for a label printer

When started without arguments the zip folder is checked for zip-archives. The content (pdf files) of identified 
zip-archives is extracted into the tmp folder. The pdf files are then cropped, rotated and the merged into
a single file which is designed for 4"x6" label printer.