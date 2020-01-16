#! /usr/bin/env python
# -*- coding: utf-8 -*-

import gi
from gi.repository import GLib
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
import signal
import commands
import sys
import os.path
from os import path
import subprocess
from subprocess import check_output

# -TAG mostra o valor
# --TAG remove a tag
# -TAG=valor atribui


UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileOpen' />
      <menuitem action='FileClose' />
      <menuitem action='FileSave' />
      <separator />
      <menuitem action='FileQuit' />
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='FileOpen' />
    <toolitem action='FileClose' />
    <toolitem action='FileSave' />
  </toolbar>
</ui>
"""

class botoes:
    x = 1

def set_list(l, i, v):
      try:
          l[i] = v
      except IndexError:
          for _ in range(i-len(l)+1):
              l.append(None)
          l[i] = v


class MyMain(Gtk.Window):

    def __init__(self, root):
        super(MyMain, self).__init__()
        self.app = root
        self.set_title(self.app.name)

        ## pegar uma imagem qq de python ##Open
        out = commands.getoutput("locate python | grep '/usr/share' | grep '.png' ")
        out = out.split('\n')
        print out[0];
        self.set_default_icon_from_file(out[0]);
        ##

        self.set_border_width(10)

        action_group = Gtk.ActionGroup("my_actions")
        self.add_file_menu_actions(action_group)
        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        self.bigGrid = Gtk.Grid()
        self.bigGrid.show();
        self.add(self.bigGrid)

        menubar = uimanager.get_widget("/MenuBar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)

        toolbar = uimanager.get_widget("/ToolBar")
        box.pack_start(toolbar, False, False, 0)

        self.bigGrid.attach(box,0,0,1,1)
        self.show_all()


        if(arquivoPdf):
            self.abrirArquivo(arquivoPdf)
            self.titulo.set_text("Ferramenta Exif Tool Python")

    def createGrid(self):
        if(hasattr(self,'grid')):
            self.grid.destroy()
            #del self.grid
            print('limpar grid')
        if(hasattr(self,'itensDaLista')):
            del self.itensDaLista
            
        self.grid = Gtk.Grid()
        self.grid.show();
        self.bigGrid.attach(self.grid,0,1,1,1)

        self.titulo = Gtk.Label("Ferramenta ExifTool Python")
        self.titulo.show()
        self.grid.attach(self.titulo,0,0,2,1)

    def abrirArquivo(self,filename):
        response = True
        if(hasattr(self,'itensDaLista')):
            if(self.verifyUnsavedChanges()):
                response = self.confirmDialog("Unsaved changes","Unsaved changes will be lost 4 ever. U Sure?");
            
        if(response):        
            self.createGrid();
            
            #print("Abrir arquivo",filename);
            self.titulo.set_text("Ferramenta Exif Tool Python")
            #raw data
            self.arrExifList = self.getExifInfoFromFile(filename)
            #here goes organized data {tag,string,status,ta}
            self.itensDaLista = {}

            for line in self.arrExifList:
                if(line):
                    # print('line=> ',line)
                    ## procurar grupo pelo indicador ']'
                    charNumGroup = line.find(']')    
                    group = line[1:charNumGroup]
                    
                    ## verificar se o grupo nao é de sistema
                    if not (group in ['ExifTool','System','File']):
                        
                        ## se no existe, add na lista
                        if not group in self.itensDaLista:
                            self.itensDaLista[group] = []
                            
                        obj = {}
                    
                        charNum = line.find(':')
                        sub1 = line[charNumGroup+1:charNum]
                        sub1 = sub1.strip()
                        
                        obj['tag'] = sub1;
                        
                        sub2 = line[charNum+1:]
                        sub2 = sub2.strip()
                        
                        obj['string'] = sub2
                        
                        obj['status'] = 'original'
                        
                        #print(obj)                    
                        
                        self.itensDaLista[group].append(obj)
                    #end if grupo
                #end if line
            #end for
            
            print(self.itensDaLista[group])
            
            self.createScreen()
        #end if response
    #end def abrirArquivo

    def getExifInfoFromFile(self,theFile):
        #print(theFile)
        if(theFile):
            exiflist = check_output([ 'exiftool', '-G',  '-a','-u', theFile ])
            arrExifList = exiflist.split("\n")
            #print(arrExifList)
            arquivoPdf = theFile;
            return arrExifList
        return ''

    def createScreen(self):
        #TODO organize groups inside colapsable boxes        
        lineNum = 1;
        
        for group in self.itensDaLista:
            itemIndex = -1;
            for obj in self.itensDaLista[group]:
                print(obj)
                
                itemIndex = itemIndex + 1
                lineNum = lineNum + 1
                
                sub1 = obj['tag']
                sub2 = obj['string']
                
                lbl = Gtk.Label(sub1)
                lbl.show()
                self.grid.attach(lbl,0,lineNum,1,1)
                
                ta = Gtk.Entry()
                ta.set_text(sub2)
                ta.show()
                self.grid.attach(ta,1,lineNum,1,1)
                
                imgClear = Gtk.Image()
                imgClear.set_from_stock(Gtk.STOCK_CLEAR, Gtk.IconSize.BUTTON)
                
                btnDelete = Gtk.Button()
                btnDelete.set_image(imgClear)
                btnDelete.show()
                btnDelete.connect("clicked", self.clearTa,ta)
                self.grid.attach(btnDelete,2,lineNum,1,1)
                
                self.itensDaLista[group][itemIndex]['ta'] = ta
                
            # end for group
        #end for of all groups
                
        #ativar botao fechar
        self.botoes.btnClose.set_sensitive(True)
        #ativr botao salvar
        self.botoes.btnSave.set_sensitive(True)
            
    def clearTa(self,button,ta):
        ta.set_text('')

    def add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("FileMenu", "Arquivo", None, None)
        action_group.add_action(action_filemenu)

        #tive que criar uma estrutura dummy para conter os objetos
        self.botoes = botoes();

        action_fileopenmenu = Gtk.Action("FileOpen", None, None, Gtk.STOCK_OPEN)
        action_fileopenmenu.connect("activate", self.on_menu_file_open)
        action_group.add_action(action_fileopenmenu)
        self.botoes.btnOpen = action_fileopenmenu        
        
        action_fileopenmenu = Gtk.Action("FileClose", None, None, Gtk.STOCK_CLOSE)
        action_fileopenmenu.connect("activate", self.on_menu_file_close)
        action_fileopenmenu.set_sensitive(False)
        action_group.add_action(action_fileopenmenu)
        self.botoes.btnClose = action_fileopenmenu        

        action_filesavemenu = Gtk.Action("FileSave", None, None, Gtk.STOCK_SAVE)
        action_filesavemenu.connect("activate", self.on_menu_file_save)
        action_filesavemenu.set_sensitive(False)
        action_group.add_action(action_filesavemenu)
        self.botoes.btnSave = action_fileopenmenu        

        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)
        action_filequit.connect("activate", self.on_menu_file_quit)
        action_group.add_action(action_filequit)
        self.botoes.btnQuit = action_fileopenmenu        

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def on_menu_file_open(self, widget):
        print("A File|Open menu item was selected.")
        fn = Gtk.FileChooserDialog(title="Abrir Arquivo",
                                   #action=Gtk.FILECHOOSER_ACTION_OPEN,
                                   buttons=(Gtk.STOCK_CANCEL,Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN,Gtk.ResponseType.ACCEPT)
                                   )
        _filter = Gtk.FileFilter()
        _filter.set_name("PDF Files")
        _filter.add_pattern("*.pdf")
        fn.add_filter(_filter)
        _filter = Gtk.FileFilter()
        _filter.set_name("All Files")
        _filter.add_pattern("*")
        fn.add_filter(_filter)
        fn.show()

        resp = fn.run()
        if resp == Gtk.ResponseType.ACCEPT:
            filename = fn.get_filename()
            if(filename):
                self.abrirArquivo(filename)

        fn.destroy()
    #end def on_menu_file_open

    def on_menu_file_close(self, widget):
        response = True
        if(self.verifyUnsavedChanges()):
            response = self.confirmDialog("Unsaved changes","Unsaved changes on file will be lost 4 ever. U Sure?");
            
        if(response):
            self.createGrid();
            arquivoPdf = ''
            #desativar botao fechar
            self.botoes.btnClose.set_sensitive(False)
            #desativar botao salvar
            self.botoes.btnSave.set_sensitive(False)
        #end if
    #end def on_menu_file_close

    def verifyUnsavedChanges(self):
        for group in self.itensDaLista:
            itemIndex = -1;
            for obj in self.itensDaLista[group]:
                if obj['string'] != obj['ta'].get_text():
                    return True
                #end if
            #end for group
        #end for groups
        return False 
    #end def verifyUnsavedChanges

    def on_menu_file_save(self, widget):
        print("A File|Save menu item was selected.")
        #TODO not implemented yet
        response = self.confirmDialog(self,"Overwrite?","Save changes on file?");
        
        if(response):
            print "Ok saving tho"
        else:
            print "ok, not saving then"
        
        print "NOP! I Wont Save, because reasons..."

    def confirmDialog(self,title,text):
        dialog = Gtk.Dialog(title, self, 
                            None, (
                                Gtk.STOCK_YES, Gtk.ResponseType.YES, 
                                Gtk.STOCK_NO, Gtk.ResponseType.NO, 
                                )
                            )
        dialog.get_content_area().add(Gtk.Label(text))
        dialog.get_content_area().set_size_request(300, 100)
        dialog.show_all()
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            return True
        return False
    #end def confirmDialog

    def on_menu_file_quit(self, widget):
        Gtk.main_quit()
        
    def cb_show(self):
        self.show()



class MyApp(Gtk.Application):
    def __init__(self, app_name):
        super(MyApp, self).__init__()
        self.name = app_name

        self.main_win = MyMain(self)
        self.main_win.connect('delete-event', lambda w, e: Gtk.main_quit() or True)
        self.main_win.cb_show();

        s = Gdk.Screen.get_default()

        l = (s.get_width() - 50) / 2;
        t = (s.get_height() - 50) /2;
        self.main_win.move(l,t);



    def run(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        Gtk.main()

if __name__ == "__main__":
    
    
    out = commands.getstatusoutput('pwd')
    pwd = out[1]

    arquivoPdf = '';

    if(len(sys.argv) > 1):
        if(sys.argv[1]):
            arquivoPdf = pwd+'/'+sys.argv[1]    
    
    app = MyApp('ExifTool')
    app.run()
