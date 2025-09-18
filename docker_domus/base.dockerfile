ARG img

FROM $img

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV OMPI_ALLOW_RUN_AS_ROOT=1
ENV OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1



#COPY ./requirements.txt /tmp/requirements.txt


#RUN apt update && apt upgrade
RUN apt update
RUN apt install -y wget gnupg2 software-properties-common apt-transport-https ca-certificates 


#https://gitlab.winehq.org/wine/wine/-/wikis/Debian-Ubuntu
RUN dpkg --add-architecture i386
#RUN mkdir -pm755 /etc/apt/keyrings
#RUN wget -O - https://dl.winehq.org/wine-builds/winehq.key | gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key -
#RUN wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/focal/winehq-focal.sources

#RUN apt update
#RUN apt install -y --install-recommends winehq-stable
RUN apt install -y wine
RUN apt install -y xvfb winbind libvulkan1
RUN export WINEPREFIX=/wineprefix
RUN wineboot --init

#Copia do Domus para o container
ADD ./Domus /Domus/
ADD ./Python313 /Python313/

#Cópia do Python para o container

#Cópia do projeto 

WORKDIR /Domus/Win64/Release/
