import urwid
import sys

class Info():
    def __init__(self):
        # self.dd = attrs_dict
        # if colnames == None:
        #     self.colnames = self.dd.keys()
        # else:
        #     self.colnames = colnames
        self.params = {"jackname": "lol", "room":"001"}
        # self.params = {str(i):str(i) for i in range(1000)}
        self.birds = [["k1", "1", "system:capture_1"],["k2", "2", "system:capture2"],
                            ["k3", "3", "system:capture:3"]]


    def to_string(info):
        params, birds = info
        parts = []
        parts.append('#!/bin/bash')
        parts.append('######## global variables ########')
        for (key, value) in params.items():
            parts.append('{0}="{1}"'.format(key, value))

        params_string = "\n".join(parts)
        parts = []
        parts.append('# NAME\tBOX\tCHANNEL')
        for (nm,bx,ch) in birds:
            parts.append("{0}\t{1}\t{2}".format(nm,bx,ch))
        birds_string = '\n'.join(parts)
        return (params_string, birds_string)

    def write_to_file(filename, info):
        params_str, birds_str = Info.to_string(info)
        with open(filename+'_parameters', 'w+') as params_file, open(filename+'_birds', 'w+') as birds_file:
            params_file.write(params_str)
            birds_file.write(birds_str)


    


class BirdsList(urwid.WidgetWrap):
    def __init__(self, name, birds_list):
        self.birds = birds_list
        body = [urwid.Text(name), urwid.Divider()]
        self.header_len = len(body)
        self.widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        for (name, box, channel) in self.birds:
            field = self.add_bird(name, box, channel)
            # body.append(urwid.AttrMap(field, None, focus_map='reversed'))
        
        urwid.WidgetWrap.__init__(self, self.widget)

    def add_bird(self, name, box, channel):
        field_name = urwid.Edit(edit_text=name)
        field_box = urwid.Edit(edit_text=box)
        field_channel = urwid.Edit(edit_text=channel)
        field = urwid.Columns([field_name, field_box, field_channel])
        self.widget.body.append(field)

    def remove_focused_bird(self):
        idx = self.widget.focus_position
        # Don't touch the header - delete only if focused on one of the bird entries
        if isinstance(self.widget.body[idx], urwid.container.Columns):
            del self.widget.body[idx]

    def keypress(self, size, key):
        if key == "ctrl n":
            self.add_bird("name", "box", "channel")
        elif key == "ctrl k":
            self.remove_focused_bird()
        elif key == "ctrl a":
            print(self.read_values())

        else:
            return super(BirdsList, self).keypress(size, key)

    def read_values(self):
        res = []
        for item in self.widget.body:
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
        body = [urwid.Text(name), urwid.Divider()]
        for (key, val) in self.params.items():
            field_key = urwid.Text(key)
            field_val = urwid.Edit(edit_text=val)
            field = urwid.Columns([field_key, field_val])
            body.append(field)

        self.widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        urwid.WidgetWrap.__init__(self, self.widget)

    def read_values(self):
        res = {}
        for item in self.widget.body:
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
        
    def keypress(self, size, key):
        if key == "ctrl a":
            print(self.read_values())

        else:
            return super(ParamsList, self).keypress(size, key)


class ColumnEditor(urwid.WidgetWrap):
    def __init__(self, info):
        self.info = info
        self.params_col = ParamsList("PARAMETERS", self.info.params)
        self.birds_col = BirdsList("BIRDS", self.info.birds)
        self.ncols = 2
        self.widget = urwid.Pile([self.params_col, self.birds_col])
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
        caption = "Enter the prefix for both filenames (ctrl+k to cancel):\n\n"
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

    def save(self):
        filename = self.edit.edit_text
        Info.write_to_file(filename, self.info)
        urwid.emit_signal(self, 'saved')


class GUI(urwid.WidgetWrap):
    def __init__(self):
        self.infobox = urwid.Text("hello scientist\nI like pie")
        self.info = Info()
        self.editor = ColumnEditor(self.info)

        self.saver = Saver()
        urwid.connect_signal(self.saver, 'saved', self.show_editor)


        self.widget = urwid.Frame(self.editor, footer=self.infobox)
        urwid.WidgetWrap.__init__(self, self.widget)

    def show_editor(self, *args):
        self.widget.body = self.editor



    def keypress(self, size, key):
        if key == "ctrl w":
            self.process_save()
        elif key == "ctrl f":
            self.widget.body = self.editor
        else:
            return super(GUI, self).keypress(size, key)

    def read_info(self):
        return self.editor.read_info()

    def process_save(self):
        self.widget.body = self.saver
        self.saver.set_info(self.read_info())
        # self.saver.save(self.read_info())
        # Then saver emits the 'finished' signal


    def process_load(self):
        pass


# p = Info()
# e = ColumnEditor(p, {})
m = GUI()
urwid.MainLoop(m).run()