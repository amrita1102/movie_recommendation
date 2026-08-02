@echo off

echo Checking Kubernetes...
kubectl get nodes

echo.
echo Pods...
kubectl get pods

echo.
echo Starting Ingress Port Forward...
start cmd /k kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 8080:80

echo.
echo Application:
echo http://localhost:8080/docs
pause