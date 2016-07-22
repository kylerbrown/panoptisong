import urwid

class Info():
    def __init__(self):
        # self.dd = attrs_dict
        # if colnames == None:
        #     self.colnames = self.dd.keys()
        # else:
        #     self.colnames = colnames
        self.params = {"jackname": "lol", "room":"001"}
        self.birds = [["k1", "1", "system:capture_1"],["k2", "2", "system:capture2"],
                            ["k3", "3", "system:capture:3"]]

    def get_colnames(self):
        return self.dd.keys()

    def get_col(self, name):
        return self.dd[name]

    def set(self, name, key, val):
        self.dd[name][key] = val


class BirdsList(urwid.WidgetWrap):
    def __init__(self, name, birds_list):
        self.birds = birds_list
        body = [urwid.Text(name), urwid.Divider()]
        self.widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        for (name, box, channel) in self.birds:
            field = self.add_bird(name, box, channel)
            body.append(urwid.AttrMap(field, None, focus_map='reversed'))
        
        urwid.WidgetWrap.__init__(self, self.widget)

    def add_bird(self, name, box, channel):
        field_name = urwid.Edit(edit_text=name)
        field_box = urwid.Edit(edit_text=box)
        field_channel = urwid.Edit(edit_text=channel)
        field = urwid.Columns([field_name, field_box, field_channel])
        self.widget.body.append(field)

    def remove_focused_bird(self):
        idx = self.widget.focus_position
        del self.widget.body[idx]

    def keypress(self, size, key):
        if key == "ctrl n":
            self.add_bird("name", "box", "channel")
        elif key == "ctrl k":
            self.remove_focused_bird()

        else:
            return super(BirdsList, self).keypress(size, key)

class ParamsList(urwid.WidgetWrap):
    def __init__(self, name, params_list):
        self.params = params_list
        body = [urwid.Text(name), urwid.Divider()]
        for (key, val) in self.params.items():
            field_key = urwid.Text(key)
            field_val = urwid.Edit(edit_text=val)
            field = urwid.Columns([field_key, field_val])
            body.append(urwid.AttrMap(field, None, focus_map='reversed'))

        self.widget = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        urwid.WidgetWrap.__init__(self, self.widget)
        



class ColumnEditor(urwid.WidgetWrap):
    def __init__(self, info):
        self.info = info
        # self.params_col = self.create_params("PARAMETERS")
        self.params_col = ParamsList("PARAMETERS", self.info.params)
        # self.birds_col = self.create_birds("BIRDS")
        self.birds_col = BirdsList("BIRDS", self.info.birds)

        self.widget = urwid.Pile([self.params_col, self.birds_col])
        urwid.WidgetWrap.__init__(self, self.widget)


    def create_params(self, name):
        body = [urwid.Text(name), urwid.Divider()]
        for (key, val) in self.info.params.items():
            field_key = urwid.Text(key)
            field_val = urwid.Edit(edit_text=val)
            field = urwid.Columns([field_key, field_val])
            # urwid.connect_signal(field, 'change', self.set_field_param,
            #     user_args=[name, key])

            body.append(urwid.AttrMap(field, None, focus_map='reversed'))
        col = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        return col

    def create_birds(self, name):
        body = [urwid.Text(name), urwid.Divider()]
        for (name, box, channel) in self.info.birds:
            field = self.new_bird_element(name, box, channel)
            # urwid.connect_signal(field, 'change', self.set_field_param,
            #     user_args=[name, key])

            body.append(urwid.AttrMap(field, None, focus_map='reversed'))
        col = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        return col

    def new_bird_element(self, name, box, channel):
        field_name = urwid.Edit(edit_text=name)
        field_box = urwid.Edit(edit_text=box)
        field_channel = urwid.Edit(edit_text=channel)
        field = urwid.Columns([field_name, field_box, field_channel])
        return field

    def get_focused_bird(self):
        """ Returns the index in self.birds_col of the bird that
            the focus is currently on, or -1 if the focus is somewhere else
        """



    def toggle_column(self):
        self.widget.focus_position = (self.widget.focus_position+1)%len(self.cols)

    def keypress(self, size, key):
        if key == 'tab':
            self.toggle_column()

        else:
            return super(ColumnEditor, self).keypress(size, key)





class GUI(urwid.WidgetWrap):
    def __init__(self):
        self.infobox = urwid.Text("hello scientist\nI like pie")
        self.info = Info()
        self.editor = ColumnEditor(self.info)

        self.widget = urwid.Frame(self.editor, footer=self.infobox)
        urwid.WidgetWrap.__init__(self, self.widget)


# p = Info()
# e = ColumnEditor(p, {})
m = GUI()
urwid.MainLoop(m).run()