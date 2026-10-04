import pathlib

path = pathlib.Path("plot_fit_views.py")
text = path.read_text(encoding="utf-8")
text = text.replace(
    'def draw_view(viewport, points, colour, shift, radius=1):\n    x0, x1, y0, y1, axis = viewport\n    width, height = 760, 620',
    'def draw_view(draw, viewport, points, colour, shift, radius=1):\n    x0, x1, y0, y1, axis = viewport\n    width, height = 760, 620')
text = text.replace('draw_view(viewport, head, (235, 235, 235), (0, 0, 0))',
                    'draw_view(draw, viewport, head, (235, 235, 235), (0, 0, 0))')
text = text.replace('draw_view(viewport, points, colour, anchor, radius=1)',
                    'draw_view(draw, viewport, points, colour, anchor, radius=1)')
path.write_text(text, encoding="utf-8")
print("patched")
