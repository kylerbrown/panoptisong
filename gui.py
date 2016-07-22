import urwid

class Params():
    def __init__(self, attrs_dict, colnames=None):
        self.dd = attrs_dict
        if colnames == None:
            self.colnames = self.dd.keys()
        else:
            self.colnames = colnames

    def get_colnames(self):
        return self.dd.keys()

    def get_col(self, name):
        return self.dd[name]

    def set(self, name, key, val):
        self.dd[name][key] = val


class ColumnEditor(urwid.WidgetWrap):
    def __init__(self, params, width):
        self.params = params
        self.colnames = params.get_colnames()
        self.ncols = len(self.colnames)
        self.body = []
        for name in self.colnames:
            attrs = self.params.get_col(name)
            self.create_column(name)

        self.widget = urwid.Columns(self.body)
        urwid.WidgetWrap.__init__(self, self.widget)


    def create_column(self, name):
        body = [urwid.Text(name), urwid.Divider()]
        for (key, val) in self.params.get_col(name).items():
            field = urwid.Edit(caption=key, edit_text=val)
            urwid.connect_signal(field, 'change', self.set_field_param,
                user_args=[name, key])

            body.append(urwid.AttrMap(field, None, focus_map='reversed'))
        col = urwid.ListBox(urwid.SimpleFocusListWalker(body))
        self.body.append(col)


    def set_field_param(self, *args):
        self.debug = args
        self.params.set(name, key, newtext)

    def toggle_column(self):
        self.widget.focus_position = (self.widget.focus_position+1)%self.ncols

    def keypress(self, size, key):
        if key == 'tab':
            self.toggle_column()
        else:
            return super(ColumnEditor, self).keypress(size, key)





class GUI(urwid.WidgetWrap):
    def __init__(self):
        pass


p = Params({"col1": {"a":"1", "b":"2"}, "col2":{"c":"3", "d":"4"}, "lol":{"f":"ffd", "g":"ggf"}})
e = ColumnEditor(p, 60)
try:
    urwid.MainLoop(e).run()
finally:
    print(e.debug)