from matplotlib.patches import Rectangle, Circle, Arc, Polygon
from matplotlib.colors import to_hex
from pylatexenc.latexwalker import LatexWalker
from pylatexenc.latex2text import LatexNodes2Text
from IPython.display import HTML, display
import re
import random

class SvgImage:
    def __init__(self, defs = None, style = None, rich_snips = False):
        self._defs = defs
        self._style = style
        self._rich_snips = rich_snips
        self._facecolor = 'white'
        self._content = {}
        self._size_w = None
        self._size_h = None
        self._class_name = None

        self._id = 'qc' + str(random.randint(1, 2 ** 30))

    def set_facecolor(self, facecolor):
        self._facecolor = facecolor

    def get_facecolor(self):
        return self._facecolor

    def set_size_inches(self, w, h):
        pass

    def set_class_name(self, class_name):
        self._class_name = class_name

    def get_content(self):
        prefix = '<svg id="{id}" width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">\n'.format(
            id = self._id,
            w = self._size_w,
            h = self._size_h,
        )

        prefix = prefix + '<style>\n'
        prefix = prefix + 'svg { font-family: Trebuchet MS,sans-serif; background-color: #ffffff; }\n'
        prefix = prefix + 'tspan.superscript { baseline-shift: super; font-size: 0.7em; }\n'
        prefix = prefix + 'tspan.subscript { baseline-shift: sub; font-size: 0.7em; }\n'
        prefix = prefix + 'tspan.initial-state { font-family: monospace; letter-spacing: -0.1em; }\n'
        prefix = prefix + '.hidden { visibility: hidden; }\n'
        prefix = prefix + '.snip-icon { cursor: pointer; }\n'
        prefix = prefix + 'foreignObject svg { width: 100% !important; height: 100% !important; }\n'
        prefix = prefix + '</style>\n'
        
        if self._style is not None:
            prefix = prefix + '<style>\n'
            for selector in self._style:
                prefix = prefix + 'svg#' + self._id + ' ' + selector + '{' + '; '.join('{}: {}'.format(key, value) for key, value in self._style[selector].items()) + '}\n'
            prefix = prefix + '</style>\n'
        if self._rich_snips:
            prefix = prefix + """
            <script>
            var prev = null;
            function f(src, id) {
                snips = document.querySelectorAll('foreignObject');
                snips.forEach((snip) => {
                    if(!snip.classList.contains('hidden')) {
                        snip.classList.add('hidden');
                    }
                });
                if(prev != src) {
                    const regex = /translate\(([.0-9]+),([.0-9]+)\)/g;
                    const matches = Array.from(src.getAttribute('transform').matchAll(regex));
                    elm = document.getElementById(id);
                    elm.classList.toggle('hidden');

                    svgWidth = src.closest('svg').getAttribute('width');
                    x = parseFloat(matches[0][1]);
                    xPlusWidth = x + 0.6 * elm.getBBox().width;
                    if(xPlusWidth > svgWidth) {
                        x = x - (xPlusWidth - svgWidth);
                    }
                    elm.setAttribute('transform', 'translate(' + x + ',' + matches[0][2] + ') scale(0.6)');
                    prev = src;  
                } else {
                    prev = null;  
                } 
            }
            </script>
            """

        if self._defs:
            prefix = prefix + '<defs>' + '\n'.join(self._defs) + '</defs>\n'

        suffix = '</svg>'

        all_content = '<g>\n'
        for key in sorted(self._content):
            all_content = all_content + self._content[key]
        all_content = all_content + '</g>\n'
        
        return prefix + all_content + suffix

    def savefig(self, filename, dpi):
        with open(filename, 'w') as file:
            file.write(self.get_content())

    def axis(self, param1):
        pass

    def set_xlim(self, xl, xr):
        self._size_w = 45 * (xr - xl + 1)

    def set_ylim(self, yb, yt):
        self._size_h = 45 * (yt - yb + 1)

    def set_aspect(self, param1):
        pass

    def tick_params(self, labelbottom=False, labeltop=False, labelleft=False, labelright=False):
        pass

    def plot(self, x, y, **kwargs):
        # kwargs: linewidth ? 
        
        element = '<line class="{class_names}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" {stroke_dasharray} />'.format(
            x1 = self._calc_x(x[0]),
            y1 = self._calc_y(y[0]),
            x2 = self._calc_x(x[1]),
            y2 = self._calc_y(y[1]),
            stroke = kwargs['color'],
            stroke_dasharray = 'stroke-dasharray="4 1"' if 'linestyle' in kwargs and kwargs['linestyle'] == 'dashed' else '',
            class_names = ' '.join(kwargs['class_names']),
        )
        self._add_content(kwargs['zorder'], element)

    def add_patch(self, p, class_names = [], snips = []):
        if type(p) == Rectangle:
            element = '<rect class="{class_names}" x="{x}" y="{y}" width="{width}" height="{height}" fill="{fc}" stroke-width="{stroke_width}"{opacity} />'.format(
                x = self._calc_x(p.xy[0]),
                y = self._calc_y(p.xy[1] + p.get_height()),
                width = 45 * p.get_width(),
                height = 45 * p.get_height(),
                fc = to_hex(p.get_fc()),
                stroke_width = p.get_linewidth(),
                class_names = ' '.join(class_names),
                opacity = '' if p.get_alpha() is None else ' opacity="' + str(p.get_alpha()) + '"',
            )
        elif type(p) == Circle:
            element = '<circle class="{class_names}" cx="{cx}" cy="{cy}" r="{r}" fill="{fc}" stroke="{ec}" stroke-width="2" />'.format(
                cx = self._calc_x(p.center[0]),
                cy = self._calc_y(p.center[1]),
                r = 45 * p.get_radius(),
                fc = to_hex(p.get_fc()),
                ec = to_hex(p.get_ec()),
                class_names = ' '.join(class_names),
            )
        elif type(p) == Arc:
            element = '<path class="{class_names}" d="M {x_s} {y} A {rx} {ry} 0 0 1 {x_e} {y}" fill="transparent" stroke="{stroke}" stroke-width="{stroke_width}" />'.format(
                x_s = -10 + self._calc_x(p.get_center()[0]),
                x_e = 10 + self._calc_x(p.get_center()[0]),
                y = self._calc_y(p.get_center()[1]),
                rx = 45 * p.get_width() / 2,
                ry = 45 * p.get_height() / 2,
                stroke = to_hex(p.get_ec()),
                stroke_width = p.get_linewidth(),
                class_names = ' '.join(class_names),
            )
        elif type(p) == Polygon:
            points = ''
            for point in p.get_xy():
                points = points + str(self._calc_x(point[0])) + ',' + str(self._calc_y(point[1])) + ' '
            element = '<polygon class="{class_names}" points="{points}" fill="{fc}" />'.format(
                points = points,
                fc = to_hex(p.get_fc()),
                class_names = ' '.join(class_names),
            )
        
        self._add_content(p.zorder, element)

        for snip in snips:
                if snip['type'] == 'decomposition':
                    icon = '<g transform="translate(1,-12)" stroke-width="1"><rect x="0.5" y="0.5" width="4.5" height="4.5" /><rect x="0.5" y="6.5" width="4.5" height="4.5" /><rect x="6.5" y="0.5" width="4.5" height="4.5" /><rect x="6.5" y="6.5" width="4.5" height="4.5" /></g>'
                elif snip['type'] == 'calibration':
                    icon = '<g transform="translate(-8,8) scale(0.011,-0.011)"><path d="M934 1806 c-71 -32 -145 -137 -200 -283 -27 -71 -84 -285 -84 -315 0 -16 11 -18 85 -18 60 0 87 4 89 13 2 6 18 72 35 146 36 148 69 232 108 274 78 81 142 -21 228 -366 29 -116 65 -243 79 -282 34 -89 91 -172 145 -210 38 -27 51 -30 116 -30 65 0 78 3 117 30 53 37 114 127 157 228 27 67 78 244 94 335 l7 32 -89 0 -88 0 -17 -82 c-42 -203 -107 -357 -155 -373 -73 -23 -126 82 -206 411 -71 289 -125 407 -217 470 -33 23 -53 29 -107 31 -41 2 -78 -2 -97 -11z"/></g>'
                
                element = '<g class="snip-icon" transform="translate({x},{y})" fill="{fc}" onclick="f(this, \'{type}-{name}\')"><rect x="0" y="-12" width="12" height="12" fill="transparent" />{icon}</g>'.format(
                    x = self._calc_x(p.xy[0] + p.get_width()) - 12,
                    y = self._calc_y(p.xy[1] + p.get_height()),
                    fc = to_hex(p.get_fc()),
                    type = snip['type'],
                    name = snip['name'],
                    icon = icon,
                )
                self._add_content(p.zorder, element)

    def text(self, x, y, str, **kwargs):
        # kwargs: clip_on ?
        ha = kwargs['ha'] if 'ha' in kwargs else 'start' 
        if ha == 'left':
            ha = 'start'
        elif ha == 'center':
            ha = 'middle'
        elif ha == 'right':
            ha = 'end'

        va = kwargs['va'] if 'va' in kwargs else 'middle' 
        if va == 'center':
            va = 'middle'

        fontsize = round(kwargs['fontsize'] / 14, 4) if 'fontsize' in kwargs else 0.7

        zorder = kwargs['zorder'] if 'zorder' in kwargs else 1

        str = str.replace('\mathrm', '')
        str = str.replace('\dagger', '†')

        # TODO: This code does not work with reset instructions
        lw_obj = LatexWalker(str)
        # parse to node list
        nodelist, pos, length = lw_obj.get_latex_nodes()
        # initialize the converter to text
        l2t_obj = LatexNodes2Text()
        # convert to text
        str = l2t_obj.nodelist_to_text(nodelist)

        result = re.findall("^([^_]+)_([^_ ]+)(.*)$", str)
        if len(result) == 1 and len(result[0]) == 3:
            str = result[0][0] + '<tspan class="subscript">' + result[0][1] + '</tspan>'
            if result[0][2] != '':
                if re.match("|[^>]+>", result[0][2]):
                    initial_state = result[0][2].replace('>', '〉')
                    str = str + '<tspan class="initial-state">' + initial_state + '</tspan>'
                else:
                    str = str + result[0][2]

        #result = re.findall("^([^_]+)_([^_]+)$", str)
        #if len(result) == 1 and len(result[0]) == 2:
        #    str = result[0][0] + '<tspan dy="5">' + result[0][1] + '</tspan>'

        result = re.findall("^([^\^]+)\^([^\^]+)$", str)
        if len(result) == 1 and len(result[0]) == 2:
            str = result[0][0] + '<tspan class="superscript">' + result[0][1] + '</tspan>'

        element = '<text class="{class_names}" x="{x}" y="{y}" font-size="{fontsize}em" {fill} dominant-baseline="{va}" text-anchor="{ha}">{str}</text>'.format(
            x = self._calc_x(x),
            y = self._calc_y(y),
            str = str,
            fontsize = fontsize,
            fill = ('fill="' + kwargs['color'] + '"') if 'color' in kwargs else '',
            va = va,
            ha = ha,
            class_names = ' '.join(kwargs['class_names']),
        )
        self._add_content(zorder, element)

    def embed(self, id, svg_str, width, height):
        index = svg_str.index(b'<svg')
        svg_str = svg_str[index:]

        match = re.search(b'<svg[^>]*>', svg_str, re.MULTILINE)
        if match:
            svg_str = svg_str.replace(
                match.group(),
                match.group() + b'\n<rect x="0" y="0" width="100%" height="100%" fill="#ffffdd" />'
            )

        element = '<foreignObject id="{id}" class="snip hidden" transform="scale(0.6)" x="0" y="12" width="{width}" height="{height}" stroke="orange" stroke-width="2">\n{svg_str}\n</foreignObject>'.format(
            id = id,
            svg_str = svg_str.decode("utf-8"),
            width = width,
            height = height,
        )
        self._add_content(100, element)

    def draw(self):
        return HTML(self.get_content())

    
    def _add_content(self, zorder, element):
        if zorder not in self._content:
            self._content[zorder] = ''
        self._content[zorder] = self._content[zorder] + element + '\n'

    def _calc_x(self, x):
        return round(45 * (2 + x), 4)

    def _calc_y(self, y):
        return round(45 * (1 - y), 4)