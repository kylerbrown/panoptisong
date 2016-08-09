import urwid
import sys
import os
from os.path import isfile, join
import re
import subprocess
from time import sleep

from collections import OrderedDict, defaultdict


HINTS = defaultdict(lambda: "", {
        'recordings': 'Directory in which recording files are saved.',
        'backup_location': 'Directory to which files can be copied at reset_time (can be remote.)',
        'servername': 'jack server name - should not matter.',
        'jackdparams': '''-r is sampling rate, -p is frames per period
If you get an error running jack, maybe you need to change the hw:x parameter, find the right soundcard using aplay -l.'''
    })


BIRD_VALS = ('name', 'box', 'experimenter', 'channel')

RECORD_SCRIPT = './panoptisong'

record_at_exit = False

class Info():
    def __init__(self, params, birds):
        self.params = params
        self.birds = birds


    def to_string(info):
        params, birds = info
        parts = []
        parts.append('#!/bin/bash')
        parts.append('######## global variables ########')
        for (key, value) in params.items():
            parts.append('{0}="{1}"'.format(key, value))

        params_string = "\n".join(parts)
        params_string = params_string + '\n' # Newline at the end for consistency
        parts = []
        parts.append('# NAME\tBOX\tCHANNEL')
        for vals in birds:
            parts.append('\t'.join(vals))
        birds_string = '\n'.join(parts)
        birds_string = birds_string + '\n' # Newline at the end for consistency
        return (params_string, birds_string)

    def write_to_file(info, prefix='<default>'):
        params_str, birds_str = Info.to_string(info)
        if prefix == '<default>':
            prefix = sys.path[0]+'/' #opening the default file
        else:
            prefix = sys.path[0]+'/'+prefix+'_' #adding script directory
        with open(prefix+'parameters', 'w+') as params_file,\
                open(prefix+'birds', 'w+') as birds_file:
            params_file.write(params_str)
            birds_file.write(birds_str)

    def list_prefixes():
        mypath = sys.path[0]
        filenames = [f for f in os.listdir(mypath) if isfile(join(mypath, f))]
        # Gets only files in the script directory
        pattern = re.compile('(.*)_parameters')
        possible_prefixes = []
        for name in filenames:
            matched = pattern.match(name)
            if matched != None:
                possible_prefixes.append(matched.group(1))
        prefixes = [pfx for pfx in possible_prefixes 
            if pfx+"_parameters" in filenames and pfx+"_birds" in filenames]
        return prefixes


    def read_from_file(prefix='<default>'):
        if prefix == '<default>':
            prefix = sys.path[0]+'/' #opening the default file
        else:
            prefix = sys.path[0]+'/'+prefix+'_' #adding script directory
        with open(prefix+'parameters', 'r+') as params_file,\
                open(prefix+'birds', 'r+') as birds_file:
            params_lines = params_file.readlines()
            birds_lines = birds_file.readlines()

        params = OrderedDict()
        params_re = re.compile('([a-zA-Z0-9\_]*?)=\"(.*?)\"')
        for line in params_lines:
            matched = params_re.match(line)
            if matched == None:
                continue
            key = matched.group(1)
            val = matched.group(2)
            params[key] = val

        birds = []
        birds_re_string = '^' + '\t'.join(['([^#]*)']*len(BIRD_VALS))+'\n$'
        birds_re = re.compile(birds_re_string)
        # birds_re = re.compile('^([^#]*)\t(.*)\t(.*)$')
        for line in birds_lines:
            matched = birds_re.match(line)
            if matched == None:
                continue
            birds.append(matched.groups())
        return Info(params, birds)
    


class BirdsList(urwid.WidgetWrap):
    def __init__(self, name, birds_list):
        self.birds = birds_list
        self.header = urwid.Pile([urwid.Text(name),
            urwid.Columns([urwid.Text(txt) for txt in BIRD_VALS]),
            urwid.Divider()])
        # header = urwid.Columns([urwid.Text(txt) for txt in BIRD_VALS])
        body = []
        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(body)) 
        self.widget = urwid.Frame(self.listbox, header=self.header)
        for vals in self.birds:
            field = self.add_bird(vals)        
        urwid.WidgetWrap.__init__(self, self.widget)

    def add_bird(self, vals):
        field = urwid.Columns([urwid.Edit(edit_text=val) for val in vals])
        self.listbox.body.append(field)

    def remove_focused_bird(self):
        idx = self.listbox.focus_position
        # Don't touch the header
        # - delete only if focused on one of the bird entries
        if isinstance(self.listbox.body[idx], urwid.container.Columns):
            del self.listbox.body[idx]

    def keypress(self, size, key):
        if key == "ctrl n":
            self.add_bird(BIRD_VALS)
        elif key == "ctrl l":
            self.remove_focused_bird()

        else:
            return super(BirdsList, self).keypress(size, key)

    def read_values(self):
        res = []
        for item in self.listbox.body:
            #item is either Column, or Text or Divider which will give errors
            try:
                vals = []
                # item.contents is a list of tuples, where Edit object
                # is the first element
                for (row, _) in item.contents:
                    vals.append(row.edit_text)
                res.append(vals)
            except:
                pass
        return res

class ParamsList(urwid.WidgetWrap):
    def __init__(self, name, params_list):
        self.params = params_list
        body = []
        for (key, val) in self.params.items():
            field_key = urwid.Text(key)
            field_val = urwid.Edit(edit_text=val)
            field = urwid.Columns([field_key, field_val])
            body.append(field)

        self.hint = urwid.Text('hint: ')
        self.walker = urwid.SimpleFocusListWalker(body)
        self.listbox = urwid.ListBox(self.walker)
        self.widget = urwid.Frame(urwid.ListBox(self.walker),
            header = urwid.Pile([urwid.Text(name), urwid.Divider()]),
            footer = urwid.Pile([urwid.Divider(), self.hint]))
        urwid.WidgetWrap.__init__(self, self.widget)


    def read_values(self):
        res = OrderedDict()
        for item in self.listbox.body:
            # item is either Column, or Text or Divider which will give errors
            try:
                # First index is over elements of the Column,
                # second because it returns a tuple with options as second element
                key = item.contents[0][0].text
                val = item.contents[1][0].edit_text
                res[key] = val
            except:
                pass
        return res

    def update_hint(self):
        self.hint.set_text('hint: '+ HINTS[self.listbox.focus.contents[0][0].text])
        
    def keypress(self, size, key):
        ret = super(ParamsList, self).keypress(size, key)
        self.update_hint()
        return ret


class ColumnEditor(urwid.WidgetWrap):
    def __init__(self, info):
        self.info = info
        self.params_col = ParamsList("PARAMETERS", self.info.params)
        self.birds_col = BirdsList("BIRDS", self.info.birds)
        self.ncols = 2
        self.widget = urwid.Pile([urwid.LineBox(self.params_col),
                            urwid.LineBox(self.birds_col)])
        urwid.WidgetWrap.__init__(self, self.widget)

    def toggle_column(self):
        self.widget.focus_position = (self.widget.focus_position+1)%self.ncols

    def keypress(self, size, key):
        if key == 'tab':
            self.toggle_column()
        else:
            return super(ColumnEditor, self).keypress(size, key)

    def read_info(self):
        params = self.params_col.read_values()
        birds = self.birds_col.read_values()
        return (params, birds)

class Saver(urwid.WidgetWrap):
    signals = ['saved']
    def __init__(self):
        caption = "SAVING\nEnter the prefix for both filenames (ctrl+k to cancel):\n\n"
        suggested = "my_config"
        self.edit = urwid.Edit(caption=caption, edit_text=suggested, align="center")
        self.widget = urwid.Filler(self.edit)
        urwid.WidgetWrap.__init__(self, self.widget)

    def set_info(self, info):
        self.info = info

    def keypress(self, size, key):
        if key == "enter":
            self.save()
        elif key == "ctrl k":
            urwid.emit_signal(self, 'saved')
        else:
            return super(Saver, self).keypress(size, key)

    def save(self, filename=None):
        if filename == None:
            filename = self.edit.edit_text
        Info.write_to_file(self.info, filename)
        urwid.emit_signal(self, 'saved')


class Runner(urwid.WidgetWrap):
    def __init__(self):
        caption = '''START RECORDING
I will start recording with currently selected parameters.
First I will kill all running jack servers.
Press ENTER to start or ctrl+k to cancel.'''
        text = urwid.Text(caption)
        button = urwid.Button(caption, self.start_recording)
        self.widget = urwid.Filler(button)
        urwid.WidgetWrap.__init__(self, self.widget)

    def keypress(self, size, key):
        if key == 'enter':
            self.start_recording()
        else:
            return super(Runner, self).keypress(size, key)

    def start_recording(self, *args):
        global record_at_exit
        record_at_exit = True
        raise urwid.ExitMainLoop()
        

class Loader(urwid.WidgetWrap):
    signals = ['loaded']
    def __init__(self):
        body = [urwid.Text('LOADING'), urwid.Divider()]
        self.widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        urwid.WidgetWrap.__init__(self, self.widget)

        prefixes = ['<default>'] + Info.list_prefixes()
        for p in prefixes:
            txt = urwid.SelectableIcon(text=p)
            self.widget.body.append(txt)

    def keypress(self, size, key):
        if key == 'enter':
            self.load()
        else:
            return super(Loader, self).keypress(size, key)

    def load(self):
        prefix = self.widget.focus.text
        self.loaded = Info.read_from_file(prefix)
        urwid.emit_signal(self, 'loaded')


class GUI(urwid.WidgetWrap):
    def __init__(self):
        self.infobox = urwid.Text('''Hello scientist!
ctrl+w to save   ctrl+e to load   ctrl+k to cancel   ctrl+x to quit   ctrl+p to record
ctrl+n to add new bird   ctrl+l to delete selected bird''')
        self.info = Info.read_from_file()
        self.editor = ColumnEditor(self.info)

        self.saver = Saver()
        self.loader = Loader()
        self.runner = Runner()
        urwid.connect_signal(self.saver, 'saved', self.show_editor)
        urwid.connect_signal(self.loader, 'loaded', self.load_data)


        self.widget = urwid.Frame(self.editor, footer=self.infobox)
        urwid.WidgetWrap.__init__(self, self.widget)

    def show_editor(self, *args):
        self.widget.body = self.editor

    def load_data(self):
        self.editor = ColumnEditor(self.loader.loaded)
        self.show_editor()


    def keypress(self, size, key):
        if key == 'ctrl w':
            self.process_save()
        elif key == 'ctrl e':
            self.process_load()
        elif key == 'ctrl k':
            self.show_editor()
        elif key == 'ctrl p':
            self.process_record()
        elif key == 'ctrl x':
            raise urwid.ExitMainLoop()
        else:
            return super(GUI, self).keypress(size, key)

    def read_info(self):
        return self.editor.read_info()

    def process_save(self):
        self.widget.body = self.overlay(self.saver, 'savebg', 100)
        self.saver.set_info(self.read_info())
        # Then saver emits the 'saved' signal

    def process_load(self):
        self.widget.body = self.overlay(self.loader, 'loadbg', 100)
        #Then loader emits the 'loaded' signal

    def process_record(self):
        self.saver.set_info(self.read_info())
        self.saver.save('_tmp') # Save config to a temp file that we will run
        self.widget.body = self.overlay(self.runner, 'runbg', 100)


    def overlay(self, widget, palette, height_percent):
        bg = urwid.AttrWrap(widget, palette)
        fill = urwid.Filler(bg, valign='middle', height=('relative', height_percent))
        overlay = urwid.Overlay(fill, self.editor,
            align = 'center', valign='middle',
            height=('relative',50), width=('relative', 50),
            top=1, bottom=1)
        return overlay


m = GUI()
loop = urwid.MainLoop(m, 
    [('savebg', 'white', 'dark blue'), ('loadbg', 'white', 'dark green'),
        ('runbg', 'white', 'dark red')])

loop.run()
if record_at_exit:
    subprocess.call('killall jackd', shell=True)
    subprocess.call('clear')
    os.execv(RECORD_SCRIPT, ('gui_recording', '_tmp'))        

