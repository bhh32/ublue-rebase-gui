#!/bin/python3
import sys
import subprocess
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(400, 150)
        self.set_title("uBlue Rebase Tool")

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.env_options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.vers_options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.other_options_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

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

        self.thirty_seven_chk = Gtk.CheckButton(label="37")
        self.thirty_eight_chk = Gtk.CheckButton(label="38")
        self.latest_chk = Gtk.CheckButton(label="Latest")

        self.thirty_eight_chk.set_group(self.thirty_seven_chk)
        self.latest_chk.set_group(self.thirty_seven_chk)

        self.is_nvidia_chk = Gtk.CheckButton(label="Install Nvidia")
        self.do_reboot_chk = Gtk.CheckButton(label="Auto-reboot")

        self.status_label = Gtk.Label()

        self.main_box.append(self.env_options_box)
        self.main_box.append(self.vers_options_box)
        self.main_box.append(self.other_options_box)
        self.main_box.append(self.button_box)
        self.main_box.append(self.status_box)

        self.env_options_box.append(self.bluefin_chk)
        self.env_options_box.append(self.gnome_chk)
        self.env_options_box.append(self.lxqt_chk)
        self.env_options_box.append(self.mate_chk)
        self.env_options_box.append(self.xfce_chk)
        self.env_options_box.append(self.kde_chk)

        self.vers_options_box.append(self.thirty_seven_chk)
        self.vers_options_box.append(self.thirty_eight_chk)
        self.vers_options_box.append(self.latest_chk)

        self.other_options_box.append(self.is_nvidia_chk)
        self.other_options_box.append(self.do_reboot_chk)

        self.rebase_btn = Gtk.Button(label="Rebase")
        self.rebase_btn.connect('clicked', self.run_command)

        self.button_box.append(self.rebase_btn)

        self.status_box.append(self.status_label)

        self.set_child(self.main_box)

    def run_command(self, button):
        self.status_label.set_text("Rebasing... Please Wait...")
        vers = self.get_vers()
        running_cmd = subprocess.Popen(["rpm-ostree", "rebase", "--experimental", "ostree-unverified-registry:ghcr.io/ublue-os/" + self.get_env() + ":" + vers], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
        running_ret_code = running_cmd.returncode

        if running_ret_code == 0:
            if self.is_nvidia_chk.get_active():
                set_kargs = subprocess.Popen(["rpm-ostree", "kargs", "--delete-if-exists=rd.driver.blacklist=nouveau", "--delete-if-exists=modprobe.blacklist.nouvea", "--delete-if-exists=nvidia-drm.modeset=1"])
                set_kargs.communicate()
                set_kargs_ret_code = set_kargs.wait()

                if set_kargs_ret_code == 0 and self.do_reboot_chk.get_active():
                    subprocess.Popen(["systemctl", "reboot"])
                else:
                    self.status_label.set_text("Reboot the system for the changes to take effect!")

            elif self.do_reboot_chk.get_active():
                subprocess.Popen(["systemctl", "reboot"])
            else:
                self.status_label.set_text("Reboot the system for the changes to take effect!")

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
        vers_output = ""
        if self.thirty_seven_chk.get_active():
            vers_output = "37"
        elif self.thirty_eight_chk.get_active():
            vers_output = "38"
        else:
            vers_output = "latest"

        return vers_output


class RebaseApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()

app = RebaseApp(application_id="com.github.bhh32.ublue_rebase_gui")
app.run(sys.argv)
