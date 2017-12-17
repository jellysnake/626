#!/usr/bin/env python
import os
import json
import webbrowser

import click
from PIL import Image

with open("data/dmc.json") as w:
    DMC = json.load(w)

def rotate(im):
    """Given our pixel walking uses inverted axes, rotate now."""
    return im.transpose(Image.FLIP_TOP_BOTTOM).transpose(Image.ROTATE_270)


def recolor(oldimage, palettename, colorlimit):
    """Given a Pillow Image, a pallette, and a colour limit; re-color"""
    palettedata = sum([x['RGB'] for x in DMC], [])[:256] ## NOTE Pillow Limitation

    palimage = Image.new('P', (16, 16))
    palimage.putpalette(palettedata)

    oldimage = oldimage.convert('P', palette=Image.ADAPTIVE, colors=colorlimit)
    oldimage = oldimage.convert('RGB')

    newimage = oldimage.im.convert('P', 0, palimage.im)
    im = oldimage._new(newimage)

    return im.convert('RGB')


def rgb2hex(pix):
    """Given a tuple of r, g, b, return the hex value """
    r, g, b = pix
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


def thread_name(rgb, palette):
    """Given an RGB and a palette; return the thread name and code"""
    for x in DMC:
        if tuple(x['RGB']) == rgb:
            return (x['ColorName'], x[palette])
    else:
        return (str(rgb), '??')


def rescale(im, scale):
    """Given an image and a scale factor; reduce the image"""
    h = int(im.height / scale)
    w = int(im.width / scale)

    return im.resize((w, h)) # Image.ANTIALIAS)


def chart(im, palette):
    """Given that image, do the html thang"""
    histo = sorted(im.getcolors())

    legend = {}
    html = ["<html>"]

    with open("styling.css") as s:
        html.append("<style>" + "".join(s.readlines()) + "</style>")

    stars = '◼✤✷✽❤✰❐❄➤⬆⬇♠♣♥♦♞♟✚⚑⚉✔❦✭⌬'
    for idx, x in enumerate(histo):
        h = rgb2hex(x[1])
        legend[h] = stars[idx % len(stars)]

    html.append('<table><tr><td class="zztop"><table class="legend">')
    html.append('<tr><td>X</td><td># sts</td><td>{} code</td><td>{} name</td></tr>'.format(palette, palette))

    for idx, h in enumerate(reversed(histo)):
        count, rgb = h
        color = rgb2hex(rgb)
        name, code = thread_name(rgb, palette)
        
        html.append('<tr>' +color_cell(rgb, legend[color]) + '<td>{}</td><td>{}</td><td>{}</td><tr>'.format(count, code, name))

    html.append('</table><br>Image width: {}<br>Image height: {}<br><br>Generated by Experiment 626 ✨'
        .format(im.width, im.height))
    html.append('</td><td class="zztop space"><table class="chart">')

    CENTER = True
    for x in range(0, im.width):
        row = []
        for y in range(0, im.height):
            rgb = im.getpixel((x,y))
            p = rgb2hex(rgb)
            
            hardborder = False ## Center point
            if CENTER:
                if im.height / 2 <= y and im.width / 2 <= x:
                    CENTER = False 
                    hardborder = True

            row.append(color_cell(rgb, legend[p], hardborder=hardborder))

        html.append("".join(row) + "</tr>")
    html.append("</table></td></table></html>")
    return "\n".join(html)


def color_cell(rgb, icon, hardborder=False):
    """Given a colour and an icon; return a coloured table cell"""
    p = rgb2hex(rgb)
    if (rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114) > 186:
        text = "color: black"
    else:
        text = "color: lightgray"

    if hardborder:
        text += "; border: 4px solid red;"

    return "<td style='{}; background-color: {}'>{}</td>".format(text, p, icon)


@click.command()
@click.argument('image')
@click.option('--palette', '-p', default="wool", help='Choices: wool, floss. Default: wool')
@click.option('--scale', '-s', default=1, help='Rescale factor. Default: 1')
@click.option('--colours', '-c', default=256, help='Limit palette to N colors. Default: 256')
@click.option('--no-open', '-n', is_flag=True, default=False, help="Don't auto-open result file")
def generate_chart(image, palette, scale, colours, no_open):
    """Given a image filename, and optional parameters; generate a chart"""
    im = Image.open(image)

    im = rescale(im, scale)
    im = recolor(im, palette, colours)
    im = rotate(im) 
    chart_page = chart(im, palette)

    outfile = 'output/{}.html'.format("_".join(image.split("/")[-1].split(".")[:-1]))

    with open(outfile, 'w') as f:
        f.write(chart_page)
    
    if no_open:
        print("Result file: {}".format(outfile))
    else:
        webbrowser.open('file://' + os.path.realpath(outfile))
    

if __name__ == '__main__':
    generate_chart()
