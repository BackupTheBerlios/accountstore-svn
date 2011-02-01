# -*- coding: utf-8 -*-
import gedit
import gtk
import os.path
import re
import account_engine as ae

from gettext import gettext as _

ACCOUNT_FILE = '/usr/lib/gedit-2/plugins/account_store.txt'

# Menu-definition
ui_str = """<ui>
    <menubar name="MenuBar">
        <menu name="ToolsMenu" action="Tools">
            <placeholder name="ToolsOps_2">
                <menuitem name="AccountStore" action="AccountStore"/>
            </placeholder>
        </menu>
    </menubar>
</ui>"""
        
# Plugin-class per window-instance:        
class AccountStoreWindowHelper:
    """ This class registers a menu-item and action to show the accelerator
        dialog """
    def __init__(self, window):
        print "ASWH.__init__()"
        self.win = window
        manager = self.win.get_ui_manager()

        self.action_group = gtk.ActionGroup("EditShortcutsPluginActions")
        self.action_group.add_actions([("AccountStore", None, _("_Account Store"), None, 
            _("Load the account store"), self.show_account_dialog)])
        
        manager.insert_action_group(self.action_group, -1)
        self.ui_id = manager.add_ui_from_string(ui_str)
        
        self.dlg = None # None => new dialog can be made. See show_account_dialog()
        
    def deactivate(self):
        print "ASWH.deactivate()"
        # nedenstående er pastet fra Examplepy
        self.remove_menu()
        self.win = None
        self.dlg = None
        self.action_group = None
    
    def remove_menu(self):
        # Get the GtkUIManager
        manager = self.win.get_ui_manager()
        # Remove the ui
        manager.remove_ui(self.ui_id)
        # Remove the action group
        manager.remove_action_group(self.action_group)
        # Make sure the manager updates
        manager.ensure_update()   
               
    def update_ui(self):
        print "ASWH.update_ui()"
        
    def show_account_dialog(self, action):
        print "ASWH.show_account_dialog()"
        # Quick'n dirty singleton pattern...
        if self.dlg is None:
            self.dlg = AccountStoreDialog(self)
        
class AccountStoreDialog:
    ''' 
    This class implements the account store dialog 
    TODO Make an input field to authenticate the user when he wants to see the
    data!
    '''
    def __init__(self, windowhelper):
        print 'ASD.__init__()'
        self.winhelp = windowhelper
        self.dlg = gtk.Dialog('Account Store', self.winhelp.win, gtk.DIALOG_DESTROY_WITH_PARENT) 
        self.dlg.set_border_width(10)
        self.liststore = gtk.ListStore(str, str, str)
        
        #################### Populate ListStore ######################
        act_mgr = ae.AccountManager()  # ae: account_engine module
        act_mgr.load() # accounts i AccountManager er blevet load'et med sine accounts
        for act in act_mgr.accounts:
            self.liststore.append(act_mgr.csv2list(str(act)))
        # Now liststore is populated
    
        ###################### Setup TreeView ########################
        # TreeViewColumns
        self.tvcol1 = gtk.TreeViewColumn('Account')
        self.tvcol2 = gtk.TreeViewColumn('User Name')
        self.tvcol2.set_property('visible', False)  # Starts invisible, authentication needed
        self.tvcol3 = gtk.TreeViewColumn('Password')
        self.tvcol3.set_property('visible', False)
        
        # Create the TreeView using liststore
        self.treeview = gtk.TreeView(self.liststore)
        self.treeview.append_column(self.tvcol1)
        self.treeview.append_column(self.tvcol2)
        self.treeview.append_column(self.tvcol3)

        # Create CellRendererText to render the data
        self.cell = gtk.CellRendererText()

        # Add the cellrenderer to the tvcols (they share the same renderer) 
        # and allow it to expand
        self.tvcol1.pack_start(self.cell, True)
        self.tvcol2.pack_start(self.cell, True)
        self.tvcol3.pack_start(self.cell, True)

        # Set the cell "text" attribute and retrieve text from the respective 
        # columns in liststore
        self.tvcol1.add_attribute(self.cell, 'text', 0)
        self.tvcol2.add_attribute(self.cell, 'text', 1)
        self.tvcol3.add_attribute(self.cell, 'text', 2)

        self.treeview.set_search_column(0)  # Make it searchable
        
        #################### Additional Widgets ######################
        self.dlg.get_content_area().pack_start(self.treeview)  # Connect TreeView and dialog
        self.but_show_codes = gtk.Button('Show Codes')
        self.but_show_codes.connect('clicked', self.toggle_show_codes)
        
        self.but_new_act = gtk.Button('New Account')
        self.but_new_act.connect('clicked', self.new_account)
        
        self.dlg.get_action_area().pack_start(self.but_show_codes)
        self.dlg.get_action_area().pack_start(self.but_new_act)
        self.dlg.set_position(gtk.WIN_POS_CENTER)
        
        # Make the dialog emit a 'response' signal when its close button is activated
        self.dlg.connect('response', self.dialog_response)
        self.dlg.show_all()
        
    def dialog_response(self, dialog, response):
        print 'ASD.dialog_response()' 
        if response == gtk.RESPONSE_DELETE_EVENT:
            self.winhelp.dlg = None  # Sæt None så ny dialog kan laves    
            self.dlg = None # TODO Tror er unødv?
            
    def toggle_show_codes(self, button):
        print 'ASD.toggle_show_codes()' 
        cols_visible = self.tvcol2.get_property('visible') and \
            	       self.tvcol2.get_property('visible')
        button.set_label('Show Codes' if cols_visible else 'Hide Codes') # 3-operator
        self.tvcol2.set_property('visible', not cols_visible)
        self.tvcol3.set_property('visible', not cols_visible)
        
    def new_account(self, button):
        self.liststore.append(('', '', ''))  # Empty row
        idx_last_row = len(self.liststore) - 1
        last_row = self.liststore[idx_last_row]
        button.set_label('Accept')
        # if input OK run => chk_act_info() (TODO) 
        # button.set_lable('New Account')
    
    def toogle_cols_editable(self):
        pass
        
################################################################################

class AccountStore(gedit.Plugin):
    # Called by gedit as the first method 
    def __init__(self):
        print '\nAS.__init__()'
        gedit.Plugin.__init__(self)
        self._instances = dict()
        

    # Called by gedit when window have been made
    def activate(self, window):
        print 'AS.activate()'
        self._instances[window] = AccountStoreWindowHelper(window)
        
    # Called by gedit when window closes
    def deactivate(self, window):
        print 'AS.deactivate()***'
        self._instances[window].deactivate()
        del self._instances[window]
        
    def update_ui(self, window):
        print 'AS.update_ui()'
        self._instances[window].update_ui()
        


