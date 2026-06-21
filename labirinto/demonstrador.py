import argparse
import os
import subprocess

imagesDirectory = "./video/ exemplo" # localização das fotos do mapa
outputName = "./video/A3sistemas"

command = f"ffmpeg -framerate 30 -pattern_type glob -i'{imagesDirectory}*.peg' -c:v libx264 -pix_fmt yuv420p {outputName}.mp4"
subprocess.call(command, shell= True)

# uso não recomendado, limitado a apenas a videos com resoluções especificas divisiveis por 10, melho usar um editor de videos normal.
# esqueci de mencionar mas o algoritmo basicamente gera um monte de fotos de cada etapa do proscesso