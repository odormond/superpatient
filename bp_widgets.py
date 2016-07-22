#!/usr/bin/env python
# coding:UTF-8

import Tkinter as tk
from bp_custo import labels_text, labels_font
from bp_custo import fields_font, fields_height, fields_width


def RadioWidget(parent, key, row, column, options, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=labels_text[key], font=labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    radioVar = tk.StringVar()
    if value:
        radioVar.set(value)
    frame = tk.Frame(parent)
    r1 = None
    for option in options:
        if isinstance(option, tuple):
            value, label = option
        else:
            value = label = option
        r = tk.Radiobutton(frame, text=label, variable=radioVar, value=value, font=fields_font[key], disabledforeground='black')
        if readonly:
            r.config(state=tk.DISABLED)
        r.pack(side=tk.LEFT)
        if r1 is None:
            r1 = r
    frame.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return radioVar, r1
    return radioVar


def EntryWidget(parent, key, row, column, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False, justify=tk.LEFT):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=labels_text[key], font=labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    var = tk.StringVar()
    if value:
        var.set(value)
    entry = tk.Entry(parent, textvariable=var, font=fields_font[key], fg=field_fg, disabledforeground='black', justify=justify)
    if readonly:
        entry.config(state=tk.DISABLED)
    entry.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return var, entry
    return var


def OptionWidget(parent, key, row, column, options, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black', want_widget=False):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=labels_text[key], font=labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    var = tk.StringVar()
    if value:
        var.set(value)
    dropdown = tk.OptionMenu(parent, var, *options)
    if readonly:
        dropdown.config(state=tk.DISABLED)
    dropdown.grid(row=row+rowshift, column=column+colshift, sticky=tk.W+tk.E)
    if want_widget:
        return var, dropdown
    return var


def TextWidget(parent, key, row, column, rowspan=1, columnspan=1, value=None, readonly=False, side_by_side=True, fg='black', field_fg='black'):
    if side_by_side:
        rowshift, colshift = 0, 1
    else:
        rowshift, colshift = 1, 0
    tk.Label(parent, text=labels_text[key], font=labels_font[key], fg=fg).grid(row=row, column=column, sticky=tk.W)
    frame = tk.Frame(parent)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    var = tk.Text(frame, yscrollcommand=scroll.set, relief=tk.SUNKEN, borderwidth=1, width=fields_width[key], height=fields_height[key], font=fields_font[key], wrap=tk.WORD, fg=field_fg)
    scroll.config(command=var.yview)
    var.grid(row=0, column=0, sticky=tk.NSEW)
    scroll.grid(row=0, column=1, pady=3, sticky=tk.N+tk.S)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid(row=row+rowshift, column=column+colshift, rowspan=rowspan, columnspan=columnspan, sticky=tk.NSEW)
    if value:
        var.insert(1.0, value.replace('\n\n', '\n').strip())
    if readonly:
        var['state'] = tk.DISABLED
    return var


def ListboxWidget(parent, key, row, column, rowspan=1, columnspan=2):
    frame = tk.Frame(parent)
    scroll = tk.Scrollbar(frame, orient=tk.VERTICAL)
    select = tk.Listbox(frame, yscrollcommand=scroll.set, height=fields_height[key], width=fields_width[key], font=fields_font[key])
    scroll.config(command=select.yview)
    select.grid(row=0, column=0, sticky=tk.NSEW)
    scroll.grid(row=0, column=1, pady=3, sticky=tk.N+tk.S)
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    frame.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=tk.NSEW)
    return select
