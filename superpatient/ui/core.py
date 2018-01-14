import wx
import wx.html2

from ..models import CANTONS


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL
        super().__init__(*args, **kwds)

        # Menu Bar
        self.menubar = wx.MenuBar()
        admin_menu = wx.Menu()

        ACCESS_RIGHTS = wx.GetApp().ACCESS_RIGHTS

        if 'MANAGE_THERAPISTS' in ACCESS_RIGHTS:
            item = admin_menu.Append(wx.ID_ANY, "Gestion des collaborateurs", "")
            self.Bind(wx.EVT_MENU, self.on_manage_collaborators, id=item.GetId())
        if 'MANAGE_COSTS' in ACCESS_RIGHTS:
            item = admin_menu.Append(wx.ID_ANY, "Gestion des tarifs", "")
            self.Bind(wx.EVT_MENU, self.on_manage_tarifs, id=item.GetId())
            admin_menu.AppendSeparator()
        # XXX Disabled for the time being
        #if 'MANUAL_BILL' in ACCESS_RIGHTS:
        #    item = admin_menu.Append(wx.ID_ANY, "Facture manuelle", "")
        #    self.Bind(wx.EVT_MENU, self.on_manual_bill, id=item.GetId())
        #    item = admin_menu.Append(wx.ID_ANY, "Gestion des adresses", "")
        #    self.Bind(wx.EVT_MENU, self.on_manage_addresses, id=item.GetId())
        #    admin_menu.AppendSeparator()
        if 'MANAGE_PATIENTS' in ACCESS_RIGHTS:
            item = admin_menu.Append(wx.ID_ANY, "Supprimer des données", "")
            self.Bind(wx.EVT_MENU, self.on_delete_data, id=item.GetId())
        if 'MANAGE_DB' in ACCESS_RIGHTS:
            item = admin_menu.Append(wx.ID_ANY, "Sauvegarder la base de données", "")
            self.Bind(wx.EVT_MENU, self.on_dump_database, id=item.GetId())
            item = admin_menu.Append(wx.ID_ANY, "Restaurer la base de données", "")
            self.Bind(wx.EVT_MENU, self.on_restore_database, id=item.GetId())
        if ACCESS_RIGHTS:
            self.menubar.Append(admin_menu, "Administration")
        self.SetMenuBar(self.menubar)
        # Menu Bar end
        self.button_1 = wx.Button(self, wx.ID_ANY, "Nouveau patient")
        self.button_2 = wx.Button(self, wx.ID_ANY, "Voir ou modifier une fiche patient")
        self.patients_count = wx.StaticText(self, wx.ID_ANY, "######")
        self.button_3 = wx.Button(self, wx.ID_ANY, "Nouvelle consultation (patient existant)")
        self.button_4 = wx.Button(self, wx.ID_ANY, "Voir ou modifier une consultation")
        self.consultations_count = wx.StaticText(self, wx.ID_ANY, "######")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_new_patient, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.on_search_patient, self.button_2)
        self.Bind(wx.EVT_BUTTON, self.on_new_consultation, self.button_3)
        self.Bind(wx.EVT_BUTTON, self.on_search_consultation, self.button_4)
        self.Bind(wx.EVT_ACTIVATE, self.on_activate, self)

    def __set_properties(self):
        self.SetTitle("SuperPatient")

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.FlexGridSizer(5, 2, 5, 5)
        sizer_2.Add(self.button_1, 0, wx.EXPAND, 0)
        sizer_2.Add((0, 0), 0, 0, 0)
        sizer_2.Add(self.button_2, 0, wx.EXPAND, 0)
        sizer_2.Add(self.patients_count, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sizer_2.Add((20, 20), 0, 0, 0)
        sizer_2.Add((0, 0), 0, 0, 0)
        sizer_2.Add(self.button_3, 0, wx.EXPAND, 0)
        sizer_2.Add((0, 0), 0, 0, 0)
        sizer_2.Add(self.button_4, 0, wx.EXPAND, 0)
        sizer_2.Add(self.consultations_count, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
        sizer_2.AddGrowableCol(0)
        sizer_1.Add(sizer_2, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()

    def on_manage_collaborators(self, event):
        print("Event handler 'on_manage_collaborators' not implemented!")
        event.Skip()

    def on_manage_tarifs(self, event):
        print("Event handler 'on_manage_tarifs' not implemented!")
        event.Skip()

    def on_manual_bill(self, event):
        print("Event handler 'on_manual_bill' not implemented!")
        event.Skip()

    def on_manage_addresses(self, event):
        print("Event handler 'on_manage_addresses' not implemented!")
        event.Skip()

    def on_delete_data(self, event):
        print("Event handler 'on_delete_data' not implemented!")
        event.Skip()

    def on_dump_database(self, event):
        print("Event handler 'on_dump_database' not implemented!")
        event.Skip()

    def on_restore_database(self, event):
        print("Event handler 'on_restore_database' not implemented!")
        event.Skip()

    def on_new_patient(self, event):
        print("Event handler 'on_new_patient' not implemented!")
        event.Skip()

    def on_search_patient(self, event):
        print("Event handler 'on_search_patient' not implemented!")
        event.Skip()

    def on_new_consultation(self, event):
        print("Event handler 'on_new_consultation' not implemented!")
        event.Skip()

    def on_search_consultation(self, event):
        print("Event handler 'on_search_consultation' not implemented!")
        event.Skip()

    def on_activate(self, event):
        print("Event handler 'on_activate' not implemented!")
        event.Skip()


class ManageCollaboratorsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.collaborators_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.LC_SINGLE_SEL)
        self.therapeute = wx.TextCtrl(self, wx.ID_ANY, "")
        self.login = wx.TextCtrl(self, wx.ID_ANY, "")
        self.address_header = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.add_btn = wx.Button(self, wx.ID_ANY, "Ajouter")
        self.change_btn = wx.Button(self, wx.ID_ANY, "Modifier")
        self.remove_btn = wx.Button(self, wx.ID_ANY, "Supprimer")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_collaborator, self.collaborators_list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_collaborator, self.collaborators_list)
        self.Bind(wx.EVT_BUTTON, self.on_add_collaborator, self.add_btn)
        self.Bind(wx.EVT_BUTTON, self.on_change_collaborator, self.change_btn)
        self.Bind(wx.EVT_BUTTON, self.on_remove_collaborator, self.remove_btn)

    def __set_properties(self):
        self.SetTitle("Gérer les collaborateurs")
        self.collaborators_list.AppendColumn("Thérapeute", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.collaborators_list.AppendColumn("Login", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.collaborators_list.AppendColumn("Entête d'adresse", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.address_header.SetMinSize((300, 100))

    def __do_layout(self):
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_28 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_31 = wx.BoxSizer(wx.VERTICAL)
        sizer_30 = wx.BoxSizer(wx.VERTICAL)
        sizer_29 = wx.BoxSizer(wx.VERTICAL)
        sizer_3.Add(self.collaborators_list, 1, wx.EXPAND, 0)
        label_1 = wx.StaticText(self, wx.ID_ANY, "Thérapeute")
        sizer_29.Add(label_1, 0, wx.ALIGN_BOTTOM, 0)
        sizer_29.Add(self.therapeute, 0, wx.EXPAND, 0)
        label_2 = wx.StaticText(self, wx.ID_ANY, "Login")
        sizer_29.Add(label_2, 0, wx.ALIGN_BOTTOM, 0)
        sizer_29.Add(self.login, 0, wx.EXPAND, 0)
        sizer_28.Add(sizer_29, 1, 0, 0)
        label_3 = wx.StaticText(self, wx.ID_ANY, "Entête d'adresse")
        sizer_30.Add(label_3, 0, wx.ALIGN_BOTTOM, 0)
        sizer_30.Add(self.address_header, 1, wx.EXPAND, 0)
        sizer_28.Add(sizer_30, 1, wx.EXPAND, 0)
        sizer_31.Add(self.add_btn, 0, wx.EXPAND, 0)
        sizer_31.Add(self.change_btn, 0, wx.EXPAND, 0)
        sizer_31.Add(self.remove_btn, 0, wx.EXPAND, 0)
        sizer_28.Add(sizer_31, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_3.Add(sizer_28, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_3)
        sizer_3.Fit(self)
        self.Layout()

    def on_deselect_collaborator(self, event):
        print("Event handler 'on_deselect_collaborator' not implemented!")
        event.Skip()

    def on_select_collaborator(self, event):
        print("Event handler 'on_select_collaborator' not implemented!")
        event.Skip()

    def on_add_collaborator(self, event):
        print("Event handler 'on_add_collaborator' not implemented!")
        event.Skip()

    def on_change_collaborator(self, event):
        print("Event handler 'on_change_collaborator' not implemented!")
        event.Skip()

    def on_remove_collaborator(self, event):
        print("Event handler 'on_remove_collaborator' not implemented!")
        event.Skip()


class ManageCostsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.costs_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.LC_SINGLE_SEL)
        self.code = wx.TextCtrl(self, wx.ID_ANY, "")
        self.description = wx.TextCtrl(self, wx.ID_ANY, "")
        self.price = wx.TextCtrl(self, wx.ID_ANY, "")
        self.add_btn = wx.Button(self, wx.ID_ANY, "Ajouter")
        self.change_btn = wx.Button(self, wx.ID_ANY, "Modifier")
        self.remove_btn = wx.Button(self, wx.ID_ANY, "Supprimer")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_cost, self.costs_list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_cost, self.costs_list)
        self.Bind(wx.EVT_BUTTON, self.on_add_cost, self.add_btn)
        self.Bind(wx.EVT_BUTTON, self.on_change_cost, self.change_btn)
        self.Bind(wx.EVT_BUTTON, self.on_remove_cost, self.remove_btn)

    def __set_properties(self):
        self.SetTitle("Gérer les tarifs")
        self.costs_list.AppendColumn("Code Tarifaire", format=wx.LIST_FORMAT_RIGHT, width=-1)
        self.costs_list.AppendColumn("Description", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.costs_list.AppendColumn("Prix de l'unité", format=wx.LIST_FORMAT_RIGHT, width=-1)
        self.costs_list.SetMinSize((-1, 250))

    def __do_layout(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(3, 4, 0, 0)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.costs_list, 1, wx.EXPAND, 0)

        code_label = wx.StaticText(self, wx.ID_ANY, "Code Tarifaire")
        grid_sizer.Add(code_label, 0, wx.ALIGN_BOTTOM, 0)
        description_label = wx.StaticText(self, wx.ID_ANY, "Description")
        grid_sizer.Add(description_label, 0, wx.ALIGN_BOTTOM, 0)
        price_label = wx.StaticText(self, wx.ID_ANY, "Prix")
        grid_sizer.Add(price_label, 0, wx.ALIGN_BOTTOM, 0)
        grid_sizer.Add((0, 0), 0, 0, 0)

        grid_sizer.Add(self.code, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.description, 0, wx.EXPAND, 0)
        grid_sizer.Add(self.price, 0, wx.EXPAND, 0)
        button_sizer.Add(self.add_btn, 0, wx.EXPAND, 0)
        button_sizer.Add(self.change_btn, 0, wx.EXPAND, 0)
        grid_sizer.Add(button_sizer, 1, wx.EXPAND, 0)

        grid_sizer.Add((0, 0), 0, 0, 0)
        grid_sizer.Add((0, 0), 0, 0, 0)
        grid_sizer.Add((0, 0), 0, 0, 0)
        grid_sizer.Add(self.remove_btn, 0, wx.EXPAND, 0)
        grid_sizer.AddGrowableCol(1)
        main_sizer.Add(grid_sizer, 0, wx.EXPAND, 0)
        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        main_sizer.SetSizeHints(self)
        self.Layout()

    def on_deselect_cost(self, event):
        print("Event handler 'on_deselect_cost' not implemented!")
        event.Skip()

    def on_select_cost(self, event):
        print("Event handler 'on_select_cost' not implemented!")
        event.Skip()

    def on_add_cost(self, event):
        print("Event handler 'on_add_cost' not implemented!")
        event.Skip()

    def on_change_cost(self, event):
        print("Event handler 'on_change_cost' not implemented!")
        event.Skip()

    def on_remove_cost(self, event):
        print("Event handler 'on_remove_cost' not implemented!")
        event.Skip()


class ManualBillDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)

        self.panel_4 = wx.Panel(self, wx.ID_ANY)
        self.therapeute = wx.Choice(self.panel_4, wx.ID_ANY, choices=[])
        self.prefilled_address = wx.Choice(self.panel_4, wx.ID_ANY, choices=["Adresse manuelle"])
        self.therapeute_address = wx.TextCtrl(self.panel_4, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE | wx.TE_READONLY)
        self.address = wx.TextCtrl(self.panel_4, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.reason = wx.TextCtrl(self.panel_4, wx.ID_ANY, "")
        self.amount = wx.TextCtrl(self.panel_4, wx.ID_ANY, "")
        self.remark = wx.TextCtrl(self.panel_4, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.button_8 = wx.Button(self.panel_4, wx.ID_ANY, "Générer")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_CHOICE, self.on_select_therapeute, self.therapeute)
        self.Bind(wx.EVT_CHOICE, self.on_select_address, self.prefilled_address)
        self.Bind(wx.EVT_BUTTON, self.on_generate, self.button_8)

    def __set_properties(self):
        self.SetTitle("frame")
        self.prefilled_address.SetSelection(0)
        self.therapeute_address.SetMinSize((300, 200))
        self.address.SetMinSize((300, 200))

    def __do_layout(self):
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_32 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_3 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_sizer_4 = wx.FlexGridSizer(2, 2, 0, 0)
        grid_sizer_4.Add(self.therapeute, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.prefilled_address, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.therapeute_address, 0, wx.EXPAND, 0)
        grid_sizer_4.Add(self.address, 0, wx.EXPAND, 0)
        grid_sizer_4.AddGrowableRow(1)
        grid_sizer_4.AddGrowableCol(0)
        grid_sizer_4.AddGrowableCol(1)
        sizer_32.Add(grid_sizer_4, 2, wx.EXPAND, 0)
        label_7 = wx.StaticText(self.panel_4, wx.ID_ANY, "Motif")
        grid_sizer_3.Add(label_7, 0, 0, 0)
        label_8 = wx.StaticText(self.panel_4, wx.ID_ANY, "Montant")
        grid_sizer_3.Add(label_8, 0, 0, 0)
        grid_sizer_3.Add(self.reason, 0, wx.EXPAND, 0)
        grid_sizer_3.Add(self.amount, 0, wx.EXPAND, 0)
        grid_sizer_3.AddGrowableCol(0)
        sizer_32.Add(grid_sizer_3, 0, wx.EXPAND, 0)
        label_6 = wx.StaticText(self.panel_4, wx.ID_ANY, "Remarques")
        sizer_32.Add(label_6, 0, 0, 0)
        sizer_32.Add(self.remark, 1, wx.EXPAND, 0)
        sizer_32.Add(self.button_8, 0, wx.EXPAND, 0)
        self.panel_4.SetSizer(sizer_32)
        sizer_6.Add(self.panel_4, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_6)
        sizer_6.Fit(self)
        self.Layout()

    def on_select_therapeute(self, event):
        print("Event handler 'on_select_therapeute' not implemented!")
        event.Skip()

    def on_select_address(self, event):
        print("Event handler 'on_select_address' not implemented!")
        event.Skip()

    def on_generate(self, event):
        print("Event handler 'on_generate' not implemented!")
        event.Skip()


class ManageAddressesDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.addresses_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.LC_SINGLE_SEL)
        self.identifier = wx.TextCtrl(self, wx.ID_ANY, "")
        self.address = wx.TextCtrl(self, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.add_btn = wx.Button(self, wx.ID_ANY, "Ajouter")
        self.change_btn = wx.Button(self, wx.ID_ANY, "Modifier")
        self.remove_btn = wx.Button(self, wx.ID_ANY, "Supprimer")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect_address, self.addresses_list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select_address, self.addresses_list)
        self.Bind(wx.EVT_BUTTON, self.on_add_address, self.add_btn)
        self.Bind(wx.EVT_BUTTON, self.on_change_address, self.change_btn)
        self.Bind(wx.EVT_BUTTON, self.on_remove_address, self.remove_btn)

    def __set_properties(self):
        self.SetTitle("Gérer les adresses")
        self.addresses_list.AppendColumn("Identifiant", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.addresses_list.AppendColumn("Adresse", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.address.SetMinSize((300, 200))

    def __do_layout(self):
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_5 = wx.FlexGridSizer(2, 2, 0, 5)
        sizer_7.Add(self.addresses_list, 1, wx.EXPAND, 0)
        label_9 = wx.StaticText(self, wx.ID_ANY, "Identifiant")
        grid_sizer_5.Add(label_9, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_5.Add(self.identifier, 0, wx.EXPAND, 0)
        label_10 = wx.StaticText(self, wx.ID_ANY, "Adresse")
        grid_sizer_5.Add(label_10, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
        grid_sizer_5.Add(self.address, 0, wx.EXPAND, 0)
        grid_sizer_5.AddGrowableRow(1)
        grid_sizer_5.AddGrowableCol(1)
        sizer_7.Add(grid_sizer_5, 1, wx.EXPAND | wx.LEFT, 5)
        sizer_8.Add(self.add_btn, 1, wx.ALIGN_RIGHT, 0)
        sizer_8.Add(self.change_btn, 0, 0, 0)
        sizer_8.Add(self.remove_btn, 1, 0, 0)
        sizer_7.Add(sizer_8, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_7)
        sizer_7.Fit(self)
        sizer_7.SetSizeHints(self)
        self.Layout()

    def on_deselect_address(self, event):
        print("Event handler 'on_deselect_address' not implemented!")
        event.Skip()

    def on_select_address(self, event):
        print("Event handler 'on_select_address' not implemented!")
        event.Skip()

    def on_add_address(self, event):
        print("Event handler 'on_add_address' not implemented!")
        event.Skip()

    def on_change_address(self, event):
        print("Event handler 'on_change_address' not implemented!")
        event.Skip()

    def on_remove_address(self, event):
        print("Event handler 'on_remove_address' not implemented!")
        event.Skip()


class ManageConsultationsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.patient = wx.StaticText(self, wx.ID_ANY, "Sexe Prénom Nom\nNaissance: DD.MM.YYYY\nThérapeute: ???")
        self.consultations = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.delete_btn = wx.Button(self, wx.ID_ANY, "Supprimer cette consultation")
        self.show_btn = wx.Button(self, wx.ID_ANY, "Afficher la consultation")
        self.modify_btn = wx.Button(self, wx.ID_ANY, "Modifier la consultation")
        self.show_all_btn = wx.Button(self, wx.ID_ANY, "Afficher toutes les consultations")
        self.button_11 = wx.Button(self, wx.ID_ANY, "Annuler")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_delete_consultation, self.delete_btn)
        self.Bind(wx.EVT_BUTTON, self.on_show_consultation, self.show_btn)
        self.Bind(wx.EVT_BUTTON, self.on_modify_consultation, self.modify_btn)
        self.Bind(wx.EVT_BUTTON, self.on_show_all_consultations, self.show_all_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_11)

    def __set_properties(self):
        self.SetTitle("Rechercher une consultation de ???")
        self.consultations.AppendColumn("Date", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.consultations.AppendColumn("Thérapeute", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.consultations.AppendColumn("Motif", format=wx.LIST_FORMAT_LEFT, width=-1)

    def __do_layout(self):
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11.Add(self.patient, 0, wx.ALL | wx.EXPAND, 5)
        sizer_11.Add(self.consultations, 1, wx.EXPAND, 0)
        sizer_12.Add(self.delete_btn, 0, 0, 0)
        sizer_12.Add(self.show_btn, 0, 0, 0)
        sizer_12.Add(self.modify_btn, 0, 0, 0)
        sizer_12.Add(self.show_all_btn, 0, 0, 0)
        sizer_12.Add(self.button_11, 0, 0, 0)
        sizer_11.Add(sizer_12, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_11)
        sizer_11.Fit(self)
        self.Layout()

    def on_delete_consultation(self, event):
        print("Event handler 'on_delete_consultation' not implemented!")
        event.Skip()

    def on_show_consultation(self, event):
        print("Event handler 'on_show_consultation' not implemented!")
        event.Skip()

    def on_modify_consultation(self, event):
        print("Event handler 'on_modify_consultation' not implemented!")
        event.Skip()

    def on_show_all_consultations(self, event):
        print("Event handler 'on_show_all_consultations' not implemented!")
        event.Skip()

    def on_cancel(self, event):
        print("Event handler 'on_cancel' not implemented!")
        event.Skip()


class PatientDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        self.female = wx.RadioButton(self.panel_1, wx.ID_ANY, "F", style=wx.RB_GROUP)
        self.male = wx.RadioButton(self.panel_1, wx.ID_ANY, "M")
        self.patient_id = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_READONLY)
        self.lastname = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.therapeute = wx.Choice(self.panel_1, wx.ID_ANY, choices=[])
        self.firstname = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.birthdate = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.opening_date = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.fixed_phone = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.important = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.mobile_phone = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.professional_phone = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.main_doctor = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.email = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.street = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.zip = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.city = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.canton = wx.Choice(self.panel_1, wx.ID_ANY, choices=CANTONS)
        self.other_doctors = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.complementary_insurance = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.profession = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.civil_status = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.sent_by = wx.TextCtrl(self.panel_1, wx.ID_ANY, "")
        self.remarks = wx.TextCtrl(self.panel_1, wx.ID_ANY, "", style=wx.TE_DONTWRAP | wx.TE_MULTILINE)
        self.new_consultation_btn = wx.Button(self.panel_1, wx.ID_ANY, "OK, ouvrir une nouvelle consultation")
        self.save_btn = wx.Button(self.panel_1, wx.ID_ANY, "Enregistrer et fermer")
        self.update_btn = wx.Button(self.panel_1, wx.ID_ANY, "Modifier")
        self.button_7 = wx.Button(self.panel_1, wx.ID_ANY, "Annuler")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_new_consultation, self.new_consultation_btn)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.save_btn)
        self.Bind(wx.EVT_BUTTON, self.on_update, self.update_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_7)

        self.tab_traversal = [
            self.lastname,
            self.firstname,
            self.birthdate,
            self.fixed_phone,
            self.mobile_phone,
            self.professional_phone,
            self.email,
            self.street,
            self.zip,
            self.city,
            self.complementary_insurance,
            self.profession,
            self.civil_status,
            self.sent_by,
            self.important,
            self.main_doctor,
            self.other_doctors,
            self.remarks,
        ]
        for widget in self.tab_traversal:
            self.Bind(wx.EVT_CHAR_HOOK, self.on_tab, widget)

    def on_tab(self, event):
        if event.KeyCode == wx.WXK_TAB:
            shift = -1 if event.ShiftDown() else 1
            next = (self.tab_traversal.index(event.EventObject) + shift) % len(self.tab_traversal)
            self.tab_traversal[next].SetFocus()
        else:
            event.Skip()

    def __set_properties(self):
        self.SetTitle("Ficher patient")
        self.patient_id.Enable(False)

    def __do_layout(self):
        sizer_13 = wx.BoxSizer(wx.VERTICAL)
        sizer_21 = wx.BoxSizer(wx.VERTICAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_7 = wx.GridBagSizer(4, 5)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.HORIZONTAL)
        self.sex_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Sexe")
        grid_sizer_7.Add(self.sex_label, (0, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_15.Add(self.female, 1, wx.EXPAND, 0)
        sizer_15.Add(self.male, 1, wx.EXPAND, 0)
        grid_sizer_7.Add(sizer_15, (0, 1), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        label_26 = wx.StaticText(self.panel_1, wx.ID_ANY, "ID patient")
        grid_sizer_7.Add(label_26, (0, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.patient_id, (0, 3), (1, 1), wx.EXPAND, 0)
        self.lastname_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Nom")
        grid_sizer_7.Add(self.lastname_label, (1, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.lastname, (1, 1), (1, 1), wx.EXPAND, 0)
        self.therapeute_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Thérapeute")
        grid_sizer_7.Add(self.therapeute_label, (1, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.therapeute, (1, 3), (1, 1), wx.EXPAND, 0)
        self.firstname_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Prénom")
        grid_sizer_7.Add(self.firstname_label, (2, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.firstname, (2, 1), (1, 1), wx.EXPAND, 0)
        self.birthdate_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Naissance le")
        grid_sizer_7.Add(self.birthdate_label, (3, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.birthdate, (3, 1), (1, 1), wx.EXPAND, 0)
        self.opening_date_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Date d'ouverture")
        grid_sizer_7.Add(self.opening_date_label, (3, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.opening_date, (3, 3), (1, 1), wx.EXPAND, 0)
        label_17 = wx.StaticText(self.panel_1, wx.ID_ANY, "Téléphone fixe")
        grid_sizer_7.Add(label_17, (4, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_19.Add(self.fixed_phone, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(sizer_19, (4, 1), (1, 1), wx.EXPAND, 0)
        label_29 = wx.StaticText(self.panel_1, wx.ID_ANY, "Important")
        grid_sizer_7.Add(label_29, (4, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.important, (4, 3), (2, 1), wx.EXPAND, 0)
        label_18 = wx.StaticText(self.panel_1, wx.ID_ANY, "Portable")
        grid_sizer_7.Add(label_18, (5, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_16.Add(self.mobile_phone, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(sizer_16, (5, 1), (1, 1), wx.EXPAND, 0)
        label_19 = wx.StaticText(self.panel_1, wx.ID_ANY, "Téléphone professionnel")
        grid_sizer_7.Add(label_19, (6, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_17.Add(self.professional_phone, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(sizer_17, (6, 1), (1, 1), wx.EXPAND, 0)
        label_30 = wx.StaticText(self.panel_1, wx.ID_ANY, "Médecin traitant")
        grid_sizer_7.Add(label_30, (6, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.main_doctor, (6, 3), (2, 1), wx.EXPAND, 0)
        label_20 = wx.StaticText(self.panel_1, wx.ID_ANY, "Courriel")
        grid_sizer_7.Add(label_20, (7, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_18.Add(self.email, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(sizer_18, (7, 1), (1, 1), wx.EXPAND, 0)
        self.street_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Rue")
        grid_sizer_7.Add(self.street_label, (8, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        street_sizer = wx.BoxSizer(wx.HORIZONTAL)
        street_sizer.Add(self.street, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(street_sizer, (8, 1), (1, 1), wx.EXPAND, 0)
        label_32 = wx.StaticText(self.panel_1, wx.ID_ANY, "Autres médecins")
        grid_sizer_7.Add(label_32, (8, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.other_doctors, (8, 3), (2, 1), wx.EXPAND, 0)
        self.zip_city_label = wx.StaticText(self.panel_1, wx.ID_ANY, "NPA/Localité")
        grid_sizer_7.Add(self.zip_city_label, (9, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        zip_city_sizer = wx.BoxSizer(wx.HORIZONTAL)
        zip_city_sizer.Add(self.zip, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        zip_city_sizer.Add(self.city, 1, wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(zip_city_sizer, (9, 1), (1, 1), wx.EXPAND, 0)
        self.canton_label = wx.StaticText(self.panel_1, wx.ID_ANY, "Canton")
        grid_sizer_7.Add(self.canton_label, (10, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.canton, (10, 1), (1, 1), wx.EXPAND, 0)
        label_22 = wx.StaticText(self.panel_1, wx.ID_ANY, "Assurance complémentaire")
        grid_sizer_7.Add(label_22, (11, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.complementary_insurance, (11, 1), (1, 1), wx.EXPAND, 0)
        label_23 = wx.StaticText(self.panel_1, wx.ID_ANY, "Profession")
        grid_sizer_7.Add(label_23, (12, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.profession, (12, 1), (1, 1), wx.EXPAND, 0)
        label_33 = wx.StaticText(self.panel_1, wx.ID_ANY, "État civil")
        grid_sizer_7.Add(label_33, (12, 2), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.civil_status, (12, 3), (1, 1), wx.EXPAND, 0)
        label_24 = wx.StaticText(self.panel_1, wx.ID_ANY, "Envoyé par")
        grid_sizer_7.Add(label_24, (13, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.sent_by, (13, 1), (1, 1), wx.EXPAND, 0)
        label_25 = wx.StaticText(self.panel_1, wx.ID_ANY, "Remarques")
        grid_sizer_7.Add(label_25, (14, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer_7.Add(self.remarks, (14, 1), (2, 3), wx.EXPAND, 0)
        grid_sizer_7.AddGrowableRow(4)
        grid_sizer_7.AddGrowableRow(5)
        grid_sizer_7.AddGrowableRow(6)
        grid_sizer_7.AddGrowableRow(7)
        grid_sizer_7.AddGrowableRow(8)
        grid_sizer_7.AddGrowableRow(9)
        grid_sizer_7.AddGrowableRow(14)
        grid_sizer_7.AddGrowableRow(15)
        grid_sizer_7.AddGrowableCol(1)
        grid_sizer_7.AddGrowableCol(3)
        sizer_21.Add(grid_sizer_7, 1, wx.EXPAND, 0)
        sizer_14.Add(self.new_consultation_btn, 1, wx.EXPAND, 0)
        sizer_14.Add(self.save_btn, 1, wx.EXPAND, 0)
        sizer_14.Add(self.update_btn, 1, wx.EXPAND, 0)
        sizer_14.Add(self.button_7, 1, wx.EXPAND, 0)
        sizer_21.Add(sizer_14, 0, wx.ALIGN_CENTER, 0)
        self.panel_1.SetSizer(sizer_21)
        sizer_13.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_13)
        sizer_13.SetSizeHints(self)
        self.Layout()
        self.SetSize((962, 571))

    def on_new_consultation(self, event):
        print("Event handler 'on_new_consultation' not implemented!")
        event.Skip()

    def on_save(self, event):
        print("Event handler 'on_save' not implemented!")
        event.Skip()

    def on_update(self, event):
        print("Event handler 'on_update' not implemented!")
        event.Skip()

    def on_cancel(self, event):
        print("Event handler 'on_cancel' not implemented!")
        event.Skip()


class ManagePatientsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.panel_2 = wx.Panel(self, wx.ID_ANY)
        self.lastname = wx.TextCtrl(self.panel_2, wx.ID_ANY, "%", style=wx.TE_PROCESS_ENTER)
        self.firstname = wx.TextCtrl(self.panel_2, wx.ID_ANY, "%", style=wx.TE_PROCESS_ENTER)
        self.patients = wx.ListCtrl(self.panel_2, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        self.button_10 = wx.Button(self.panel_2, wx.ID_ANY, "Rechercher")
        self.show_patient_btn = wx.Button(self.panel_2, wx.ID_ANY, "Afficher la fiche patient")
        self.modify_patient_btn = wx.Button(self.panel_2, wx.ID_ANY, "Modifier la fiche patient")
        self.new_consultation_btn = wx.Button(self.panel_2, wx.ID_ANY, "Nouvelle consultation pour ce patient")
        self.show_consultations_btn = wx.Button(self.panel_2, wx.ID_ANY, "Afficher toutes les consultations")
        self.delete_patient_btn = wx.Button(self, wx.ID_ANY, "Supprimer le patient et toutes ses consultations")
        self.display_consultations_btn = wx.Button(self, wx.ID_ANY, "Afficher les consultations du patient")
        self.button_14 = wx.Button(self.panel_2, wx.ID_ANY, "Annuler")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_TEXT_ENTER, self.on_search_patient, self.lastname)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_search_patient, self.firstname)
        self.Bind(wx.EVT_BUTTON, self.on_search_patient, self.button_10)
        self.Bind(wx.EVT_BUTTON, self.on_show_patient, self.show_patient_btn)
        self.Bind(wx.EVT_BUTTON, self.on_modify_patient, self.modify_patient_btn)
        self.Bind(wx.EVT_BUTTON, self.on_new_consultation, self.new_consultation_btn)
        self.Bind(wx.EVT_BUTTON, self.on_show_consultations, self.show_consultations_btn)
        self.Bind(wx.EVT_BUTTON, self.on_delete_patient, self.delete_patient_btn)
        self.Bind(wx.EVT_BUTTON, self.on_display_consultations, self.display_consultations_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_14)

    def __set_properties(self):
        self.SetTitle("Recherche d'un patient")
        self.patients.AppendColumn("Sexe", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.patients.AppendColumn("Nom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.patients.AppendColumn("Prénom", format=wx.LIST_FORMAT_LEFT, width=-1)
        self.patients.SetMinSize((-1, 400))

    def __do_layout(self):
        sizer_20 = wx.BoxSizer(wx.VERTICAL)
        sizer_24 = wx.BoxSizer(wx.VERTICAL)
        sizer_23 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_8 = wx.FlexGridSizer(0, 2, 0, 5)
        label_31 = wx.StaticText(self.panel_2, wx.ID_ANY, "Nom")
        grid_sizer_8.Add(label_31, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        grid_sizer_8.Add(self.lastname, 0, wx.EXPAND, 0)
        label_34 = wx.StaticText(self.panel_2, wx.ID_ANY, "Prénom")
        grid_sizer_8.Add(label_34, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
        grid_sizer_8.Add(self.firstname, 0, wx.EXPAND, 0)
        grid_sizer_8.AddGrowableCol(1)
        sizer_24.Add(grid_sizer_8, 0, wx.EXPAND, 0)
        sizer_24.Add(self.patients, 1, wx.EXPAND, 0)
        sizer_23.Add(self.button_10, 0, 0, 0)
        sizer_23.Add(self.show_patient_btn, 0, 0, 0)
        sizer_23.Add(self.modify_patient_btn, 0, 0, 0)
        sizer_23.Add(self.new_consultation_btn, 0, 0, 0)
        sizer_23.Add(self.show_consultations_btn, 0, 0, 0)
        sizer_23.Add(self.delete_patient_btn, 0, 0, 0)
        sizer_23.Add(self.display_consultations_btn, 0, 0, 0)
        sizer_23.Add(self.button_14, 0, 0, 0)
        sizer_24.Add(sizer_23, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.panel_2.SetSizer(sizer_24)
        sizer_20.Add(self.panel_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_20)
        sizer_20.Fit(self)
        self.Layout()

    def on_search_patient(self, event):
        print("Event handler 'on_search_patient' not implemented!")
        event.Skip()

    def on_show_patient(self, event):
        print("Event handler 'on_show_patient' not implemented!")
        event.Skip()

    def on_modify_patient(self, event):
        print("Event handler 'on_modify_patient' not implemented!")
        event.Skip()

    def on_new_consultation(self, event):
        print("Event handler 'on_new_consultation' not implemented!")
        event.Skip()

    def on_show_consultations(self, event):
        print("Event handler 'on_show_consultations' not implemented!")
        event.Skip()

    def on_delete_patient(self, event):
        print("Event handler 'on_delete_patient' not implemented!")
        event.Skip()

    def on_display_consultations(self, event):
        print("Event handler 'on_display_consultations' not implemented!")
        event.Skip()

    def on_cancel(self, event):
        print("Event handler 'on_cancel' not implemented!")
        event.Skip()


class ConsultationDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.TAB_TRAVERSAL | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.panel_3 = wx.Panel(self, wx.ID_ANY)
        self.illness = wx.RadioButton(self.panel_3, wx.ID_ANY, "Maladie", style=wx.RB_GROUP)
        self.accident = wx.RadioButton(self.panel_3, wx.ID_ANY, "Accident")
        self.reason = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.general_state = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.paraclinic_exams = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.medical_background = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.family_history = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.thorax = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.abdomen = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.physical_exam = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.head_neck = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.upper_limbs = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.lower_limbs = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.other = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.important = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.diagnostic = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.treatment = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.remarks = wx.TextCtrl(self.panel_3, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.consultation_date = wx.TextCtrl(self.panel_3, wx.ID_ANY, "")
        self.therapeute = wx.Choice(self.panel_3, wx.ID_ANY, choices=[])
        self.save_and_bill_btn = wx.Button(self, wx.ID_ANY, "Enregistrer et facturer")  # Used for new consultation
        self.save_and_close_btn = wx.Button(self, wx.ID_ANY, "Enregistrer et fermer")  # Used when editing an old consultation
        self.view_bill_btn = wx.Button(self, wx.ID_ANY, "Voir la facture")  # Used when viewing an old consultation
        self.edit_bill_btn = wx.Button(self, wx.ID_ANY, "Editer la facture")  # Used when editing an old consultation
        self.cancel_btn = wx.Button(self, wx.ID_ANY, "Annuler")
        self.ok_btn = wx.Button(self, wx.ID_ANY, "OK")
        self.show_all_consultations_btn = wx.Button(self, wx.ID_ANY, "Toutes les consultations")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_save, self.save_and_bill_btn)
        self.Bind(wx.EVT_BUTTON, self.on_save, self.save_and_close_btn)
        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_btn)
        self.Bind(wx.EVT_BUTTON, self.on_view_or_edit_bill, self.view_bill_btn)
        self.Bind(wx.EVT_BUTTON, self.on_view_or_edit_bill, self.edit_bill_btn)
        self.Bind(wx.EVT_BUTTON, self.on_close, self.ok_btn)
        self.Bind(wx.EVT_BUTTON, self.on_show_all_consultations, self.show_all_consultations_btn)

        self.tab_traversal = [
            self.reason,
            self.general_state,
            self.medical_background,
            self.family_history,
            self.thorax,
            self.abdomen,
            self.head_neck,
            self.upper_limbs,
            self.lower_limbs,
            self.other,
            self.paraclinic_exams,
            self.physical_exam,
            self.important,
            self.diagnostic,
            self.treatment,
            self.remarks,
            self.consultation_date,
        ]
        for widget in self.tab_traversal:
            self.Bind(wx.EVT_CHAR_HOOK, self.on_tab, widget)

    def on_tab(self, event):
        if event.KeyCode == wx.WXK_TAB:
            shift = -1 if event.ShiftDown() else 1
            next = (self.tab_traversal.index(event.EventObject) + shift) % len(self.tab_traversal)
            self.tab_traversal[next].SetFocus()
        else:
            event.Skip()

    def __set_properties(self):
        self.SetTitle("Consultation du ??? - ???")
        self.reason.SetMinSize((300, 70))
        self.general_state.SetMinSize((300, 70))
        self.paraclinic_exams.SetMinSize((300, -1))
        self.medical_background.SetMinSize((300, 70))
        self.family_history.SetMinSize((300, 70))
        self.thorax.SetMinSize((300, 70))
        self.abdomen.SetMinSize((300, 70))
        self.physical_exam.SetMinSize((300, -1))
        self.head_neck.SetMinSize((300, 70))
        self.upper_limbs.SetMinSize((300, 70))
        self.lower_limbs.SetMinSize((300, 70))
        self.other.SetMinSize((300, 70))
        self.important.SetMinSize((300, 70))
        self.diagnostic.SetMinSize((300, 70))
        self.treatment.SetMinSize((300, 70))
        self.remarks.SetMinSize((300, 70))
        self.important.SetForegroundColour(wx.Colour(255, 0, 0))

    def __do_layout(self):
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        column_sizer = wx.BoxSizer(wx.HORIZONTAL)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        accident_sizer = wx.BoxSizer(wx.HORIZONTAL)
        accident_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Motif(s) de consultation"), 1, 0, 0)
        accident_sizer.Add(self.illness, 0, 0, 0)
        accident_sizer.Add(self.accident, 0, 0, 5)
        #accident_sizer.Add((20, 10), 0, 0, 0)
        left_sizer.Add(accident_sizer, 0, wx.EXPAND, 0)
        left_sizer.Add(self.reason, 1, wx.EXPAND, 0)
        left_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Antécédents personnels"), 0, wx.EXPAND, 0)
        left_sizer.Add(self.medical_background, 1, wx.EXPAND, 0)
        left_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Thorax"), 0, wx.EXPAND, 0)
        left_sizer.Add(self.thorax, 1, wx.EXPAND, 0)
        left_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Tête et cou"), 0, wx.EXPAND, 0)
        left_sizer.Add(self.head_neck, 1, wx.EXPAND, 0)
        left_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Membres inférieurs"), 0, wx.EXPAND, 0)
        left_sizer.Add(self.lower_limbs, 1, wx.EXPAND, 0)
        left_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Diagnostic pour la facture"), 0, wx.EXPAND, 0)
        left_sizer.Add(self.diagnostic, 1, wx.EXPAND, 0)
        left_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Date d'ouverture"), 0, wx.EXPAND, 0)
        left_sizer.Add(self.consultation_date, 0, wx.EXPAND, 0)
        column_sizer.Add(left_sizer, 0, wx.EXPAND, 0)

        central_sizer = wx.BoxSizer(wx.VERTICAL)
        central_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "État général"), 0, wx.EXPAND, 0)
        central_sizer.Add(self.general_state, 1, wx.EXPAND, 0)
        central_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Antécédents familiaux"), 0, wx.EXPAND, 0)
        central_sizer.Add(self.family_history, 1, wx.EXPAND, 0)
        central_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Abdomen"), 0, wx.EXPAND, 0)
        central_sizer.Add(self.abdomen, 1, wx.EXPAND, 0)
        central_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Membres supérieurs"), 0, wx.EXPAND, 0)
        central_sizer.Add(self.upper_limbs, 1, wx.EXPAND, 0)
        central_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Neuro, vascul, dermato, endocrino, lymph"), 0, wx.EXPAND, 0)
        central_sizer.Add(self.other, 1, wx.EXPAND, 0)
        treatment = wx.StaticText(self.panel_3, wx.ID_ANY, "Traitement")
        treatment.SetForegroundColour(wx.Colour(35, 142, 35))
        central_sizer.Add(treatment, 0, wx.EXPAND, 0)
        central_sizer.Add(self.treatment, 1, wx.EXPAND, 0)
        central_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Thérapeute"), 0, wx.EXPAND, 0)
        central_sizer.Add(self.therapeute, 0, wx.EXPAND, 0)
        column_sizer.Add(central_sizer, 1, wx.EXPAND, 0)

        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Examens paracliniques"), 0, wx.EXPAND, 0)
        right_sizer.Add(self.paraclinic_exams, 1, wx.EXPAND, 0)
        right_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Examen physique"), 0, wx.EXPAND, 0)
        right_sizer.Add(self.physical_exam, 1, wx.EXPAND, 0)
        important = wx.StaticText(self.panel_3, wx.ID_ANY, "Important")
        important.SetForegroundColour(wx.Colour(255, 0, 0))
        right_sizer.Add(important, 0, wx.EXPAND, 0)
        right_sizer.Add(self.important, 1, wx.EXPAND, 0)
        right_sizer.Add(wx.StaticText(self.panel_3, wx.ID_ANY, "Remarques"), 0, wx.EXPAND, 0)
        right_sizer.Add(self.remarks, 1, wx.EXPAND, 0)
        column_sizer.Add(right_sizer, 1, wx.EXPAND, 0)

        self.panel_3.SetSizer(column_sizer)
        top_sizer.Add(self.panel_3, 1, wx.EXPAND, 0)

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.save_and_bill_btn, 0, 0, 0)
        button_sizer.Add(self.save_and_close_btn, 0, 0, 0)
        button_sizer.Add(self.view_bill_btn, 0, 0, 0)
        button_sizer.Add(self.edit_bill_btn, 0, 0, 0)
        button_sizer.Add(self.cancel_btn, 0, 0, 0)
        button_sizer.Add(self.ok_btn, 0, 0, 0)
        button_sizer.Add(self.show_all_consultations_btn, 0, 0, 0)
        top_sizer.Add(button_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        self.SetSizer(top_sizer)
        top_sizer.Fit(self)
        top_sizer.SetSizeHints(self)
        self.Layout()
        self.SetSize((1024, -1))

    def on_save(self, event):
        print("Event handler 'on_save' not implemented!")
        event.Skip()

    def on_cancel(self, event):
        print("Event handler 'on_cancel' not implemented!")
        event.Skip()

    def on_close(self, event):
        print("Event handler 'on_close' not implemented!")
        event.Skip()

    def on_view_or_edit_bill(self, event):
        print("Event handler 'on_view_or_edit_bill' not implemented!")
        event.Skip()

    def on_show_all_consultations(self, event):
        print("Event handler 'on_show_all_consultations' not implemented!")
        event.Skip()


class AllConsultationsDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super().__init__(*args, **kwds)
        self.html = wx.html2.WebView.New(self, wx.ID_ANY)
        self.button_12 = wx.Button(self, wx.ID_ANY, "OK")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.on_cancel, self.button_12)

    def __set_properties(self):
        self.SetTitle("Consultations du patient")

    def __do_layout(self):
        sizer_27 = wx.BoxSizer(wx.VERTICAL)
        sizer_27.Add(self.html, 1, wx.EXPAND, 0)
        sizer_27.Add(self.button_12, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_27)
        sizer_27.Fit(self)
        sizer_27.SetSizeHints(self)
        self.Layout()
        self.SetSize((800, 600))

    def on_cancel(self, event):
        print("Event handler 'on_cancel' not implemented!")
        event.Skip()
