import shlex

argString = "shh chat   -m  asdasdsdasa    user"
temp=shlex.split(argString)

if temp[0] =="shh" and temp[1] == "chat" and temp[3][0]=="@":
    print("correct command")