#!/bin/bash
# =====================================================
# 🚀 Script de arranque DevOps local
# Levanta Minikube, ArgoCD y Dashboard de Kubernetes
# ----------------------------------------------------------
# Descripción:
#   - Inicia Minikube y verifica el clúster Kubernetes.
#   - Despliega (si es necesario) ArgoCD en su namespace.
#   - Realiza port-forward y login automático al CLI de ArgoCD.
#   - Abre el dashboard de Kubernetes en el navegador.
#
# Uso:
#   bash start-devops-env.sh
#
# Requisitos:
#   - Docker instalado y en ejecución
#   - Minikube y kubectl configurados
#   - argocd CLI instalado
#
# Autor: Roqval22
# =====================================================

set -e  # Detener ejecución ante cualquier error

# --- CONFIGURACIÓN BÁSICA ---
ARGOCD_NAMESPACE="argocd"
ARGOCD_PORT=8080  # Puedes cambiarlo si lo necesitas
DASHBOARD_PORT=8001

echo "==========================================="
echo " 🧩 Iniciando entorno DevOps local"
echo "==========================================="

# --- 1️⃣ Iniciar Minikube ---
if minikube status | grep -q "host: Running"; then
  echo "✅ Minikube ya está en ejecución"
else
  echo "🚀 Iniciando Minikube con Docker..."
  minikube start --driver=docker
fi

# --- 2️⃣ Verificar nodos ---
kubectl get nodes

# --- 3️⃣ Crear namespace de ArgoCD si no existe ---
if kubectl get ns | grep -q "$ARGOCD_NAMESPACE"; then
  echo "✅ Namespace '$ARGOCD_NAMESPACE' ya existe"
else
  echo "📦 Creando namespace '$ARGOCD_NAMESPACE'..."
  kubectl create namespace $ARGOCD_NAMESPACE
fi

# --- 4️⃣ Instalar ArgoCD si no está desplegado ---
if kubectl get pods -n $ARGOCD_NAMESPACE | grep -q "argocd-server"; then
  echo "✅ ArgoCD ya está instalado"
else
  echo "⬇️ Instalando ArgoCD..."
  kubectl apply -n $ARGOCD_NAMESPACE -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
  echo "⌛ Esperando a que los pods de ArgoCD estén en ejecución..."
  kubectl wait --for=condition=Ready pods --all -n $ARGOCD_NAMESPACE --timeout=180s
fi

# --- 5️⃣ Mostrar estado de ArgoCD ---
echo "📊 Estado actual de ArgoCD:"
kubectl get pods -n $ARGOCD_NAMESPACE

# --- 6️⃣ Exponer ArgoCD (port-forward) ---
echo "🌐 Iniciando port-forward en https://localhost:$ARGOCD_PORT ..."
# Abre una nueva terminal que mantiene vivo el port-forward
start "" bash -c "kubectl port-forward svc/argocd-server -n $ARGOCD_NAMESPACE $ARGOCD_PORT:443"
ARGO_PID=$!
sleep 5  # Esperar a que se abra el puerto

# --- 7️⃣ Obtener contraseña del usuario admin ---
echo ""
echo "🔑 Obteniendo credenciales de acceso a ArgoCD..."
if kubectl get secret argocd-initial-admin-secret -n $ARGOCD_NAMESPACE &>/dev/null; then
  PASSWORD=$(kubectl -n $ARGOCD_NAMESPACE get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
  echo "Usuario: admin"
  echo "Contraseña: $PASSWORD"
else
  echo "⚠️  No se encontró el secreto de contraseña (posiblemente ya fue eliminado o ArgoCD reseteado)"
fi

# --- 8️⃣ Limpiar sesión anterior y login automático ---
echo ""
echo "🧹 Limpiando sesión previa del CLI de ArgoCD..."
if [ -f ~/.argocd/config ]; then
  rm -rf ~/.argocd/config
  echo "🗑️  Archivo ~/.argocd/config eliminado."
fi

echo "🔐 Realizando login automático en ArgoCD CLI..."
argocd login localhost:$ARGOCD_PORT --username admin --password $PASSWORD --insecure || {
  echo "⚠️  Error al hacer login automático. Revisa el port-forward o credenciales."
}

# --- 9️⃣ Mostrar usuario actual ---
argocd account get-user-info || true

# --- 🔟 Abrir dashboard de Kubernetes ---
echo ""
echo "📈 Abriendo dashboard de Kubernetes en el navegador..."
minikube dashboard --port $DASHBOARD_PORT &

echo ""
echo "✅ Entorno DevOps iniciado correctamente."
echo "👉 ArgoCD disponible en: https://localhost:$ARGOCD_PORT"
echo "👉 Dashboard en: http://localhost:$DASHBOARD_PORT"
echo "Usa Ctrl+C para detener los port-forward y dashboard cuando termines."
echo ""
