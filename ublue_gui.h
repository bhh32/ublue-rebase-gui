#include <string>
#include <ncurses.h>

struct Config
{
    std::string dskEnv;
    std::string vers;
    bool isNvidia;
    bool doReboot;

    std::string dskEnvChoices[6];
    std::string versChoices[3];
    std::string nvidiaChoices[2];
    std::string rebootChoices[2];
};

class UblueGui
{
    private:
        int choiceLoop(WINDOW* menuwin, std::string* choices, int choicesSize);
        std::string command;
        int nvidiaChoiceSize = 2;
        int envChoiceSize = 6;
        int versChoiceSize = 3;
        int rebootChoiceSize = 2;

    public:
        Config init();
        void setEnv(WINDOW* menuwin, Config &config);
        void setVers(WINDOW* menuwin, Config &config);
        void setNvidia(WINDOW* menuwin, Config &config);
        void setReboot(WINDOW* menuwin, Config &config);
        void doRebase(Config config);
        void setKargs(bool isNvidia);        
};
