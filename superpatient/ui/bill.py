import datetime
from collections import OrderedDict
import wx

from superpatient.customization import DATE_FMT, labels_text
from superpatient.models import PAYMENT_METHODS, SEX_ALL


class BillDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.tarif_codes = OrderedDict()  # key = display string, value = (tarif_code, tarif_description, tarif_unit_price_cts)
        self.document_id = wx.StaticText(self, wx.ID_ANY, "document id")
        self.therapeute = wx.StaticText(self, wx.ID_ANY, "therapeute details")
        self.lastname = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.firstname = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.street = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.zip = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.city = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.birthdate = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.address = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.law = wx.Choice(self, wx.ID_ANY, choices=["LCA"])
        self.sex = wx.Choice(self, wx.ID_ANY, choices=[""] + SEX_ALL)
        self.incident_date = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.patient_id = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.avs_no = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.cada_no = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.insurance_no = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.canton = wx.Choice(self, wx.ID_ANY, choices=["", "AG", "AI", "AR", "BE", "BL", "BS", "FR", "GE", "GL", "GR", "JU", "LU", "NE", "NW", "OW", "SG", "SH", "SO", "SZ", "TG", "TI", "UR", "VD", "VS", "ZG", "ZH"])
        self.copy = wx.Choice(self, wx.ID_ANY, choices=["Non", "Oui"])
        self.reimbursement_type = wx.Choice(self, wx.ID_ANY, choices=["TG", "TP"])
        self.contract_no = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.treatment_period = wx.TextCtrl(self, wx.ID_ANY, "")
        self.reason = wx.Choice(self, wx.ID_ANY, choices=["", "Maladie", "Accident"])
        self.mandant = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.diagnostic = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.therapy = wx.Choice(self, wx.ID_ANY, choices=["Thérapie individuelle"])
        self.point_value = wx.TextCtrl(self, wx.ID_ANY, "1.0")
        self.vat_enabled = wx.Choice(self, wx.ID_ANY, choices=["TVA: Non", "TVA: Oui"])
        self.comment = wx.TextCtrl(self, wx.ID_ANY, "")
        self.position_adder_btn = wx.Button(self, wx.ID_ANY, "+", style=wx.BU_EXACTFIT)  # | wx.BORDER_NONE)
        self.payment_method = wx.Choice(self, wx.ID_ANY, choices=[""] + PAYMENT_METHODS)
        self.save_and_print_btn = wx.Button(self, wx.ID_ANY, "Sauver et imprimmer")
        self.print_btn = wx.Button(self, wx.ID_ANY, "Imprimmer")
        self.cancel_btn = wx.Button(self, wx.ID_ANY, "Annuler")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_add_position, self.position_adder_btn)
        self.Bind(wx.EVT_BUTTON, self.on_save_and_print, self.save_and_print_btn)
        self.Bind(wx.EVT_BUTTON, self.on_print, self.print_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_btn)

    def __set_properties(self):
        self.SetTitle("Facturation de la consultation")
        self.lastname.SetMinSize((200, -1))
        self.address.Enable(False)
        self.law.Enable(False)
        self.law.SetSelection(0)
        self.sex.Enable(False)
        self.sex.SetSelection(0)
        self.canton.Enable(False)
        self.copy.SetSelection(0)
        self.reimbursement_type.Enable(False)
        self.reimbursement_type.SetSelection(0)
        self.reason.Enable(False)
        self.reason.SetSelection(0)
        self.therapy.Enable(False)
        self.therapy.SetSelection(0)
        self.point_value.Enable(False)
        self.vat_enabled.Enable(False)
        self.vat_enabled.SetSelection(0)

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_2 = wx.GridBagSizer(0, 10)
        label_9 = wx.StaticText(self, wx.ID_ANY, "Document")
        label_9.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_9, (0, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.document_id, (0, 1), (1, 4), wx.ALIGN_CENTER_VERTICAL, 0)
        label_11 = wx.StaticText(self, wx.ID_ANY, "Auteur facture")
        label_11.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_11, (1, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.therapeute, (1, 1), (1, 4), wx.ALIGN_CENTER_VERTICAL, 0)
        label_26 = wx.StaticText(self, wx.ID_ANY, "Patient")
        label_26.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_26, (2, 0), (1, 1), 0, 0)
        label_1 = wx.StaticText(self, wx.ID_ANY, "Nom")
        grid_sizer_2.Add(label_1, (2, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.lastname, (2, 2), (1, 1), wx.EXPAND, 0)
        label_2 = wx.StaticText(self, wx.ID_ANY, u"Prénom")
        grid_sizer_2.Add(label_2, (3, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.firstname, (3, 2), (1, 1), wx.EXPAND, 0)
        label_3 = wx.StaticText(self, wx.ID_ANY, "Rue")
        grid_sizer_2.Add(label_3, (4, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.street, (4, 2), (1, 1), wx.EXPAND, 0)
        label_4 = wx.StaticText(self, wx.ID_ANY, "NPA")
        grid_sizer_2.Add(label_4, (5, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.zip, (5, 2), (1, 1), wx.EXPAND, 0)
        label_5 = wx.StaticText(self, wx.ID_ANY, u"Localité")
        grid_sizer_2.Add(label_5, (6, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.city, (6, 2), (1, 1), wx.EXPAND, 0)
        label_6 = wx.StaticText(self, wx.ID_ANY, "Date de naissance")
        grid_sizer_2.Add(label_6, (7, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.birthdate, (7, 2), (1, 1), wx.EXPAND, 0)
        grid_sizer_2.Add(self.address, (7, 3), (6, 2), wx.EXPAND, 0)
        label_7 = wx.StaticText(self, wx.ID_ANY, "Loi")
        grid_sizer_2.Add(label_7, (8, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.law, (8, 2), (1, 1), wx.EXPAND, 0)
        label_8 = wx.StaticText(self, wx.ID_ANY, "Sexe")
        grid_sizer_2.Add(label_8, (9, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.sex, (9, 2), (1, 1), wx.EXPAND, 0)
        label_10 = wx.StaticText(self, wx.ID_ANY, "Date cas")
        grid_sizer_2.Add(label_10, (10, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.incident_date, (10, 2), (1, 1), wx.EXPAND, 0)
        label_12 = wx.StaticText(self, wx.ID_ANY, u"N° patient")
        grid_sizer_2.Add(label_12, (11, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.patient_id, (11, 2), (1, 1), wx.EXPAND, 0)
        label_13 = wx.StaticText(self, wx.ID_ANY, u"N° AVS")
        grid_sizer_2.Add(label_13, (12, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.avs_no, (12, 2), (1, 1), wx.EXPAND, 0)
        label_14 = wx.StaticText(self, wx.ID_ANY, u"N° CADA")
        grid_sizer_2.Add(label_14, (13, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.cada_no, (13, 2), (1, 1), wx.EXPAND, 0)
        label_15 = wx.StaticText(self, wx.ID_ANY, u"N° assuré")
        grid_sizer_2.Add(label_15, (14, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.insurance_no, (14, 2), (1, 1), wx.EXPAND, 0)
        label_16 = wx.StaticText(self, wx.ID_ANY, "Canton")
        grid_sizer_2.Add(label_16, (15, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.canton, (15, 2), (1, 1), wx.EXPAND, 0)
        label_17 = wx.StaticText(self, wx.ID_ANY, "Copie")
        grid_sizer_2.Add(label_17, (16, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.copy, (16, 2), (1, 1), wx.EXPAND, 0)
        label_18 = wx.StaticText(self, wx.ID_ANY, "Type de remboursement")
        grid_sizer_2.Add(label_18, (17, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.reimbursement_type, (17, 2), (1, 1), wx.EXPAND, 0)
        label_19 = wx.StaticText(self, wx.ID_ANY, u"N° contrat")
        grid_sizer_2.Add(label_19, (18, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.contract_no, (18, 2), (1, 1), wx.EXPAND, 0)
        label_20 = wx.StaticText(self, wx.ID_ANY, "Traitement")
        grid_sizer_2.Add(label_20, (19, 1), (1, 1), 0, 0)
        grid_sizer_2.Add(self.treatment_period, (19, 2), (1, 1), wx.EXPAND, 0)
        label_23 = wx.StaticText(self, wx.ID_ANY, "Motif traitement")
        grid_sizer_2.Add(label_23, (19, 3), (1, 1), 0, 0)
        grid_sizer_2.Add(self.reason, (19, 4), (1, 1), wx.EXPAND, 0)
        label_21 = wx.StaticText(self, wx.ID_ANY, u"N°/Nom entreprise")
        grid_sizer_2.Add(label_21, (20, 1), (1, 1), 0, 0)
        label_24 = wx.StaticText(self, wx.ID_ANY, u"Permanence ostéopathique de la Gare (POG) Sàrl")
        grid_sizer_2.Add(label_24, (20, 2), (1, 3), 0, 0)
        label_22 = wx.StaticText(self, wx.ID_ANY, u"Rôle/Localité")
        grid_sizer_2.Add(label_22, (21, 1), (1, 1), 0, 0)
        label_25 = wx.StaticText(self, wx.ID_ANY, labels_text.bill_role_locality)
        grid_sizer_2.Add(label_25, (21, 2), (1, 3), 0, 0)
        label_27 = wx.StaticText(self, wx.ID_ANY, "Mandataire")
        label_27.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_27, (22, 0), (1, 1), 0, 0)
        grid_sizer_2.Add(self.mandant, (22, 1), (1, 4), wx.EXPAND, 0)
        label_28 = wx.StaticText(self, wx.ID_ANY, "Diagnostic")
        label_28.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_28, (23, 0), (1, 1), 0, 0)
        grid_sizer_2.Add(self.diagnostic, (23, 1), (1, 4), wx.EXPAND, 0)
        label_29 = wx.StaticText(self, wx.ID_ANY, u"Thérapie")
        label_29.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_29, (24, 0), (1, 1), 0, 0)
        grid_sizer_2.Add(self.therapy, (24, 1), (1, 1), 0, 0)
        label_30 = wx.StaticText(self, wx.ID_ANY, "Valeur du point (VPt)")
        grid_sizer_2.Add(label_30, (24, 2), (1, 1), wx.ALIGN_RIGHT, 0)
        grid_sizer_2.Add(self.point_value, (24, 3), (1, 1), 0, 0)
        grid_sizer_2.Add(self.vat_enabled, (24, 4), (1, 1), 0, 0)
        label_31 = wx.StaticText(self, wx.ID_ANY, "Commentaire")
        label_31.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        grid_sizer_2.Add(label_31, (25, 0), (1, 1), 0, 0)
        grid_sizer_2.Add(self.comment, (25, 1), (1, 4), wx.EXPAND, 0)
        grid_sizer_2.AddGrowableCol(2, 1)
        grid_sizer_2.AddGrowableCol(4, 1)
        sizer_1.Add(grid_sizer_2, 0, wx.ALL | wx.EXPAND, 5)
        self._positions_scroll = self._gen_positions_grid()
        sizer_1.Add(self._positions_scroll, 1, wx.ALL | wx.EXPAND, 5)
        self.positions_footer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.total = wx.StaticText(self, wx.ID_ANY, "Total: 0.00 CHF", style=wx.ALIGN_RIGHT)
        self.total.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.positions_footer_sizer.Add(self.position_adder_btn, 0, wx.ALIGN_LEFT, 0)
        self.positions_footer_sizer.AddStretchSpacer()
        self.positions_footer_sizer.Add(wx.StaticText(self, wx.ID_ANY, "Moyen de payement"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        self.positions_footer_sizer.Add(self.payment_method, 0, wx.ALIGN_CENTER, 0)
        self.positions_footer_sizer.AddStretchSpacer()
        self.positions_footer_sizer.Add(self.total, 0, 0, 0)
        sizer_1.Add(self.positions_footer_sizer, 0, wx.EXPAND | wx.ALL, 5)
        sizer_2.Add(self.save_and_print_btn, 0, 0, 0)
        sizer_2.Add(self.print_btn, 0, 0, 0)
        sizer_2.Add(self.cancel_btn, 0, 0, 0)
        sizer_1.Add(sizer_2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        width, height = self.GetSize()
        self.SetSize((width+3, height))

    def _gen_positions_grid(self):
        scroll = wx.ScrolledWindow(self)
        self._positions_grid = wx.GridBagSizer(0, 10)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Date", size=(80, -1)), (0, 0), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Tarif"), (0, 1), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Code tarifaire"), (0, 2), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Quantité", size=(60, -1)), (0, 3), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Prix", size=(50, -1)), (0, 4), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Vpt", size=(50, -1)), (0, 5), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "TVA", size=(40, -1)), (0, 6), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "Montant", size=(55, -1)), (0, 7), (1, 1), 0, 0)
        self._positions_grid.Add(wx.StaticText(scroll, wx.ID_ANY, "", size=(25, -1)), (0, 8), (1, 1), 0, 0)  # The column for the remove button
        self._positions_grid.AddGrowableCol(2)
        self._positions = []
        scroll.SetSizer(self._positions_grid)
        scroll.SetMinSize((850, 200))
        scroll.SetScrollRate(1, 1)
        return scroll

    def _tarif_code_choices(self):
        return list(self.tarif_codes)

    def _gen_tarif_code(self):
        window = wx.Window(self._positions_scroll)
        sizer = wx.BoxSizer(wx.VERTICAL)
        choice = wx.Choice(window, wx.ID_ANY, choices=self._tarif_code_choices())
        label = wx.TextCtrl(window, wx.ID_ANY, "")
        sizer.Add(choice, 0, 0, 0)
        sizer.Add(label, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_CHOICE, self.on_select_tarif_code, choice)
        window.SetSizer(sizer)
        return window

    def _gen_remove_btn(self):
        btn = wx.Button(self._positions_scroll, wx.ID_ANY, "X", style=wx.BU_EXACTFIT)
        self.Bind(wx.EVT_BUTTON, self.on_remove_position, btn)
        return btn

    def on_add_position(self, event):
        self.add_position()

    def add_position(self, position=None, readonly=False):
        tarif_code_widget = self._gen_tarif_code()
        if position is not None:
            position_date = position.position_date
            tarif_code = position.tarif_code
            tarif_description = position.tarif_description
            quantity = str(position.quantity)
            price_cts = position.price_cts
        else:
            position_date = datetime.date.today()
            tarif_code, tarif_description, price_cts = list(self.tarif_codes.values())[0]
            quantity = "1"

        tarif_code_widget.Children[0].StringSelection = tarif_code or ''
        tarif_code_widget.Children[1].Value = tarif_description or ''
        price = "%0.2f" % (price_cts / 100) if price_cts is not None else ''
        self._positions.append((wx.TextCtrl(self._positions_scroll, wx.ID_ANY, position_date.strftime(DATE_FMT), size=(80, -1)),  # Date
                                wx.StaticText(self._positions_scroll, wx.ID_ANY, "590"),  # Tarif
                                tarif_code_widget,  # Tarif code
                                wx.TextCtrl(self._positions_scroll, wx.ID_ANY, quantity, size=(60, -1), style=wx.ALIGN_RIGHT),  # Quantity
                                wx.TextCtrl(self._positions_scroll, wx.ID_ANY, price, size=(50, -1), style=wx.ALIGN_RIGHT),  # Unit price
                                wx.TextCtrl(self._positions_scroll, wx.ID_ANY, "1.0", size=(50, -1), style=wx.ALIGN_RIGHT),  # VPt
                                wx.TextCtrl(self._positions_scroll, wx.ID_ANY, "0.0%", size=(40, -1), style=wx.ALIGN_RIGHT),  # VAT
                                wx.TextCtrl(self._positions_scroll, wx.ID_ANY, "", size=(55, -1), style=wx.ALIGN_RIGHT),  # Amount
                                self._gen_remove_btn(),  # Remove button
                                ))
        tarif_code_widget.Children[1].Enable(price_cts is None)
        quantity_widget, price_widget, vpt_widget, vat_widget, amount_widget = self._positions[-1][3:8]
        quantity_widget.Enable(price_cts is not None)
        price_widget.Enable(price_cts is None)
        vpt_widget.Enable(False)
        vat_widget.Enable(False)
        amount_widget.Enable(False)
        self.Bind(wx.EVT_TEXT, self.on_update_amount, quantity_widget)
        self.Bind(wx.EVT_TEXT, self.on_update_amount, price_widget)
        row = len(self._positions)
        for col, widget in enumerate(self._positions[-1]):
            self._positions_grid.Add(widget, (row, col), (1, 1), wx.EXPAND if col == 2 else 0, 0)
        self._positions_grid.Layout()
        size = self._positions_grid.GetMinSize()
        self._positions_scroll.SetVirtualSize(size)
        if position is None:
            if price_cts is None:
                price_widget.SetSelection(-1, -1)
                price_widget.SetFocus()
            else:
                quantity_widget.SetSelection(-1, -1)
                quantity_widget.SetFocus()
        if readonly:
            for widget in self._positions[-1]:
                widget.Disable()
        self.update_amount(len(self._positions)-1)

    def on_remove_position(self, event):
        item = self._positions_grid.GetItem(event.EventObject)
        row = item.GetPos().Row
        pos_index = row - 1
        for widget in self._positions[pos_index]:
            self._positions_grid.Detach(widget)
            widget.Destroy()
        del self._positions[pos_index]
        for moved_row, positions in enumerate(self._positions[pos_index:]):
            moved_row += row
            for col, widget in enumerate(positions):
                self._positions_grid.Detach(widget)
                self._positions_grid.Add(widget, (moved_row, col), (1, 1), wx.EXPAND if col == 2 else 0, 0)
        self._positions_grid.Layout()
        size = self._positions_grid.GetMinSize()
        self._positions_scroll.SetVirtualSize(size)

    def on_select_tarif_code(self, event):
        choice_widget = event.EventObject
        description_widget = choice_widget.GetNextSibling()
        choice = choice_widget.StringSelection
        code, description, price_cts = self.tarif_codes[choice]
        description_widget.Value = description or ""
        description_widget.Enable(price_cts is None)
        position_index = self._positions_grid.GetItem(choice_widget.Parent).GetPos().GetRow() - 1
        quantity_widget, price_widget = self._positions[position_index][3:5]
        quantity_widget.Enable(price_cts is not None)
        quantity_widget.Value = "1"
        price_widget.Enable(price_cts is None)
        price_widget.Value = '%0.2f' % (price_cts/100) if price_cts is not None else ""
        if price_cts is None:
            price_widget.SetSelection(-1, -1)
            price_widget.SetFocus()
        else:
            quantity_widget.SetSelection(-1, -1)
            quantity_widget.SetFocus()

    def on_update_amount(self, event):
        position_index = self._positions_grid.GetItem(event.EventObject).GetPos().GetRow() - 1
        self.update_amount(position_index)

    def update_amount(self, position_index):
        quantity_widget, price_widget, _, _, amount_widget = self._positions[position_index][3:8]
        na = False
        try:
            quantity_cts = round(float(quantity_widget.Value) * 100)
        except ValueError:
            na = True
        try:
            price_cts = round(float(price_widget.Value) * 100)
        except ValueError:
            na = True
        if not na:
            amount_widget.Value = '%0.2f' % (quantity_cts * price_cts / 100 / 100)
        else:
            amount_widget.Value = 'n/a'
        total_cts = 0
        try:
            for position in self._positions:
                amount_wgt = position[-2]
                total_cts += round(float(amount_wgt.Value) * 100)
        except ValueError:
            self.total.LabelText = "Total: n/a CHF"
        else:
            self.total.LabelText = "Total: %0.2f CHF" % (total_cts / 100)
        self.positions_footer_sizer.Layout()

    def get_positions(self):
        from dateutil import parse_date
        return [(parse_date(date_wgt.Value),
                 self.tarif_codes[tarif_code_wgt.Children[0].StringSelection][0],
                 tarif_code_wgt.Children[1].Value,
                 float(quantity_wgt.Value),
                 round(float(price_wgt.Value) * 100))
                for date_wgt, _, tarif_code_wgt, quantity_wgt, price_wgt, _, _, _, _ in self._positions]

    def on_save_and_print(self, event):
        print("Event handler 'on_save_and_print' not implemented!")
        event.Skip()

    def on_print(self, event):
        print("Event handler 'on_print' not implemented!")
        event.Skip()

    def on_cancel(self, event):
        print("Event handler 'on_cancel' not implemented!")
        event.Skip()
