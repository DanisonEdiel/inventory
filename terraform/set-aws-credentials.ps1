# Script para configurar credenciales AWS
# Ejecutar este script antes de ejecutar terraform
# IMPORTANTE: Copia este archivo a set-aws-credentials.ps1 y reemplaza los valores con tus credenciales reales

# Reemplaza estos valores con tus credenciales reales
$AWS_ACCESS_KEY_ID = "ASIAT62RWUMGWICZGNHN"
$AWS_SECRET_ACCESS_KEY = "PXamQkf5yN21uebbRPM9sIQ6pqvBPp4gR2kxJuEm"
$AWS_SESSION_TOKEN = "IQoJb3JpZ2luX2VjEHwaCXVzLXdlc3QtMiJIMEYCIQCV1jb8Px1PQ1VlFs8ONYZ1YJK5s0FyhUhACwgRGtRwRQIhAP2Lh9OdW6XaonixbzBvcRaTQ3DCCQUkRTaau6qhZV+zKrwCCIX//////////wEQARoMMjcyMzY0OTA1MjI5IgwzlWNh7vLBUAQELkgqkAJxzVWcGNPJrgRkIPlNBVPfv3GsOVotJxX67zDJjMXeCw2MBzz6gIDdJ8GnJrYIpwMIhk6XWPMNkBi19TILUPy6XfQvBaKck+Sw405TFsBSdRLOkj9wSnk02lbkNpLd/FSvGuzuI1rOt2rY8OLV4HjQ4X0mPWjq/yxHLQ/oPP6vq5KYkGHRJZ8g34LJi7A8ejKEtu8UsBGJyYbR7kSb02z/x3cvTTlEGiJUHPwe81nM33vUYvDEexp4JhLXF35s1lv6vs/I1eewFyZEPSfXOhzaQC59iYWa527QGYYWBLFPFVBl3Qj2HgYI1xgkfh8FMERZYj+frMLSyPRf4jSc37XG2N57f6aoQpbQQpSLvxBUoDCRpLLDBjqcAV8DLWYkc5PX9D2JzR3v8CkJB4I3burC0BMJ9UDDn/6Y2crglV2ywI5rZqMsczX4YkOtCzfnH3pAUN4n5DHjdEi+alFHXEOZQ4MbuPSwPUxirPK0fMJcBk2Jz/a0BqcuslrUkBbe5uI28ivgankCdbZf+0vd3w6z9nrJyFluo9zvkXO9CsP8OKIZpNXxA1xm67yhF5PQzh2WTrRftg=="

# Configurar variables de entorno
$env:AWS_ACCESS_KEY_ID = $AWS_ACCESS_KEY_ID
$env:AWS_SECRET_ACCESS_KEY = $AWS_SECRET_ACCESS_KEY

if ($AWS_SESSION_TOKEN -ne "") {
    $env:AWS_SESSION_TOKEN = $AWS_SESSION_TOKEN
}

