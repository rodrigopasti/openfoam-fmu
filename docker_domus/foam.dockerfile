ARG img
FROM $img

#COPY ./requirements.txt /tmp/requirements.txt

#RUN /root/miniconda/bin/pip install -r /tmp/requirements.txt

COPY ./1_buildings_with_only_fluid_domain_25_10_2024 /1_buildings_with_only_fluid_domain_25_10_2024
WORKDIR /1_buildings_with_only_fluid_domain_25_10_2024/

# Comando a ser executado
#CMD /root/miniconda/bin/python3 ./somma.py -app:${app} -schema:${schema} -app_id:${app_id} -state:${state} -user:${user} -${place}
