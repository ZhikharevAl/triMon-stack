FROM amazoncorretto:17

WORKDIR /opt/app

COPY Hello-1.0-SNAPSHOT.jar .
COPY jmx_prometheus_javaagent-0.20.0.jar .
COPY config.yaml .

EXPOSE 8888

CMD ["java", "-javaagent:jmx_prometheus_javaagent-0.20.0.jar=8888:config.yaml", "-jar", "Hello-1.0-SNAPSHOT.jar"]

