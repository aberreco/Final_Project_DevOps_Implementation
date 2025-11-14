# Final\_Project\_DevOps\_Implementation

Proyecto Final del curso DevOps IronHack





Lista de Alumnos del equipo:

* Guillermo Castelao Martinez
* Iria Martinez Cuervo
* Brais Gallego Castro
* Andres Berreco Martinez
* Jose Carlos Cano Domenech
* Roque Valledor Mera





Resumen del proyecto y objetivos:

Calculadora Flask con endpoint para cada operación. Integración con base de datos.





Descripción del workflow CI/CD

Fase1: añadir comprobación linter y verificar métrica de linter

Fase2: comprobación de test de unidad y verificación de cobertura de test (75% de test)

Fase3: desplegamos a dev

Fase4: hacer pruebas de integración y verificar la cobertura de test (100%)

Fase5: lanzar SonarQube y analizar calidad

Fase6: contanerizar la aplicación y la base de datos

Fase7: desplegar a staging

Fase8: si todo ok desplegar a prod

Fase9: añadir Grafana para métricas exportadas de la aplicación

Fase10: añadir métricas de performance de host





Herramientas y tecnologías usadas:

GitHub actions con self-hosted (runners)

SonarQube

Grafana

Docker Compose





Instrucciones de setup/ejecución o despliegue:

`minikube start --driver=docker --cpus=4 --memory=4096`





Pantallazos de los dashboards de monitoring y el porque de las métricas elegidas:

