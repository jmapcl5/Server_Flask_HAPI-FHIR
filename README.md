# Server_Flask_HAPI-FHIR

Una aplicacion basica IoT web, el cual usa un MAX30102 para dar los datos SpO2 y Heart Rate de un paciente y se envian a traves de mqtt(mosquitto). La web esta construida en Flask con python , por otro lado tambien se usa HAPI FHIR para poder usar el estandar FHIR

Configuren el Servidor HAPI-FHIR : https://github.com/hapifhir/hapi-fhir-jpaserver-starter/tree/master. En esta aplicacion el servidor esta usando PostgreSql y jetty maven para iniciarlo, por lo que deberan configurar esto.

Por otro lado la web en flask se comunica con el servidor hapi fhir usando los verbos de hapi-fhir. La web es basica, toma los registros del paciente, despues se redirige a otro link donde se mostrara los datos obtenidos en el servidor hapi fhir, tambien se añadio una grafica en tiempo real del Heart Rate.

Si lo va usar, compreube las conexiones entre el servidor y la web, compruebe que los request llegen al serivodr y que este responda para asi obtener los datos.


