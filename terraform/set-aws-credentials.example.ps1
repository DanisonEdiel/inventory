# Script para configurar credenciales AWS
# Ejecutar este script antes de ejecutar terraform
# IMPORTANTE: Copia este archivo a set-aws-credentials.ps1 y reemplaza los valores con tus credenciales reales

# Reemplaza estos valores con tus credenciales reales
$AWS_ACCESS_KEY_ID = "TU_ACCESS_KEY_ID"
$AWS_SECRET_ACCESS_KEY = "TU_SECRET_ACCESS_KEY"
$AWS_SESSION_TOKEN = ""  # Dejar vacío si no usas credenciales temporales

# Configurar variables de entorno
$env:AWS_ACCESS_KEY_ID = $AWS_ACCESS_KEY_ID
$env:AWS_SECRET_ACCESS_KEY = $AWS_SECRET_ACCESS_KEY

if ($AWS_SESSION_TOKEN -ne "") {
    $env:AWS_SESSION_TOKEN = $AWS_SESSION_TOKEN
}

