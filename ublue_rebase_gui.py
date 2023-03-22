#!/bin/python3
from multiprocessing import Pool
import signal

import os
import sys
import subprocess
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(600, 250)
        self.set_title("uBlue Rebase Tool")

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.env_options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.other_options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        self.bluefin_chk = Gtk.CheckButton(label="Bluefin")
        self.gnome_chk = Gtk.CheckButton(label="Gnome")
        self.lxqt_chk = Gtk.CheckButton(label="LXQT")
        self.mate_chk = Gtk.CheckButton(label="Mate")
        self.xfce_chk = Gtk.CheckButton(label="XFCE")
        self.kde_chk = Gtk.CheckButton(label="KDE")

        self.gnome_chk.set_group(self.bluefin_chk)
        self.lxqt_chk.set_group(self.bluefin_chk)
        self.mate_chk.set_group(self.bluefin_chk)
        self.xfce_chk.set_group(self.bluefin_chk)
        self.kde_chk.set_group(self.bluefin_chk)

        self.is_nvidia_chk = Gtk.CheckButton(label="Install Nvidia")
        self.do_reboot_chk = Gtk.CheckButton(label="Auto-reboot")

        self.main_box.append(self.env_options_box)
        self.main_box.append(self.other_options_box)
        self.main_box.append(self.button_box)

        self.env_options_box.append(self.bluefin_chk)
        self.env_options_box.append(self.gnome_chk)
        self.env_options_box.append(self.lxqt_chk)
        self.env_options_box.append(self.mate_chk)
        self.env_options_box.append(self.xfce_chk)
        self.env_options_box.append(self.kde_chk)

        self.other_options_box.append(self.is_nvidia_chk)
        self.other_options_box.append(self.do_reboot_chk)

        self.rebase_btn = Gtk.Button(label="Rebase")
        self.rebase_btn.connect('clicked', self.running)

        self.button_box.append(self.rebase_btn)

        self.set_child(self.main_box)

    def run_command(self):
        running_cmd = subprocess.Popen(["rpm-ostree", "rebase", "--experimental", "ostree-unverified-registry:ghcr.io/ublue-os/" + self.get_env() + ":latest"], stdin=subprocess.PIPE)
        running_ret_code = running_cmd.returncode

        if running_ret_code == 0:
            if self.is_nvidia_chk.get_active():
                set_kargs = subprocess.Popen(["rpm-ostree", "kargs", "--delete-if-exists=rd.driver.blacklist=nouveau", "--delete-if-exists=modprobe.blacklist.nouvea", "--delete-if-exists=nvidia-drm.modeset=1"])
                set_kargs.communicate()
                set_kargs_ret_code = set_kargs.wait()

                if set_kargs_ret_code == 0 and self.do_reboot_chk.get_active():
                    subprocess.Popen(["systemctl", "reboot"])
                else:
                    print("Reboot the system for the changes to take effect!")
            
            elif self.do_reboot_chk.get_active():
                subprocess.Popen(["systemctl", "reboot"])
            else:
                print("Reboot the system for the changes to take effect!")

    def running(self):
        run_process = Pool(target=self.run_command, args=())
        if run_process.exitcode == -signal.SIGTERM:
            print("The process is complete!")

    def build_command(self):
        env = self.get_env()
        vers = self.get_vers()

        return "ostree-unverified-registry:ghcr.io/ublue-os/" + env + ":" + bytes.decode(vers, 'utf-8')

        
    def get_env(self):
        env = ""
        if self.bluefin_chk.get_active():
            env = "bluefin"
        elif self.gnome_chk.get_active():
            env = "silverblue"
        elif self.lxqt_chk.get_active():
            env = "lxqt"
        elif self.mate_chk.get_active():
            env = "mate"
        elif self.xfce_chk.get_active():
            env = "vauxite"
        elif self.xfce_chk.get_active():
            env = "kinoite"

        if self.is_nvidia_chk.get_active():
            env = env + "-nvidia"
        elif not self.is_nvidia_chk.get_active() and self.bluefin_chk.get_active():
            env = env + "-main"
        
        return env
    
    def get_vers(self):
        vers_cat_process = subprocess.Popen(["cat", "/etc/fedora-release"], stdout=subprocess.PIPE)
        vers_cut_process = subprocess.Popen(["cut", "-d ", "-f3"], stdin=vers_cat_process.stdout, stdout=subprocess.PIPE)
        vers_cut_output, vers_cut_errors = vers_cut_process.communicate()
        vers_cut_process.wait()

        return vers_cut_output


class RebaseApp(Adw.Application):
    def __init__(self, **kwargs):
        Gtk.init_check()
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

os.system("export DISPLAY=':0'")
app = RebaseApp(application_id="com.github.bhh32.ublue_rebase_gui")
app.run(sys.argv)
