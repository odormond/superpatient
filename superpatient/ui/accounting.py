import logging

import wx
import wx.grid


logger = logging.getLogger(__name__)


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        super().__init__(*args, **kwds)

        # Menu Bar
        self.menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Importer les paiements", "")
        self.Bind(wx.EVT_MENU, self.on_import_payments, id=item.GetId())
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Gestion des rappels", "")
        self.Bind(wx.EVT_MENU, self.on_manage_reminders, id=item.GetId())
        self.menubar.Append(wxglade_tmp_menu, "Paiements")
        wxglade_tmp_menu = wx.Menu()
        item = wxglade_tmp_menu.Append(wx.ID_ANY, "Statistiques", "")
        self.Bind(wx.EVT_MENU, self.on_show_stats, id=item.GetId())
        self.menubar.Append(wxglade_tmp_menu, "Statistiques")
        self.SetMenuBar(self.menubar)
        # Menu Bar end
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.therapeute = wx.Choice(self.panel_1, wx.ID_ANY, choices=[])
        self.filter_start = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.button_6 = wx.Button(self.panel_1, wx.ID_ANY, "\U0001f4c5", style=wx.BU_EXACTFIT)
        self.payment_method = wx.Choice(self.panel_1, wx.ID_ANY, choices=[])
        self.filter_end = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.button_7 = wx.Button(self.panel_1, wx.ID_ANY, "\U0001f4c5", style=wx.BU_EXACTFIT)
        self.bill_status = wx.Choice(self.panel_1, wx.ID_ANY, choices=[])
        self.filter_lastname = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.filter_firstname = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER)
        self.button_8 = wx.Button(self.panel_1, wx.ID_ANY, "\U0001f50e", style=wx.BU_EXACTFIT)
        self.payments = wx.ListCtrl(self.panel_1, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.payments_count = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.total_bills = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_RIGHT)
        self.total_reminder_costs = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_RIGHT)
        self.total = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY | wx.TE_RIGHT)
        self.payment_date = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.button_1 = wx.Button(self.panel_1, wx.ID_ANY, "Marquer payé")
        self.button_2 = wx.Button(self.panel_1, wx.ID_ANY, "Réimprimer")
        self.button_3 = wx.Button(self.panel_1, wx.ID_ANY, "Marquer imprimé")
        self.button_4 = wx.Button(self.panel_1, wx.ID_ANY, "Marquer envoyé")
        self.button_5 = wx.Button(self.panel_1, wx.ID_ANY, "Marquer abandonné")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.on_search, self.therapeute)
        self.Bind(wx.EVT_CHOICE, self.on_search, self.payment_method)
        self.Bind(wx.EVT_CHOICE, self.on_search, self.bill_status)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search, self.filter_lastname)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search, self.filter_firstname)
        self.Bind(wx.EVT_BUTTON, self.on_popup_start_date, self.button_6)
        self.Bind(wx.EVT_BUTTON, self.on_popup_end_date, self.button_7)
        self.Bind(wx.EVT_BUTTON, self.on_search, self.button_8)
        self.Bind(wx.EVT_BUTTON, self.on_mark_paid, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_print_again, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.on_mark_printed, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.on_mark_sent, self.button_4)
        self.Bind(wx.EVT_BUTTON, self.on_mark_abandoned, self.button_5)

    def __set_properties(self):
        self.SetTitle("frame")
        self.payments.AppendColumn("S", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Sex", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Nom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Prénom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Facture du", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.payments.AppendColumn("Prix", format=wx.LIST_FORMAT_RIGHT, width=-1)
        self.payments.AppendColumn("Payé le", format=wx.LIST_FORMAT_LEFT, width=-1)

    def __do_layout(self):
        sizer_0 = wx.BoxSizer(wx.VERTICAL)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.FlexGridSizer(2, 4, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(3, 4, 0, 0)
        grid_sizer_1 = wx.FlexGridSizer(0, 5, 0, 0)
        label_1 = wx.StaticText(self.panel_1, wx.ID_ANY, "Thérapeute")
        grid_sizer_1.Add(label_1, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.therapeute, 0, wx.EXPAND, 0)
        label_2 = wx.StaticText(self.panel_1, wx.ID_ANY, "Facture dès le")
        grid_sizer_1.Add(label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.filter_start, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.button_6, 0, 0, 0)
        label_4 = wx.StaticText(self.panel_1, wx.ID_ANY, "Moyen de paiement")
        grid_sizer_1.Add(label_4, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.payment_method, 0, wx.EXPAND, 0)
        label_3 = wx.StaticText(self.panel_1, wx.ID_ANY, "Facture jusqu'au")
        grid_sizer_1.Add(label_3, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.filter_end, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.button_7, 0, 0, 0)
        label_6 = wx.StaticText(self.panel_1, wx.ID_ANY, "Status de la facture")
        grid_sizer_1.Add(label_6, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.bill_status, 0, wx.EXPAND, 0)
        grid_sizer_1.Add((0, 0), 0, 0, 0)
        grid_sizer_1.Add((0, 0), 0, 0, 0)
        grid_sizer_1.Add((0, 0), 0, 0, 0)
        label_7 = wx.StaticText(self.panel_1, wx.ID_ANY, "Nom")
        grid_sizer_1.Add(label_7, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.filter_lastname, 0, wx.EXPAND, 0)
        label_5 = wx.StaticText(self.panel_1, wx.ID_ANY, "Prénom")
        grid_sizer_1.Add(label_5, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_1.Add(self.filter_firstname, 0, wx.EXPAND, 0)
        grid_sizer_1.Add(self.button_8, 0, 0, 0)
        grid_sizer_1.AddGrowableCol(1)
        grid_sizer_1.AddGrowableCol(3)
        sizer_1.Add(grid_sizer_1, 0, wx.EXPAND, 0)
        sizer_1.Add(self.payments, 1, wx.EXPAND, 0)
        label_8 = wx.StaticText(self.panel_1, wx.ID_ANY, "# entrées")
        grid_sizer_2.Add(label_8, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.payments_count, 0, wx.EXPAND, 0)
        label_9 = wx.StaticText(self.panel_1, wx.ID_ANY, "Total factures")
        grid_sizer_2.Add(label_9, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.total_bills, 0, wx.EXPAND, 0)
        grid_sizer_2.Add((0, 0), 0, 0, 0)
        grid_sizer_2.Add((0, 0), 0, 0, 0)
        label_12 = wx.StaticText(self.panel_1, wx.ID_ANY, "Total frais de rappels")
        grid_sizer_2.Add(label_12, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.total_reminder_costs, 0, wx.EXPAND, 0)
        grid_sizer_2.Add((0, 0), 0, 0, 0)
        grid_sizer_2.Add((0, 0), 0, 0, 0)
        label_13 = wx.StaticText(self.panel_1, wx.ID_ANY, "Total")
        grid_sizer_2.Add(label_13, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_2.Add(self.total, 0, wx.EXPAND, 0)
        grid_sizer_2.AddGrowableCol(1)
        grid_sizer_2.AddGrowableCol(3)
        sizer_1.Add(grid_sizer_2, 0, wx.EXPAND, 0)
        label_14 = wx.StaticText(self.panel_1, wx.ID_ANY, "Paiement reçu le")
        sizer_2.Add(label_14, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_2.Add(self.payment_date, 0, wx.EXPAND, 0)
        sizer_2.Add(self.button_1, 0, wx.EXPAND, 0)
        sizer_2.Add((0, 0), 0, 0, 0)
        sizer_2.Add(self.button_2, 0, wx.EXPAND, 0)
        sizer_2.Add(self.button_3, 0, wx.EXPAND, 0)
        sizer_2.Add(self.button_4, 0, wx.EXPAND, 0)
        sizer_2.Add(self.button_5, 0, wx.EXPAND, 0)
        sizer_2.AddGrowableCol(0)
        sizer_2.AddGrowableCol(1)
        sizer_2.AddGrowableCol(2)
        sizer_2.AddGrowableCol(3)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_1)
        sizer_0.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_0)
        sizer_0.Fit(self)
        self.Layout()
        self.SetSize((800, 600))

    def on_import_payments(self, event):
        logger.warning("Event handler 'on_import_payments' not implemented!")
        event.Skip()

    def on_manage_reminders(self, event):
        logger.warning("Event handler 'on_manage_reminders' not implemented!")
        event.Skip()

    def on_show_stats(self, event):
        logger.warning("Event handler 'on_show_stats' not implemented!")
        event.Skip()

    def on_popup_start_date(self, event):
        logger.warning("Event handler 'on_popup_start_date' not implemented!")
        event.Skip()

    def on_popup_end_date(self, event):
        logger.warning("Event handler 'on_popup_end_date' not implemented!")
        event.Skip()

    def on_search(self, event):
        logger.warning("Event handler 'on_search' not implemented!")
        event.Skip()

    def on_mark_paid(self, event):
        logger.warning("Event handler 'on_mark_paid' not implemented!")
        event.Skip()

    def on_print_again(self, event):
        logger.warning("Event handler 'on_print_again' not implemented!")
        event.Skip()

    def on_mark_printed(self, event):
        logger.warning("Event handler 'on_mark_printed' not implemented!")
        event.Skip()

    def on_mark_sent(self, event):
        logger.warning("Event handler 'on_mark_sent' not implemented!")
        event.Skip()

    def on_mark_abandoned(self, event):
        logger.warning("Event handler 'on_mark_abandoned' not implemented!")
        event.Skip()


class RemindersManagementDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.upto = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_PROCESS_ENTER | wx.TE_READONLY)
        self.button_6 = wx.Button(self, wx.ID_ANY, "\U0001f4c5", style=wx.BU_EXACTFIT)
        self.reminders = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        #self.base_font = wx.Font(wx.FontInfo(12))
        #self.reminders.SetFont(self.base_font)
        self.total = wx.TextCtrl(self, wx.ID_ANY, "")
        self.button_9 = wx.Button(self, wx.ID_ANY, "Générer les rappels")
        self.button_10 = wx.Button(self, wx.ID_ANY, "Annuler")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.on_update_list, self.upto)
        self.Bind(wx.EVT_BUTTON, self.on_popup_date, self.button_6)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_update_selection, self.reminders)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_update_selection, self.reminders)
        self.Bind(wx.EVT_BUTTON, self.on_generate, self.button_9)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_10)

    def __set_properties(self):
        self.SetTitle("Gestion des rappels")
        self.reminders.AppendColumn("", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.reminders.AppendColumn("Nom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.reminders.AppendColumn("Prénom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.reminders.AppendColumn("Facture du", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.reminders.AppendColumn("Prix", format=wx.LIST_FORMAT_RIGHT, width=-1)
        self.reminders.AppendColumn("Rappel le", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.reminders.AppendColumn("#", format=wx.LIST_FORMAT_RIGHT, width=-1)

    def __do_layout(self):
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        label_16 = wx.StaticText(self, wx.ID_ANY, "Facture ou rappels jusqu'au", style=wx.ALIGN_RIGHT)
        sizer_4.Add(label_16, 1, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        sizer_4.Add(self.upto, 1, 0, 0)
        sizer_4.Add(self.button_6, 0, 0, 0)
        sizer_3.Add(sizer_4, 0, wx.EXPAND, 0)
        sizer_3.Add(self.reminders, 1, wx.EXPAND, 0)
        label_15 = wx.StaticText(self, wx.ID_ANY, "Total", style=wx.ALIGN_RIGHT)
        sizer_5.Add(label_15, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 3)
        sizer_5.Add(self.total, 1, 0, 0)
        sizer_3.Add(sizer_5, 0, wx.EXPAND, 0)
        sizer_6.Add(self.button_9, 1, wx.ALIGN_RIGHT, 0)
        sizer_6.Add(self.button_10, 1, 0, 0)
        sizer_3.Add(sizer_6, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()
        self.SetSize((900, 600))

    def on_update_list(self, event):
        logger.warning("Event handler 'on_update_list' not implemented!")
        event.Skip()

    def on_popup_date(self, event):
        logger.warning("Event handler 'on_popup_date' not implemented!")
        event.Skip()

    def on_update_selection(self, event):
        logger.warning("Event handler 'on_update_selection' not implemented!")
        event.Skip()

    def on_generate(self, event):
        logger.warning("Event handler 'on_generate' not implemented!")
        event.Skip()

    def on_cancel(self, event):
        logger.warning("Event handler 'on_cancel' not implemented!")
        event.Skip()


class StatisticsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.year = wx.Choice(self, wx.ID_ANY, choices=[])
        self.month = wx.Choice(self, wx.ID_ANY, choices=[])
        self.stats_type = wx.Choice(self, wx.ID_ANY, choices=[])
        self.stats = wx.grid.Grid(self, wx.ID_ANY)
        self.ok = wx.Button(self, wx.ID_ANY, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.update_display, self.year)
        self.Bind(wx.EVT_CHOICE, self.update_display, self.month)
        self.Bind(wx.EVT_CHOICE, self.update_display, self.stats_type)
        self.Bind(wx.EVT_BUTTON, self.on_done, self.ok)

    def __set_properties(self):
        self.SetTitle("Statistiques")
        self.SetMaxSize(wx.GetDisplaySize())
        self.stats_type.SetSelection(0)
        self.stats.CreateGrid(0, 0)
        self.stats.EnableEditing(0)

    def __do_layout(self):
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8.Add(self.year, 1, 0, 0)
        sizer_8.Add(self.month, 1, 0, 0)
        sizer_8.Add(self.stats_type, 1, 0, 0)
        sizer_7.Add(sizer_8, 0, wx.EXPAND, 0)
        sizer_7.Add(self.stats, 1, wx.EXPAND, 0)
        sizer_7.Add(self.ok, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_7)
        sizer_7.Fit(self)
        self.Layout()

    def update_display(self, event):
        logger.warning("Event handler 'update_display' not implemented!")
        event.Skip()

    def on_done(self, event):
        logger.warning("Event handler 'on_done' not implemented!")
        event.Skip()


class ImportDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        super().__init__(*args, **kwds)
        self.volume_in_order = wx.StaticText(self, wx.ID_ANY, "0", style=wx.ALIGN_RIGHT)
        self.revenue_in_order = wx.StaticText(self, wx.ID_ANY, "0.00 CHF", style=wx.ALIGN_RIGHT)
        self.details_in_order = wx.Button(self, wx.ID_ANY, "Détails")
        self.volume_wrong_amount = wx.StaticText(self, wx.ID_ANY, "0", style=wx.ALIGN_RIGHT)
        self.revenue_wrong_amount = wx.StaticText(self, wx.ID_ANY, "0.00 CHF", style=wx.ALIGN_RIGHT)
        self.details_wrong_amount = wx.Button(self, wx.ID_ANY, "Détails")
        self.volume_already_paid = wx.StaticText(self, wx.ID_ANY, "0", style=wx.ALIGN_RIGHT)
        self.revenue_already_paid = wx.StaticText(self, wx.ID_ANY, "0.00 CHF", style=wx.ALIGN_RIGHT)
        self.details_already_paid = wx.Button(self, wx.ID_ANY, "Détails")
        self.volume_not_found = wx.StaticText(self, wx.ID_ANY, "0", style=wx.ALIGN_RIGHT)
        self.revenue_not_found = wx.StaticText(self, wx.ID_ANY, "0.00 CHF", style=wx.ALIGN_RIGHT)
        self.details_not_found = wx.Button(self, wx.ID_ANY, "Détails")
        self.volume_ignored = wx.StaticText(self, wx.ID_ANY, "0", style=wx.ALIGN_RIGHT)
        self.details_ignored = wx.Button(self, wx.ID_ANY, "Détails")
        self.button_11 = wx.Button(self, wx.ID_ANY, "Valider l'import")
        self.button_12 = wx.Button(self, wx.ID_ANY, "Annuler")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_details_in_order, self.details_in_order)
        self.Bind(wx.EVT_BUTTON, self.on_details_wrong_amount, self.details_wrong_amount)
        self.Bind(wx.EVT_BUTTON, self.on_details_already_paid, self.details_already_paid)
        self.Bind(wx.EVT_BUTTON, self.on_details_not_found, self.details_not_found)
        self.Bind(wx.EVT_BUTTON, self.on_details_ignored, self.details_ignored)
        self.Bind(wx.EVT_BUTTON, self.on_validate_import, self.button_11)
        self.Bind(wx.EVT_BUTTON, self.on_cancel_import, self.button_12)

    def __set_properties(self):
        self.SetTitle("Résumé de l'import")

    def __do_layout(self):
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_3 = wx.FlexGridSizer(6, 4, 0, 0)
        label_33 = wx.StaticText(self, wx.ID_ANY, "Paiements")
        grid_sizer_3.Add(label_33, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT, 0)
        label_17 = wx.StaticText(self, wx.ID_ANY, "Volume", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_17, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 0)
        label_18 = wx.StaticText(self, wx.ID_ANY, "Revenue", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_18, 0, wx.ALIGN_BOTTOM | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_3.Add((0, 0), 0, 0, 0)
        label_19 = wx.StaticText(self, wx.ID_ANY, "En ordre", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_19, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.volume_in_order, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.revenue_in_order, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.details_in_order, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        label_20 = wx.StaticText(self, wx.ID_ANY, "Ne correspondant pas au montant attendu", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_20, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.volume_wrong_amount, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.revenue_wrong_amount, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.details_wrong_amount, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        label_21 = wx.StaticText(self, wx.ID_ANY, "Déjà encaissés", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_21, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.volume_already_paid, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.revenue_already_paid, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.details_already_paid, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        label_22 = wx.StaticText(self, wx.ID_ANY, "Non trouvés", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_22, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.volume_not_found, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.revenue_not_found, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.details_not_found, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        label_23 = wx.StaticText(self, wx.ID_ANY, "Ignorés", style=wx.ALIGN_RIGHT)
        grid_sizer_3.Add(label_23, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add(self.volume_ignored, 0, wx.ALIGN_RIGHT, 0)
        grid_sizer_3.Add((0, 0), 0, 0, 0)
        grid_sizer_3.Add(self.details_ignored, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_3.AddGrowableCol(0)
        grid_sizer_3.AddGrowableCol(1)
        grid_sizer_3.AddGrowableCol(2)
        sizer_9.Add(grid_sizer_3, 1, wx.EXPAND, 0)
        sizer_10.Add(self.button_11, 1, wx.ALIGN_RIGHT, 0)
        sizer_10.Add(self.button_12, 1, wx.EXPAND, 0)
        sizer_9.Add(sizer_10, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_9)
        sizer_9.Fit(self)
        self.Layout()

    def on_details_in_order(self, event):
        logger.warning("Event handler 'on_details_in_order' not implemented!")
        event.Skip()

    def on_details_wrong_amount(self, event):
        logger.warning("Event handler 'on_details_wrong_amount' not implemented!")
        event.Skip()

    def on_details_already_paid(self, event):
        logger.warning("Event handler 'on_details_already_paid' not implemented!")
        event.Skip()

    def on_details_not_found(self, event):
        logger.warning("Event handler 'on_details_not_found' not implemented!")
        event.Skip()

    def on_details_ignored(self, event):
        logger.warning("Event handler 'on_details_ignored' not implemented!")
        event.Skip()

    def on_validate_import(self, event):
        logger.warning("Event handler 'on_validate_import' not implemented!")
        event.Skip()

    def on_cancel_import(self, event):
        logger.warning("Event handler 'on_cancel_import' not implemented!")
        event.Skip()


class DetailsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.details = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.SetTitle("Détails des transactions")
        self.SetMaxSize(wx.GetDisplaySize())

    def __do_layout(self):
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_11.Add(self.details, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_11)
        sizer_11.Fit(self)
        self.Layout()
