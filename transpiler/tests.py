
class Container:
    default_properties = {
        "id": "",
        "color": "red",
        "draw_hide": "default draw_hide",
        "shape": "default shape",
        "height": "default height",
        "event_listeners": [],
        "children": [],
        "position_xy": [20, 20],
    }
assert "children" in Container.default_properties.keys