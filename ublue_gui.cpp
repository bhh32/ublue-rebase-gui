#include <ncurses.h>
#include <string>
#include "ublue_gui.h"

using namespace std;


Config UblueGui::init()
{
    Config config;
    config.dskEnv = "silverblue";
    config.vers = "latest";
    config.isNvidia = false;
    config.doReboot = false;

    config.dskEnvChoices[0] ="Bluefin";
    config.dskEnvChoices[1] = "Gnome";
    config.dskEnvChoices[2] = "KDE";
    config.dskEnvChoices[3] = "Mate";
    config.dskEnvChoices[4] = "LXQT";
    config.dskEnvChoices[5] = "XFCE";

    config.versChoices[0] = "37";
    config.versChoices[1] = "38";
    config.versChoices[2] = "Latest";

    config.nvidiaChoices[0] = "I don't have Nvidia";
    config.nvidiaChoices[1] = "I have Nvidia";

    config.rebootChoices[0] = "Reboot Automatically";
    config.rebootChoices[1] = "DON'T Reboot Automatically";

    return config;
}

int UblueGui::choiceLoop(WINDOW* menuwin, string* choices, int choicesSize)
{
    int highlight = 0;
    int choice;

    while(true)
    {
        for(int i = 0; i < choicesSize; ++i)
        {
            if(i == highlight)
            {
                wattron(menuwin, A_REVERSE);
            }

            mvwprintw(menuwin, i + 1, 1, choices[i].c_str());
            wattroff(menuwin, A_REVERSE);
        }

        choice = wgetch(menuwin);

        switch(choice)
        {
            case KEY_UP:
                highlight--;
                if(highlight < 0)
                {
                    highlight = 0;
                }
                break;
            case KEY_DOWN:
                highlight++;
                if(highlight > choicesSize)
                {
                    highlight = choicesSize;
                }
                break;
            default:
                break;
        }

        if(choice == 10)
            break;
    }

    return highlight;
}

void UblueGui::setNvidia(WINDOW* menuwin, Config &config)
{
    int selected = choiceLoop(menuwin, config.nvidiaChoices, nvidiaChoiceSize);

    switch(selected)
    {
        case 0:
            config.isNvidia = false;
            break;
        case 1:
            config.isNvidia = true;
            break;
        default:
            config.isNvidia = false;
            break;
    }
}

void UblueGui::setEnv(WINDOW* menuwin, Config &config)
{
    int selected = choiceLoop(menuwin, config.dskEnvChoices, envChoiceSize);
    
    printw("selected: %d", selected);

    switch(selected)
    {
        case 0:
            config.dskEnv= "bluefin";
            break;
        case 1:
            config.dskEnv = "silverblue";
            break;
        case 2:
            config.dskEnv = "kinoite";
            break;
        case 3:
            config.dskEnv = "mate";
            break;
        case 4:
            config.dskEnv = "lxqt";
            break;
        case 5:
            config.dskEnv = "vauxite";
            break;
        default:
            config.dskEnv = "silverblue";
            break;
    }

    if(!config.isNvidia)
    {
        if(config.dskEnv != "bluefin")
            config.dskEnv = config.dskEnv + "-main";
    }
    else
        config.dskEnv = config.dskEnv + "-nvidia";
}

void UblueGui::setVers(WINDOW* menuwin, Config &config)
{
    int selected = choiceLoop(menuwin, config.versChoices, versChoiceSize);

    switch(selected)
    {
        case 0:
            config.vers = "37";
            break;
        case 1:
            config.vers = "38";
            break;
        case 2:
        default:
            config.vers = "latest";
            break;
    }
}

void UblueGui::setReboot(WINDOW* menuwin, Config &config)
{
    int selected = choiceLoop(menuwin, config.rebootChoices, rebootChoiceSize);

    switch(selected)
    {
        case 0:
            config.doReboot = true;
            break;
        case 1:
        default:
            config.doReboot = false;
            break;
    }
}

void UblueGui::doRebase(Config config)
{
    string command = "rpm-ostree rebase --experimental ostree-unverified-registry:ghcr.io/ublue-os/";
    command.append(config.dskEnv);
    command.append(":");
    command.append(config.vers);
    const char* cmd = command.c_str();
    system(cmd);
    setKargs(config.isNvidia);
    clear();
    if(config.doReboot)
        system("systemctl reboot");
    else
        mvprintw(2, 0, "Manually reboot your computer with systemctl reboot for changes to take effect!");
}

void UblueGui::setKargs(bool isNvidia)
{
    if(isNvidia)
    {
        clear();
        printw("Setting kargs...");
        system("rpm-ostree kargs --delete-if-exists=rd.driver.blacklist=nouveau --delete-if-exists=modprobe.blacklist=nouveau --delete-if-exists=nvidia-drm.modeset=1");
        system("rpm-ostree kargs --append=rd.driver.blacklist=nouveau --append=modprobe.blacklist=nouveau --append=nvidia-drm.modeset=1");
    }
}

// Main Function
int main(int argc, char **argv)
{
    UblueGui gui;
    Config config = gui.init();

    // initialize the screen
    initscr();
    cbreak(); // CTRL+C to exit out of the ncurses program (defaults)
    noecho(); // Don't show user input

    // Set screen size
    int yMax, xMax;
    getmaxyx(stdscr, yMax, xMax);

    // Create window
    WINDOW* menuwin = newwin(8, xMax - 12, yMax - 52, 5);
    box(menuwin, 0, 0);
    refresh();
    wrefresh(menuwin);

    keypad(menuwin, true); // Makes it so arrow keys can be used

    gui.setNvidia(menuwin, config);
    clear();
    refresh();
    wrefresh(menuwin);

    gui.setEnv(menuwin, config);
    clear();
    refresh();
    wrefresh(menuwin);

    gui.setVers(menuwin, config);
    clear();
    refresh();
    wrefresh(menuwin);

    gui.setReboot(menuwin, config);
    clear();
    refresh();
    wrefresh(menuwin);
    
    gui.doRebase(config);
    
    getch();

    // ends the screen
    endwin();

    return 0;
}
