import wx


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MainFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        super().__init__(*args, **kwds)

        # Menu Bar
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        # Menu Bar end
        self.payments = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_VRULES)
        self.lastname = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.firstname = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.therapeute = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.price = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.payment_method = wx.Choice(self, wx.ID_ANY, choices=[])
        self.validate_btn = wx.Button(self, wx.ID_ANY, "Valider")
        self.change_payment_method_btn = wx.Button(self, wx.ID_ANY, "Changer moyen de paiement et imprimer")
        self.button_1 = wx.Button(self, wx.ID_ANY, "Rafraichir")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_payment, self.payments)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_payment, self.payments)
        self.Bind(wx.EVT_CHOICE, self.on_select_payment_method, self.payment_method)
        self.Bind(wx.EVT_BUTTON, self.on_validate, self.validate_btn)
        self.Bind(wx.EVT_BUTTON, self.on_change_payment, self.change_payment_method_btn)
        self.Bind(wx.EVT_BUTTON, self.on_refresh, self.button_1)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MainFrame.__set_properties
        self.SetTitle("Vérification/Confirmation finale de paiement")
        self.payments.AppendColumn("Sex", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Nom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Prénom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Thérapeute", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Heure", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Prix", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Payé par", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payment_method.Enable(False)
        self.validate_btn.Enable(False)
        self.change_payment_method_btn.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(2, 4, 0, 0)
        sizer_1.Add(self.payments, 1, wx.ALL | wx.EXPAND, 0)
        label_1 = wx.StaticText(self, wx.ID_ANY, "Nom")
        grid_sizer_1.Add(label_1, 0, wx.ALIGN_BOTTOM | wx.EXPAND, 0)
        label_2 = wx.StaticText(self, wx.ID_ANY, "Prénom")
        grid_sizer_1.Add(label_2, 0, wx.ALIGN_BOTTOM | wx.EXPAND, 0)
        label_3 = wx.StaticText(self, wx.ID_ANY, "Thérapeute")
        grid_sizer_1.Add(label_3, 0, wx.ALIGN_BOTTOM | wx.EXPAND, 0)
        label_4 = wx.StaticText(self, wx.ID_ANY, "Prix")
        grid_sizer_1.Add(label_4, 0, wx.ALIGN_BOTTOM | wx.EXPAND, 0)
        grid_sizer_1.Add(self.lastname, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.firstname, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.therapeute, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.price, 0, wx.EXPAND, 0)
        grid_sizer_1.AddGrowableCol(0)
        grid_sizer_1.AddGrowableCol(1)
        grid_sizer_1.AddGrowableCol(2)
        grid_sizer_1.AddGrowableCol(3)
        sizer_1.Add(grid_sizer_1, 0, wx.EXPAND, 0)
        label_5 = wx.StaticText(self, wx.ID_ANY, "Moyen de paiement", style=wx.ALIGN_RIGHT)
        sizer_2.Add(label_5, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_2.Add((5, 0), 0, 0, 0)
        sizer_2.Add(self.payment_method, 0, wx.EXPAND, 0)
        sizer_2.Add(self.validate_btn, 1, wx.EXPAND, 0)
        sizer_2.Add(self.change_payment_method_btn, 2, wx.EXPAND, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        sizer_1.Add(self.button_1, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def on_deselect_payment(self, event):  # wxGlade: MainFrame.<event_handler>
        print("Event handler 'on_deselect_payment' not implemented!")
        event.Skip()

    def on_select_payment(self, event):  # wxGlade: MainFrame.<event_handler>
        print("Event handler 'on_select_payment' not implemented!")
        event.Skip()

    def on_select_payment_method(self, event):  # wxGlade: MainFrame.<event_handler>
        print("Event handler 'on_select_payment_method' not implemented!")
        event.Skip()

    def on_validate(self, event):  # wxGlade: MainFrame.<event_handler>
        print("Event handler 'on_validate' not implemented!")
        event.Skip()

    def on_change_payment(self, event):  # wxGlade: MainFrame.<event_handler>
        print("Event handler 'on_change_payment' not implemented!")
        event.Skip()

    def on_refresh(self, event):  # wxGlade: MainFrame.<event_handler>
        print("Event handler 'on_refresh' not implemented!")
        event.Skip()


class BPCaisse(wx.App):
    def OnInit(self):
        self.main_frame = MainFrame(None, wx.ID_ANY, "")
        self.SetTopWindow(self.main_frame)
        self.main_frame.Show()
        return True


if __name__ == "__main__":
    bp_caisse = BPCaisse(0)
    bp_caisse.MainLoop()
