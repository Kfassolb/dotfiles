# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from libqtile import bar, layout, qtile, widget, hook
from libqtile.config import Click, Drag, Group, Key, Match, Screen
from libqtile.lazy import lazy
from libqtile.utils import guess_terminal
import os #PARA QUE FUNCIONE EL AUTOSTART LINEA 230
import subprocess
import re

import psutil

mod = "mod4"
# terminal = guess_terminal()

keys = [
    # A list of available commands that can be bound to keys can be found
    # at https://docs.qtile.org/en/latest/manual/config/lazy.html
    # Switch between windows
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    Key([mod, "shift"], "h", lazy.layout.swap_left(), desc="Move window to the left"),
    Key([mod, "shift"], "l", lazy.layout.swap_right(), desc="Move window to the right"),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows. If current window is on the edge of screen and direction
    # will be to screen edge - window would shrink.
    
    Key([mod], "i", lazy.layout.grow(), desc = "Grow window size"),
    Key([mod], "m", lazy.layout.shrink(), desc = "shrink window size"),
    Key([mod], "n", lazy.layout.reset(), desc = "reset window size"), 
    Key([mod], "o", lazy.layout.maximize(), desc = "Maximize window size"),

    Key([mod, "shift"], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    Key(
        [mod, "shift"],
        "Return",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    Key([mod], "Return", lazy.spawn("kitty"), desc="Launch terminal"),
    # Toggle between different layouts as defined below
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    Key([mod], "w", lazy.window.kill(), desc="Kill focused window"),
    Key(
        [mod],
        "f",
        lazy.window.toggle_fullscreen(),
        desc="Toggle fullscreen on the focused window",
    ),
    Key([mod], "t", lazy.window.toggle_floating(), desc="Toggle floating on the focused window"),
    Key([mod, "control"], "r", lazy.reload_config(), desc="Reload the config"),
    Key([mod, "control"], "q", lazy.shutdown(), desc="Shutdown Qtile"),
    Key([mod], "r", lazy.spawn("bash /home/kfasso/.config/rofi/launchers/type-1/launcher.sh"), desc="Spawn a command using a prompt widget"),
        
    # ------------ Hardware Configs ------------

    # Volume
    Key([], "XF86AudioLowerVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%")),
    Key([], "XF86AudioRaiseVolume", lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5%")),
    Key([], "XF86AudioMute", lazy.spawn("pactl set-sink-mute @DEFAULT_SINK@ toggle")),

    # Brightness
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set +10%")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 10%-")),

        # Screenshot
    Key([mod], "s", lazy.spawn("scrot 'screenshot_%Y-%m-%d-%T_$wx$h.png' -e 'mv $f ~/Imágenes/Screenshots/'")),
    Key([mod, "shift"], "s", lazy.spawn("scrot -s 'screenshot_%Y-%m-%d-%T_$wx$h.png' -e 'mv $f ~/Imágenes/Screenshots/'")),
]

# Add key bindings to switch VTs in Wayland.
# We can't check qtile.core.name in default config as it is loaded before qtile is started
# We therefore defer the check until the key binding is run by using .when(func=...)
for vt in range(1, 8):
    keys.append(
        Key(
            ["control", "mod1"],
            f"f{vt}",
            lazy.core.change_vt(vt).when(func=lambda: qtile.core.name == "wayland"),
            desc=f"Switch to VT{vt}",
        )
    )


__groups = {
    1: Group("󰈹", matches=[Match(wm_class=re.compile(r"^(brave\-browser)$"))]),
    2: Group("", matches=[Match(wm_class=re.compile(r"^(kitty)$"))]),
    3: Group("󰨞", matches=[Match(wm_class=re.compile(r"^(code)$"))]),
    4: Group("󱚌"),   
    5: Group("", matches=[Match(wm_class=re.compile(r"^(nautilus)$"))]),
    6: Group("", matches=[Match(wm_class=re.compile(r"^(spotify)$"))]),
}
groups = [__groups[i] for i in __groups]


def get_group_key(name):
    return [k for k, g in __groups.items() if g.name == name][0]  #Toma el primer valor de la lista de valores a retornar (si se retornara una lista de valores, también creo que es para que no recorra todo el bucle y entregue el primer valor encontrado)


for i in groups:
    keys.extend([
        # mod1 + letter of group = switch to group
        Key([mod], str(get_group_key(i.name)), lazy.group[i.name].toscreen(),
            desc="Switch to group {}".format(i.name)),

        # mod1+shift+letter of group = switch to & move focused window to group
        Key([mod, "shift"], str(get_group_key(i.name)),
            lazy.window.togroup(i.name, switch_group=True),
            desc="Switch to & move focused window to group {}".format(i.name)),
        # Or, use below if you prefer not to switch to that group.
        # # mod1 + shift + letter of group = move focused window to group
        # Key([mod, "shift"], i.name, lazy.window.togroup(i.name),
        #     desc="move focused window to group {}".format(i.name)),
    ])

#Colors
color = {
    "grey": "#37383b",
    "dark": "#1a1826",
    "light": "#f1ffff",
    "blue": "#66818d",
    "transparent":"#00000000",
}



layouts = [
    layout.MonadTall(
        margin=8,
        border_focus = "#154c79"
    ),
    layout.Max(),
    # Try more layouts by unleashing below layouts.
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.MonadTall(),
    # layout.MonadWide(),
    # layout.RatioTile(),
    # layout.Tile(),
    ]

widget_defaults = dict(
        font = "Hack Nerd Font",
        fontsize = 12,
        padding = 3,
)
extension_defaults = widget_defaults.copy()

def icon(fg=color["light"], bg=color["transparent"], textFontSize=30, iconText="?", paddingValue=0):
    return widget.TextBox(
        foreground=fg,
        background=bg,
        fontsize=textFontSize,
        text=iconText,
        padding=paddingValue,
    )

def get_widgets(primary=False):
    widgets = [
        widget.Spacer(
            length=3,
            background="#00000000",
            ),
        widget.TextBox(
            text=" ",
            foreground=color["dark"],
            background="#00000000",
            #decorations = [
            #BorderDecoration (
            #    border_width = [8, 0, 8, 0],
            #    colour=colors['dark']
            #) 
        #],
            fontsize=17,
            mouse_callbacks={"Button1": lazy.spawn(".config/rofi/launchers/type-1/launcher.sh"), "Button3": lazy.spawn(".config/rofi/powermenu/type-2/powermenu.sh")}
        ), 
        icon(iconText="",fg=color["dark"]),
        widget.GroupBox(
            highlight_method="text",
            background=color["dark"],
            highlight_color=[color["light"], color["light"]],
            inactive=color["grey"],
            fontsize=16,
            ),
        icon(iconText="",fg=color["dark"]),

        widget.WindowName(
            fontsize=12,
            foreground=color["light"]
            ),

        icon(iconText="",fg=color["blue"]),
        widget.Volume(
            fmt="墳 {}",
            foreground=color["light"],
            background=color["blue"],
            ),
        icon(iconText="",fg=color["blue"]),

        icon(iconText="",fg=color["dark"]),
        widget.CPU(
            format="󰍛 {load_percent:04}%",
            foreground=color["light"],
            background=color["dark"],
            ),
        widget.Memory(
            format="{MemUsed: .0f}{mm}",
            measure_mem='G',
            foreground=color["light"],
            background=color["dark"],
            ),
        icon(iconText="",fg=color["dark"]),

        icon(iconText="",fg=color["blue"]),
        widget.Net(
            format=" {total}{total_suffix}",
            foreground=color["light"],
            background=color["blue"],
            ),
        icon(iconText="",fg=color["blue"]),

        icon(iconText="",fg=color["blue"]),
        widget.Battery(
            format="󰁹{char}{percent:2.0%}",
            foreground=color["light"],
            background=color["blue"],
            ),
        icon(iconText="",fg=color["blue"]),

        icon(iconText="",fg=color["dark"]),
        widget.Clock(
            format=" %H:%M %d/%m/%y",
            foreground=color["light"],
            background=color["dark"],
            ),
        icon(iconText="",fg=color["dark"]),
            ]
    if primary:
        widgets.insert(10, widget.Systray())
    return widgets

xrandr = "xrandr | grep -w 'connected' | cut -d ' ' -f 2 | wc -l"

command = subprocess.run(
    xrandr,
    shell=True,
    stdout=subprocess.PIPE,
    )

connected_monitors = int(command.stdout.decode("UTF-8"))

screens = list()  #inicializamos lista de monitores

# Se crearan cant barras según cant de monitores conectados
for i in range(connected_monitors):
    screens.append(
        Screen(
            top=bar.Bar(
                get_widgets(primary=False),
                22,
                background="#00000000",
                margin = [8,5,2,5],
            ),
        ),
    )


# Drag floating layouts.
mouse = [
    Drag([mod], "Button1", lazy.window.set_position_floating(), start=lazy.window.get_position()),
    Drag([mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
    ]
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None

# xcursor theme (string or None) and size (integer) for Wayland backend
wl_xcursor_theme = None
wl_xcursor_size = 24

# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"

autostart = [
        "nitrogen --restore &",
        "picom &",
]

for x in autostart:
    os.system(x)
