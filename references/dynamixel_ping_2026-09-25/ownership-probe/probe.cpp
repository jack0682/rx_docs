#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/prctl.h>
#include <sys/wait.h>
#include <unistd.h>
#include <signal.h>
#include <cstdio>
#include <cstring>
#include <string>
int main(int argc,char**argv){
#ifdef HELPER
 struct ucred c{};socklen_t n=sizeof(c);struct stat actual{},expected{};
 const pid_t parent=getppid();
 if(prctl(PR_SET_PDEATHSIG,SIGKILL)||getppid()!=parent || getsockopt(0,SOL_SOCKET,SO_PEERCRED,&c,&n)|| c.pid!=parent){puts("DXL_HOST_CHANNEL_REQUIRED");return 21;}
 auto path=std::string("/proc/")+std::to_string(parent)+"/exe";
 if(stat(path.c_str(),&actual)||stat("/probe/owner",&expected)||actual.st_dev!=expected.st_dev||actual.st_ino!=expected.st_ino){puts("DXL_HOST_EXECUTABLE_REQUIRED");return 22;}
 char x;if(read(0,&x,1)!=1||x!='P'){puts("DXL_HOST_REQUEST_REQUIRED");return 23;}
 puts("PROBE_OWNER_ACCEPTED_NO_SDK_OR_DEVICE");return 0;
#else
 int sockets[2];bool direct=argc>1 && std::string(argv[1])=="direct";
 if(!direct && socketpair(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0,sockets))return 90;
 auto pid=fork();if(pid==0){if(!direct){dup2(sockets[1],0);close(sockets[0]);close(sockets[1]);} execl("/probe/helper",argc>1 && std::string(argv[1])=="spoof"?"/probe/owner":"helper",nullptr);_exit(91);}
 if(!direct){close(sockets[1]);write(sockets[0],"P",1);close(sockets[0]);}int status;waitpid(pid,&status,0);return WIFEXITED(status)?WEXITSTATUS(status):92;
#endif
}
