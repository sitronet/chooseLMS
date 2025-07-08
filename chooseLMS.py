#!/usr/bin/python3

__author__ = "Noël"
__copyright__ = "2025 june"
__credits__ = ["Noël", "c'est moi"]
__license__ = "GPL 2.0 , 3.0"
__version__ = "0.0.a"
__maintainer__ = "??"
__email__ = "rondrach  (at)  gmail"
__status__ = "Alpha release"


from kivy.app import App
from kivy.lang import Builder
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
import xml.etree.ElementTree as ET
from requests import get

import hashlib
import requests
import urllib.request
import platform
import os
import subprocess

from kivy.uix.boxlayout import BoxLayout

Builder.load_string('''
<SelectArch>:
    #padding: '30dp'
    #spacing: '20dp'
    
        
    BoxLayout:
        id: box_fenetre
        orientation: 'vertical'    
        #cols: 2
        padding: 20
        spacing: 20
        size_hint: 1,1
        
        Label:
            id: label_information
            canvas.before:
                Color:
                    rgba: 0.5, 0.5, 0.5, 1
                Line:    # --- adds a border --- #
                    width: 1
                    rectangle: self.x, self.y, self.width, self.height
            size_hint: (1, 0.4)
            text: 'programm to choose LMS version between DEV, STABLE, LATEST'
        
        Button:
            id: show_arch
            size_hint: (1, 0.5)
            text: "Show architecture"
            on_release: root.show_architecture()
        Button:
            id: label_systeme
            size_hint: (1, 0.5)
            text: ''
        Button:
            id: label_architecture
            size_hint: (1, 0.5)
            text: ''
        Button:
            id: label_program_installed
            size_hint: (1, 0.5)
            text: ''
            #on_release: root.popup_lms.open
        
        Spinner:
            id: choix_LMS
            size_hint: (1, 0.5)
            disabled: True
            text: 'Select LMS Version to install'
            values: ("DEV", "STABLE" , "LATEST") 
            on_text: root.choix_LMS_clicked(choix_LMS.text)
            
        GridLayout:
            #orientation: 'horizontal'
            cols: 2
            size_hint: (1,0.5)
            Button:
                id: confirmer
                size_hint: (1,0.5)
                text: 'Confirmer' 
                disabled: True          
                #on_release: root.confirmer
            Button:
                id: cancel_arch
                size_hint: (1, 0.5)
                text: 'Cancel (Exit)'
                disabled: True
                on_release: root.cancel_arch()
                
        Label:
            id: label_info
            canvas.before:
                Color:
                    rgba: 0.5, 0.5, 0.5, 1
                Line:    # --- adds a border --- #
                    width: 1
                    rectangle: self.x, self.y, self.width, self.height
            text: 'processing...'
        ProgressBar:
            id: progressionbar    
        
''')

class SelectArch(BoxLayout):
    '''
    pour mémoire :
    dev_repo_url     = "https://lyrion.org/lms-server-repository/dev.xml"
    stable_repo_url  = "https://lyrion.org/lms-server-repository/stable.xml"
    latest_repo_url  = "https://lyrion.org/lms-server-repository/latest.xml"
    '''

    def show_current_lms(self):

        service = None
        state = None
        preset = None

        try:
            resultat = subprocess.run(['sudo', 'systemctl', '--no-pager', 'list-unit-files'],
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

        if 'lyrionmusicserver' in resultat.stdout:
            lignes = resultat.stdout.splitlines()
            print('lyrionmusicserver trouvé ')
            trouve = True
            for ligne in lignes:
                if 'lyrion' in ligne:
                    service, state, preset  = ligne.split()
                    self.ids.label_program_installed.text = service + ' installed and state  : ' + state
                    self.program, extension = service.split('.')
                    print(self.program)
        else:
            trouve = False
            print('lyrionmusicserver non trouvé')

            ''' inserer ici pour logitechmediaserver la même chose'''

            if 'logitechmediaserver' in resultat.stdout:
                lignes = resultat.stdout.splitlines()
                print('logitechmediaserver trouvé ')
                trouve = True
                for ligne in lignes:
                    if 'logitech' in ligne:
                        service, state, preset = ligne.split()
                        self.ids.label_program_installed.text = service + ' installed and state  : ' + state
                        self.program, extension = service.split('.')
                        print(self.program)

        if trouve:
            try:
                resultat2 = subprocess.run([ 'dpkg', '-s', self.program],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise
            lignes = resultat2.stdout.splitlines()
            for ligne in lignes:
                if 'Version' in ligne:
                    residu, self.version_installed = ligne.split(':')
            self.version_installed = self.version_installed.strip()
            self.ids.label_program_installed.text = service + ' installed  - Version : ' + self.version_installed + ' state : ' + state
            name= 'LMS'
            box_popup = BoxLayout(orientation='vertical')
            box_popup.add_widget(Label(text=resultat2.stdout))
            content = box_popup
            popup_lms = Popup(content=content, title=name)
            b = Button(text="close me", on_press=popup_lms.dismiss,size_hint=(0.2,0.1),pos_hint={'x': 0.4, 'y': 0})
            box_popup.add_widget(b)
            self.ids.label_program_installed.bind(on_press=popup_lms.open)
        else:
            self.ids.label_program_installed.text = 'No version server installed '
            self.version_installed = 'none'



    def show_architecture(self):
        self.show_current_lms()
        platformarch = platform.uname()
        machine = platformarch.machine
        systeme = platformarch.system
        self.ids.label_systeme.text = systeme + '  ' + machine
        self.ids.label_architecture.text =  machine

        if systeme != 'Linux' and systeme != 'linux' :
            self.ids.label_information.text = \
                "this programm doesn't run on your system - click Cancel Button to exit"
            self.ids.cancel_arch.disabled = False
            return

        '''
        Comments here to test the programm for normal user
        in use it is uncommented 
        '''

        uid = os.getuid()
        if uid != 0 :
            self.ids.label_information.text =\
                "This programm must be run as root. As user, use 'sudo' - click Cancel Button to exit"
            self.ids.cancel_arch.disabled = False
            return

        '''end comments here'''

        bouton_confirmer = self.ids.confirmer
        self.ids.confirmer.disabled = False
        self.ids.cancel_arch.disabled = False
        bouton_confirmer.bind(on_press=self.confirmer_arch)
        # Detect the architecture of the distribution
        if machine in 'x86_64':
            arch = "debamd64"

        elif machine in  'i386' or machine in 'i686':
            arch = "debi386"

        elif machine in 'armv7l':
            arch = "debarm"

        elif machine in 'aarch64':
            arch = "debarm"

        else:
            arch = "Unknown architecture : " + machine
            self.ids.label_information.text = arch + ' - Click Cancel Button'
        self.ids.label_architecture.text = arch

        name = 'Arch'
        texte_format = 'node : ' + platformarch.node + '\n' \
                       + 'system : ' + platformarch.system + '\n' \
                       + 'machine : ' +  platformarch.machine + '\n'  \
                       +  'release : ' + platformarch.release + '\n ' \
                       + 'version : ' + platformarch.version + '\n'
        box_popup = BoxLayout(orientation='vertical')
        box_popup.add_widget(Label(text=texte_format))

        content = box_popup
        popup_arch = Popup(content=content, title=name)
        b = Button(text="close me", on_press=popup_arch.dismiss,size_hint=(0.2,0.1),pos_hint={'x': 0.4, 'y': 0})
        box_popup.add_widget(b)
        self.ids.label_systeme.bind(on_press=popup_arch.open)
        self.ids.label_architecture.bind(on_press=popup_arch.open)

    def confirmer_installation(self,instance):
        # donc nous avons le systeme , l'arch, la version souhaitée
        # ne reste plus qu'à l'installer
        self.ids.choix_LMS.disabled = True
        choix = self.ids.choix_LMS.text
        if choix == 'DEV':
            repo_url = "https://lyrion.org/lms-server-repository/dev.xml"
        elif choix == 'STABLE':
            repo_url = "https://lyrion.org/lms-server-repository/stable.xml"
        elif choix == 'LATEST':
            repo_url = "https://lyrion.org/lms-server-repository/latest.xml"

        repo_url = repo_url.strip()

        arch = self.ids.label_architecture.text
        response = get(repo_url)
        #parse response.content to get the url of the arch
        root = ET.fromstring(response.content)

        for type_tag in root.findall(arch):
            download_url = type_tag.get('url')
            version = type_tag.get('version')
            revision = type_tag.get('revision')
            size = type_tag.get('size')
            md5 = type_tag.get('md5')
            print (md5)

        # comparaison avec la version installée
        if version == self.version_installed:
            print("inutile c'est la même version")
            self.ids.label_info.text = ' ! version installed is the version to install ! Choose an other one '
            self.ids.cancel_arch.disabled = False
            self.ids.choix_LMS.disabled = False
            return
        liste_fname = download_url.split('/')
        fname = '/tmp/' + liste_fname[-1]
        taille, unite = size.split(' ')
        size = int(taille) * 1024 * 1024
        self.ids.label_info.text = '\nfichier à télécharger : ' + download_url + '\n'
        self.ids.progressionbar.value = 0
        self.ids.progressionbar.max = size
        r = requests.get(download_url, stream=True)
        with open(fname, 'wb') as f:
            total_length = size
            for chunk in r.iter_content(chunk_size=1024):
                self.ids.progressionbar.value += 1024
                self.ids.label_info.text += '.'
                if chunk:
                    f.write(chunk)
                    f.flush()
        # vérification  md5 du fichier téléchargé
        if md5checksum(fname) == md5:
            print(' download md5 concorde')
            self.ids.label_info.text = 'vérification md5 : OK'
        # comparaison avec la version installée
        print(version)
        print(self.version_installed)
        if version == self.version_installed:
            print ("inutile c'est la même version")
            self.ids.label_info.text = ' ! version installed is the version to install ! '
            self.ids.cancel_arch.disabled = False
        else:
            # remove old version : apt-get remove -y "$CURRENT_SERVICE"
            self.ids.label_info.text = "ok, j'y vais pour installer " + version

            if self.version_installed != 'none':
                try:
                    resultat_desinstallation = subprocess.run([ 'apt', 'remove', '-y', self.program],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                except Exception as err:
                    print(f"Unexpected {err=}, {type(err)=}")
                    raise
                if resultat_desinstallation.stderr:
                    self.ids.label_info.text += '\n désinstallation : ' + resultat_desinstallation.stderr
            # Install the new package : dpkg - i paquet
            try:
                resultat_installation = subprocess.run([ 'dpkg', '-i', fname],
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            except Exception as err:
                print(f"Unexpected {err=}, {type(err)=}")
                raise
            if resultat_installation.stderr:
                self.ids.label_info.text += '\n installation : ' + resultat_installation.stderr

            self.ids.confirmer.disabled = True
            # delete the /tmp/file
            os.remove(fname)

    def confirmer_arch(self, *args):
        self.ids.show_arch.disabled = True
        self.ids.label_systeme.disabled = True
        self.ids.label_architecture.disabled = True
        self.ids.label_program_installed.disabled = True
        #self.ids.cancel_arch.disabled = True
        #self.ids.confirmer.disabled = True
        self.ids.choix_LMS.disabled = False
        choix = self.ids.choix_LMS.text
        stack_sup = self.ids.box_fenetre
        return

    def cancel_arch(self):
        self.ids.cancel_arch.text = 'ok, exit ...'
        self.ids.confirmer.disabled = True
        print('Action canceled by user on Arch')
        exit(0)

    def choix_LMS_clicked(self, choix):
        choix = choix.strip()
        self.ids.confirmer.text= 'Confirmer le choix'
        self.ids.confirmer.unbind(on_release=self.confirmer_arch())
        self.ids.confirmer.unbind(on_release=self.confirmer_arch)
        self.ids.confirmer.bind(on_release=self.confirmer_installation)
        self.ids.confirmer.disabled = False
        self.confirmer = self.confirmer_installation
        return choix

    def _create_popup(self, title, content):
        return Popup(
            title=title,
            content=Label(text=content),
            size_hint=(.8, 1),
            auto_dismiss=True
        )

# methodes utiles

def download(url, file_name):
    # open in binary mode
    with open(file_name, "wb") as file:
        # get request
        response = get(url)
        # write to file
        file.write(response.content)

def md5checksum(fname):
    md5 = hashlib.md5()
    # handle content in binary form
    f = open(fname, "rb")
    while chunk := f.read(4096):
        md5.update(chunk)
    return md5.hexdigest()



class ChooseApp(App):

    def build(self):
        return SelectArch()

if __name__ == "__main__":
    ChooseApp().run()
